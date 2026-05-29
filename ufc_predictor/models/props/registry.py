"""Registry for dedicated betting/prop models.

Models are only marked trained when a saved artifact exists and its metadata
confirms a credible training-data path. Cached-label experiments should remain
not_trained until source health and leakage-safe datasets are proven.
"""

from __future__ import annotations

from dataclasses import asdict

from ufc_predictor.models.props.predictor import load_prop_model, model_artifact_available
from ufc_predictor.models.props.schemas import PropModelStatus

TRAINABLE_NOW = {
    "finish_model",
    "goes_distance_model",
    "method_model",
    "round_model",
}

MODEL_NAMES = [
    "method_model",
    "round_model",
    "goes_distance_model",
    "finish_model",
    "strike_volume_model",
    "takedown_control_model",
    "odds_edge_model",
]


def prop_model_status() -> dict:
    statuses = {}
    for name in MODEL_NAMES:
        artifact = load_prop_model(name) if model_artifact_available(name) else None
        artifact_status = _artifact_status(artifact)
        if artifact_status in {"trained", "experimental"}:
            status = PropModelStatus(
                name=name,
                status=artifact_status,
                support_level="model_supported",
                message="Dedicated prop model artifact includes metadata and validation metrics.",
            )
        elif name in TRAINABLE_NOW:
            status = PropModelStatus(
                name=name,
                status="not_trained",
                support_level="not_available",
                message="Training is blocked until credible source health and leakage-safe training data are proven.",
            )
        else:
            status = PropModelStatus(
                name=name,
                status="not_trained",
                support_level="not_available",
                message="Training is blocked until the required per-fight labels or odds history exist.",
            )
        statuses[name] = asdict(status)
    return statuses


def _artifact_is_credible(artifact: dict | None) -> bool:
    return _artifact_status(artifact) == "trained"


def _artifact_status(artifact: dict | None) -> str | None:
    if not artifact:
        return None
    metadata = artifact.get("metadata") or {}
    metrics = artifact.get("metrics") or {}
    valid = bool(
        artifact.get("model_name")
        and artifact.get("feature_names")
        and metrics
        and metadata.get("leakage_checked") is True
        and metadata.get("trained_at")
        and metadata.get("data_cutoff_date")
    )
    if not valid:
        return None
    if metadata.get("status") in {"trained", "experimental"}:
        return metadata.get("status")
    if metadata.get("training_source_status") == "credible":
        return "trained"
    return None
