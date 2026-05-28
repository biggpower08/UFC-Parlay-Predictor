"""Registry for future dedicated betting/prop models."""

from __future__ import annotations

from dataclasses import asdict

from ufc_predictor.models.props.schemas import PropModelStatus

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
    return {
        name: asdict(
            PropModelStatus(
                name=name,
                status="not_trained",
                support_level="not_available",
                message="No trained dedicated model artifact is available yet.",
            )
        )
        for name in MODEL_NAMES
    }
