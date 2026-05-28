from ufc_predictor.features.matchup_builder import FEATURE_NAMES, build_matchup_features

__all__ = [
    "build_master_df",
    "compare_fighters",
    "extract_stats",
    "FEATURE_NAMES",
    "build_matchup_features",
]


def __getattr__(name):
    if name in {"build_master_df", "compare_fighters", "extract_stats"}:
        from ufc_predictor.features import feature_engineering

        return getattr(feature_engineering, name)
    raise AttributeError(name)
