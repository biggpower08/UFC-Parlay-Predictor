"""Training readiness registry for dedicated prop models."""

from __future__ import annotations


MODEL_TRAINING_ORDER = [
    "finish_model",
    "goes_distance_model",
    "method_model",
    "round_model",
    "strike_volume_model",
    "takedown_control_model",
]


def model_training_plan(audit: dict) -> dict:
    ready = bool(audit.get("training_data_ready"))
    labels = audit.get("label_availability", {})
    return {
        "finish_model": "training_data_ready" if ready and labels.get("finish_binary", 0) else "not_trained",
        "goes_distance_model": "training_data_ready" if ready and labels.get("goes_distance_binary", 0) else "not_trained",
        "method_model": "training_data_ready" if ready and labels.get("method_class", 0) else "not_trained",
        "round_model": "training_data_ready" if ready and labels.get("round_phase_class", 0) else "not_trained",
        "strike_volume_model": "insufficient_data" if not labels.get("combined_sig_strikes", 0) else "training_data_ready",
        "takedown_control_model": "insufficient_data" if not labels.get("fighter_a_takedowns", 0) else "training_data_ready",
    }
