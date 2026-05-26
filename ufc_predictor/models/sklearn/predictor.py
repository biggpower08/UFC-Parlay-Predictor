"""Sklearn logistic regression predictor."""

import json
from functools import lru_cache

import numpy as np

from ufc_predictor.config import settings
from ufc_predictor.features.matchup_builder import (
    FEATURE_NAMES,
    build_matchup_features,
    build_training_dataset,
    features_to_vector,
)
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def model_available() -> bool:
    if not settings.LATEST_MODEL_PKL.is_file():
        return False
    try:
        import joblib  # noqa: F401
        import sklearn  # noqa: F401
    except ImportError:
        return False
    return True


@lru_cache(maxsize=1)
def load_model():
    if not model_available():
        return None
    try:
        import joblib

        return joblib.load(settings.LATEST_MODEL_PKL)
    except ImportError:
        logger.warning("joblib/sklearn unavailable; skipping sklearn model")
        return None


def save_model(bundle: dict):
    import joblib

    settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, settings.LATEST_MODEL_PKL)
    model_available.cache_clear()
    load_model.cache_clear()
    logger.info("Model saved to %s", settings.LATEST_MODEL_PKL)


def train_pipeline(X, y):
    try:
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, classification_report
        from sklearn.model_selection import train_test_split
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc:
        raise RuntimeError("scikit-learn is required to train the sklearn predictor") from exc

    if len(y) < 50:
        raise RuntimeError("Too few samples to train.")

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=settings.RETRAIN_TEST_SIZE,
        random_state=settings.RETRAIN_RANDOM_STATE,
        stratify=y,
    )
    pipeline = Pipeline(
        [
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=2000, class_weight="balanced")),
        ]
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    metrics = {
        "n_samples": int(len(y)),
        "test_accuracy": round(float(acc), 4),
        "classification_report": classification_report(y_test, y_pred, output_dict=True),
    }
    return pipeline, metrics


def save_weights(pipeline, metrics=None):
    clf = pipeline.named_steps["clf"]
    coefs = clf.coef_[0].tolist()
    weights = {
        "feature_names": FEATURE_NAMES,
        "coefficients": dict(zip(FEATURE_NAMES, coefs)),
        "intercept": float(clf.intercept_[0]),
    }
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with open(settings.MODEL_WEIGHTS_JSON, "w", encoding="utf-8") as f:
        json.dump(weights, f, indent=2)
    if metrics is not None:
        with open(settings.MODEL_METRICS_JSON, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=2)
    load_model_weights.cache_clear()


def predict_matchup(fighter_a_row, fighter_b_row, note_flags_a=None, note_flags_b=None):
    bundle = load_model()
    if bundle is None:
        return None
    pipeline = bundle["pipeline"]
    feats = build_matchup_features(fighter_a_row, fighter_b_row, note_flags_a, note_flags_b)
    expected_features = bundle.get("feature_names") or FEATURE_NAMES
    missing_features = [name for name in expected_features if name not in feats]
    extra_features = [name for name in feats if name not in expected_features]
    X = features_to_vector(feats).reshape(1, -1)
    prob_a = float(pipeline.predict_proba(X)[0][1])
    return {
        "prob_a_wins": prob_a,
        "prob_b_wins": 1 - prob_a,
        "features": feats,
        "diagnostics": {
            "expected_features": list(expected_features),
            "actual_features": list(FEATURE_NAMES),
            "missing_features": missing_features,
            "extra_features": extra_features,
            "elo_features_present": all(name in feats for name in ("delta_elo", "elo_expected_a")),
            "delta_elo": feats.get("delta_elo"),
            "elo_expected_a": feats.get("elo_expected_a"),
        },
    }


def explain_top_features(prediction, top_n=3):
    if prediction is None:
        return []
    w = load_model_weights()
    if not w:
        return []
    coefs = w.get("coefficients", {})
    feats = prediction["features"]
    contribs = [(n, feats[n] * coefs[n]) for n in FEATURE_NAMES if n in coefs]
    contribs.sort(key=lambda x: abs(x[1]), reverse=True)
    return contribs[:top_n]


@lru_cache(maxsize=1)
def load_model_weights() -> dict:
    if not settings.MODEL_WEIGHTS_JSON.is_file():
        return {}
    with open(settings.MODEL_WEIGHTS_JSON, encoding="utf-8") as f:
        return json.load(f)
