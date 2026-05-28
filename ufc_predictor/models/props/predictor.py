"""JSON-backed prop model predictor.

The first prop models are lightweight logistic-regression artifacts trained
from cached fight history. They avoid sklearn/joblib at runtime so the public
app can report model status without extra dependencies.
"""

from __future__ import annotations

import json
from functools import lru_cache

import numpy as np

from ufc_predictor.config import settings
from ufc_predictor.features.matchup_builder import FEATURE_NAMES


@lru_cache(maxsize=None)
def load_prop_model(model_name: str) -> dict | None:
    path = settings.PROP_MODELS_DIR / f"{model_name}.json"
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def model_artifact_available(model_name: str) -> bool:
    return load_prop_model(model_name) is not None


def predict_prop_model(model_name: str, feature_dict: dict) -> dict:
    artifact = load_prop_model(model_name)
    if artifact is None or not _artifact_is_usable(artifact):
        return {
            "status": "not_trained",
            "support_level": "not_available",
            "message": "No credible trained dedicated prop model artifact is available.",
            "probabilities": {},
            "label": None,
        }

    expected_features = artifact.get("feature_names") or FEATURE_NAMES
    vector = np.array([float(feature_dict.get(name, 0.0) or 0.0) for name in expected_features], dtype=float)
    means = np.array(artifact["means"], dtype=float)
    scales = np.array(artifact["scales"], dtype=float)
    X = (vector - means) / scales
    weights = np.array(artifact["weights"], dtype=float)
    intercept = np.array(artifact["intercept"], dtype=float)
    logits = X @ weights.T + intercept
    probs = _softmax(logits)
    classes = artifact["classes"]
    best_index = int(np.argmax(probs))
    return {
        "status": "trained",
        "support_level": "model_supported",
        "message": artifact.get("message", "Dedicated prop model artifact is available."),
        "label": classes[best_index],
        "confidence": _confidence_label(float(probs[best_index])),
        "probabilities": {classes[i]: round(float(probs[i]), 4) for i in range(len(classes))},
        "model_version": artifact.get("model_version"),
    }


def feature_dict_from_analysis_stats(stats_a: dict, stats_b: dict) -> dict:
    def num(stats, key):
        try:
            value = float(stats.get(key) or 0.0)
        except (TypeError, ValueError):
            return 0.0
        return value if value == value else 0.0

    return {
        "delta_slpm": num(stats_a, "SLpM") - num(stats_b, "SLpM"),
        "delta_str_acc": num(stats_a, "Str Acc %") - num(stats_b, "Str Acc %"),
        "delta_str_def": num(stats_a, "Str Def %") - num(stats_b, "Str Def %"),
        "delta_sapm": num(stats_a, "SApM") - num(stats_b, "SApM"),
        "delta_td_avg": num(stats_a, "TD Avg") - num(stats_b, "TD Avg"),
        "delta_td_acc": num(stats_a, "TD Acc %") - num(stats_b, "TD Acc %"),
        "delta_td_def": num(stats_a, "TD Def %") - num(stats_b, "TD Def %"),
        "delta_sub_avg": num(stats_a, "Sub Avg") - num(stats_b, "Sub Avg"),
        "delta_reach": num(stats_a, "Reach (cm)") - num(stats_b, "Reach (cm)"),
        "delta_elo": num(stats_a, "Elo") - num(stats_b, "Elo"),
        "delta_points_p4p": num(stats_a, "P4P Points") - num(stats_b, "P4P Points"),
        "delta_rank_p4p": num(stats_b, "P4P Rank") - num(stats_a, "P4P Rank"),
        "delta_points_dom": num(stats_a, "Dom Points") - num(stats_b, "Dom Points"),
        "delta_rank_dom": num(stats_b, "Dom Rank") - num(stats_a, "Dom Rank"),
        "elo_expected_a": 1 / (1 + 10 ** ((num(stats_b, "Elo") - num(stats_a, "Elo")) / 400)),
    }


def predict_supported_prop_models(stats_a: dict, stats_b: dict) -> dict:
    features = feature_dict_from_analysis_stats(stats_a, stats_b)
    return {
        model_name: predict_prop_model(model_name, features)
        for model_name in ("finish_model", "goes_distance_model", "method_model", "round_model")
    }


def _softmax(logits):
    shifted = logits - np.max(logits)
    exp = np.exp(shifted)
    return exp / np.sum(exp)


def _confidence_label(probability: float) -> str:
    if probability >= 0.68:
        return "high"
    if probability >= 0.58:
        return "medium"
    return "low"


def _artifact_is_usable(artifact: dict) -> bool:
    metadata = artifact.get("metadata") or {}
    return bool(
        artifact.get("feature_names")
        and artifact.get("metrics")
        and metadata.get("training_source_status") == "credible"
        and metadata.get("leakage_checked") is True
    )
