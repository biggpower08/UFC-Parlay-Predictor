"""Predictor interfaces for future dedicated prop models."""

from __future__ import annotations


class PropModelPredictor:
    model_name = "base_prop_model"

    def status(self) -> str:
        return "not_trained"

    def predict(self, *_args, **_kwargs) -> dict:
        return {
            "status": "not_trained",
            "support_level": "not_available",
            "message": "No trained dedicated prop model artifact is available.",
            "probability": None,
        }
