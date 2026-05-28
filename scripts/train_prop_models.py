"""Train dedicated prop models from cached fight history.

Official/primary source target:
- UFCStats event and bout result pages for winner, method, round, and time.

Current local training source:
- ufc_predictor/data/raw/fights.csv, normalized from historical fight results.

Models trained now:
- finish_model
- goes_distance_model
- method_model
- round_model

Models intentionally left untrained until richer data exists:
- strike_volume_model
- takedown_control_model
- odds_edge_model
"""

from __future__ import annotations

import json
from collections import Counter

import numpy as np

from ufc_predictor.config import settings
from ufc_predictor.data_sources.fighter_stats import load_fighters_cached
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.data_sources.rankings import division_point_dominance, p4p_rankings
from ufc_predictor.features.matchup_builder import FEATURE_NAMES
from ufc_predictor.models.elo.elo_engine import build_elo_fight_counts, compute_elo_ratings
from ufc_predictor.models.props.feature_builder import build_prop_datasets
from ufc_predictor.models.props.predictor import load_prop_model
from ufc_predictor.utils.helpers import normalize_name

MODEL_VERSION = "prop_logreg_v1"


def train_prop_models() -> dict:
    fights = load_fights()
    master = build_training_master(fights)
    datasets = build_prop_datasets(fights, master)
    settings.PROP_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    metrics = {}
    for model_name, payload in datasets.items():
        X, y = payload["X"], payload["y"]
        artifact, model_metrics = train_softmax_model(model_name, X, y)
        path = settings.PROP_MODELS_DIR / f"{model_name}.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(artifact, handle, indent=2)
        load_prop_model.cache_clear()
        metrics[model_name] = model_metrics

    metrics["not_trained"] = {
        "strike_volume_model": "Needs per-fight significant strike totals.",
        "takedown_control_model": "Needs per-fight takedown/control labels.",
        "odds_edge_model": "Needs historical odds snapshots.",
    }
    with open(settings.PROP_MODEL_METRICS_JSON, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    return metrics


def build_training_master(fights):
    fighters = load_fighters_cached().copy()
    fighters["_search_name"] = fighters["name"].astype(str).map(normalize_name)
    fights_elo, _elo_ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
    fight_counts = build_elo_fight_counts(fights_elo)
    fighters["elo"] = fighters["_search_name"].map(elo_by_search).fillna(settings.ELO_INITIAL)
    fighters["peak_elo"] = fighters["name"].map(
        lambda name: peak_elo.get(name, elo_by_search.get(normalize_name(name), settings.ELO_INITIAL))
    )
    fighters["elo_fights_count"] = fighters["_search_name"].map(fight_counts).fillna(0).astype(int)
    fighters["elo_source"] = fighters["elo_fights_count"].map(lambda count: "computed" if int(count) > 0 else "baseline")
    return add_rankings(fighters)


def add_rankings(fighters):
    out = fighters.copy()
    for ranking_df, prefix in ((p4p_rankings(), "p4p"), (division_point_dominance(), "dom")):
        ranks = ranking_df.copy()
        ranks["_search_name"] = ranks["Fighter"].astype(str).map(normalize_name)
        rename = {
            "Rank": f"rank_{prefix}",
            "Points": f"points_{prefix}",
            "Division": f"division_{prefix}",
            "Record": f"record_{prefix}",
        }
        ranks = ranks.rename(columns=rename)
        keep = ["_search_name"] + [value for value in rename.values() if value in ranks.columns]
        out = out.merge(ranks[keep].drop_duplicates("_search_name"), on="_search_name", how="left")
    return out


def train_softmax_model(model_name: str, X: np.ndarray, y: np.ndarray) -> tuple[dict, dict]:
    if len(y) < 50:
        raise RuntimeError(f"Too few samples to train {model_name}.")

    classes = sorted(str(label) for label in set(y))
    y_idx = np.array([classes.index(str(label)) for label in y], dtype=int)
    X_train, X_test, y_train, y_test = stratified_split(X, y_idx)
    means = X_train.mean(axis=0)
    scales = X_train.std(axis=0)
    scales[scales == 0] = 1.0
    X_train = (X_train - means) / scales
    X_test = (X_test - means) / scales
    weights, intercept = fit_softmax(X_train, y_train, len(classes))
    train_pred = predict_classes(X_train, weights, intercept)
    test_pred = predict_classes(X_test, weights, intercept)
    metrics = {
        "model_name": model_name,
        "model_version": MODEL_VERSION,
        "n_samples": int(len(y)),
        "classes": classes,
        "class_counts": {classes[index]: int(count) for index, count in Counter(y_idx).items()},
        "train_accuracy": round(float((train_pred == y_train).mean()), 4),
        "test_accuracy": round(float((test_pred == y_test).mean()), 4),
    }
    artifact = {
        "model_name": model_name,
        "model_version": MODEL_VERSION,
        "model_type": "numpy_softmax_logistic_regression",
        "feature_names": FEATURE_NAMES,
        "classes": classes,
        "means": means.tolist(),
        "scales": scales.tolist(),
        "weights": weights.tolist(),
        "intercept": intercept.tolist(),
        "metrics": metrics,
        "message": "Dedicated prop model artifact trained from cached fight result labels.",
    }
    return artifact, metrics


def stratified_split(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, seed: int = 42):
    rng = np.random.default_rng(seed)
    train_idx = []
    test_idx = []
    for class_id in sorted(set(y)):
        idx = np.where(y == class_id)[0]
        rng.shuffle(idx)
        n_test = max(1, int(round(len(idx) * test_size)))
        test_idx.extend(idx[:n_test])
        train_idx.extend(idx[n_test:])
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]


def fit_softmax(X: np.ndarray, y: np.ndarray, n_classes: int, lr: float = 0.08, epochs: int = 1200):
    n_samples, n_features = X.shape
    weights = np.zeros((n_classes, n_features), dtype=float)
    intercept = np.zeros(n_classes, dtype=float)
    counts = np.bincount(y, minlength=n_classes)
    class_weights = n_samples / np.maximum(counts, 1) / n_classes
    Y = np.eye(n_classes)[y]
    sample_weights = class_weights[y]

    for _ in range(epochs):
        logits = X @ weights.T + intercept
        probs = softmax(logits)
        error = (probs - Y) * sample_weights[:, None]
        weights -= lr * (error.T @ X / n_samples + 0.001 * weights)
        intercept -= lr * error.mean(axis=0)
    return weights, intercept


def predict_classes(X: np.ndarray, weights: np.ndarray, intercept: np.ndarray):
    return np.argmax(X @ weights.T + intercept, axis=1)


def softmax(logits: np.ndarray):
    shifted = logits - logits.max(axis=1, keepdims=True)
    exp = np.exp(shifted)
    return exp / exp.sum(axis=1, keepdims=True)


if __name__ == "__main__":
    results = train_prop_models()
    for name, metric in results.items():
        print(f"{name}: {metric}")
