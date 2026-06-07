"""Runtime availability checks for feature-factory outputs."""

from __future__ import annotations

from typing import Any

from ufc_predictor.features.feature_schema import FeatureSchema


def summarize_feature_availability(features: dict[str, Any], schema: FeatureSchema) -> dict:
    all_features = schema.all_features()
    missing_required = [
        name for name in schema.required_features
        if name not in features or features.get(name) is None
    ]
    missing_optional = [
        name for name in schema.optional_features
        if name not in features or features.get(name) is None
    ]
    available_required = len(schema.required_features) - len(missing_required)
    available_optional = len(schema.optional_features) - len(missing_optional)
    return {
        "required_features": len(schema.required_features),
        "required_features_available": available_required == len(schema.required_features),
        "required_feature_coverage": _coverage(available_required, len(schema.required_features)),
        "optional_features": len(schema.optional_features),
        "optional_feature_coverage": _coverage(available_optional, len(schema.optional_features)),
        "missing_required_features": missing_required,
        "missing_optional_features": missing_optional,
        "unknown_features": sorted(set(features) - set(all_features)),
    }


def _coverage(available: int, total: int) -> float:
    if total <= 0:
        return 1.0
    return round(float(available) / float(total), 4)
