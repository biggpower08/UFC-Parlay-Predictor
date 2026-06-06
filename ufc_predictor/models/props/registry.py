"""Registry for dedicated betting/prop models.

Models are only marked trained when a saved artifact exists and its metadata
confirms a credible training-data path. Cached-label experiments should remain
not_trained until source health and leakage-safe datasets are proven.
"""

from __future__ import annotations

from dataclasses import asdict
import json

from ufc_predictor.config import settings
from ufc_predictor.models.props.predictor import load_prop_model, model_artifact_available
from ufc_predictor.models.props.schemas import PropModelStatus

MODEL_NAMES = [
    "winner_model",
    "method_model",
    "round_model",
    "goes_distance_model",
    "finish_model",
    "strike_volume_model",
    "takedown_control_model",
    "odds_calibration_model",
]


def prop_model_status() -> dict:
    statuses = {}
    registry_statuses = _registry_statuses()
    metrics_statuses = _metrics_statuses()
    for name in MODEL_NAMES:
        if name in registry_statuses:
            statuses[name] = registry_statuses[name]
            continue
        artifact = load_prop_model(name) if model_artifact_available(name) else None
        artifact_status = _artifact_status(artifact)
        if artifact_status in {"production_ready", "trained", "experimental"}:
            status = PropModelStatus(
                name=name,
                status=artifact_status,
                support_level="model_supported",
                message="Dedicated prop model artifact includes metadata and validation metrics.",
            )
        elif metrics_statuses.get(name) == "insufficient_data":
            status = PropModelStatus(
                name=name,
                status="insufficient_data",
                support_level="not_available",
                message=metrics_statuses.get(f"{name}:reason") or "Training data is insufficient for this dedicated prop model.",
            )
        elif name in {"finish_model", "goes_distance_model", "method_model", "round_model"}:
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
    if metadata.get("status") in {"production_ready", "trained", "experimental"}:
        return metadata.get("status")
    if metadata.get("training_source_status") == "credible":
        return "trained"
    return None


def _registry_statuses() -> dict[str, dict]:
    if not settings.MODEL_REGISTRY_JSON.is_file():
        return {}
    try:
        with open(settings.MODEL_REGISTRY_JSON, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}

    statuses = {}
    for name, entry in payload.items():
        status_value = entry.get("status") or "not_trained"
        support_level = "model_supported" if status_value in {"production_ready", "trained", "experimental"} else "not_available"
        statuses[name] = {
            "name": name,
            "status": status_value,
            "support_level": support_level,
            "message": public_message(status_value, entry),
            "target_label": entry.get("target_label"),
            "training_rows": entry.get("training_rows", 0),
            "validation_rows": entry.get("validation_rows", 0),
            "date_range": entry.get("date_range"),
            "split_type": entry.get("split_type"),
        }
    return statuses


def public_message(status: str, entry: dict) -> str:
    if status == "production_ready":
        return "Model trained and validated against a baseline."
    if status == "trained":
        return "Model trained with validation metrics; outputs should still be treated as fight research."
    if status == "experimental":
        return "Experimental model trained, but data quality or split limitations remain."
    if status == "insufficient_data":
        return "Insufficient labeled data is available for this dedicated model."
    if status == "blocked":
        limitations = entry.get("limitations") or []
        return limitations[0] if limitations else "This model is blocked by missing source data."
    return "Dedicated model is not trained yet."


def _metrics_statuses() -> dict[str, str]:
    if not settings.PROP_MODEL_METRICS_JSON.is_file():
        return {}
    try:
        with open(settings.PROP_MODEL_METRICS_JSON, encoding="utf-8") as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return {}
    statuses = {}
    for name, entry in payload.items():
        status = entry.get("status")
        if status:
            statuses[name] = status
        if entry.get("reason"):
            statuses[f"{name}:reason"] = entry["reason"]
    return statuses
