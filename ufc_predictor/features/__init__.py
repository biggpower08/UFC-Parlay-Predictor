from ufc_predictor.features.matchup_builder import FEATURE_NAMES, build_matchup_features
from ufc_predictor.features.matchup_features import (
    build_historical_feature_set,
    build_matchup_feature_set,
    get_runtime_matchup_features,
    validate_feature_set,
)

__all__ = [
    "build_master_df",
    "compare_fighters",
    "extract_stats",
    "FEATURE_NAMES",
    "build_matchup_features",
    "build_matchup_feature_set",
    "build_historical_feature_set",
    "get_runtime_matchup_features",
    "validate_feature_set",
]


def __getattr__(name):
    if name in {"build_master_df", "compare_fighters", "extract_stats"}:
        from ufc_predictor.features import feature_engineering

        return getattr(feature_engineering, name)
    raise AttributeError(name)
