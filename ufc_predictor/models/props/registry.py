"""Registry for dedicated betting/prop models."""

from __future__ import annotations

from dataclasses import asdict

from ufc_predictor.models.props.predictor import model_artifact_available
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
        if model_artifact_available(name):
            status = PropModelStatus(
                name=name,
                status="trained",
                support_level="model_supported",
                message="Dedicated prop model artifact is available.",
            )
        elif name in TRAINABLE_NOW:
            status = PropModelStatus(
                name=name,
                status="not_trained",
                support_level="not_available",
                message="This model can be trained from cached fight result labels.",
            )
        else:
            status = PropModelStatus(
                name=name,
                status="insufficient_data",
                support_level="not_available",
                message="Per-fight strike/control or historical odds data is not available yet.",
            )
        statuses[name] = asdict(status)
    return statuses
