"""Semantic feature groups for safe pre-fight MMA model interactions."""

from __future__ import annotations

from ufc_predictor.features.feature_schema import FORBIDDEN_FEATURES, get_feature_schema


FEATURE_GROUP_KEYWORDS: dict[str, tuple[str, ...]] = {
    "physical": ("age", "height", "reach", "stance", "weight_gap", "size", "same_division", "cross_division"),
    "experience": ("prior_fights", "history_count", "prior_wins", "win_rate", "days_since", "recent", "fights_last"),
    "striking": ("sig_strike", "strikes", "knockdown", "striking", "striker_score", "high_volume_striker", "pace"),
    "grappling": ("takedown", "wrestler", "control_fighter", "control_vulnerability", "submission_attempt", "submission_threat", "grappler", "grappling"),
    "finishing": ("finish", "ko_tko", "submission", "decision", "durability", "power_finisher", "early_finish", "volatility"),
    "division_context": ("division", "weight_class", "scheduled_rounds", "catchweight", "size_context"),
    "opponent_weakness": ("absorbed", "absorption_weakness", "defense_weakness", "defensive_volume_weakness", "vulnerability", "exposure_weakness", "finish_loss", "durability_weakness", "low_activity_weakness", "poor_recent_form_weakness", "breakdown_risk", "cardio_late"),
    "model_probability": ("duration_probability", "expected_fight_length", "finish_probability"),
    "data_quality": ("warning", "quality", "available", "missing", "low_sample"),
}

MODEL_ALLOWED_GROUPS: dict[str, set[str]] = {
    "winner_model": {"physical", "experience", "striking", "grappling", "finishing", "division_context", "opponent_weakness", "data_quality"},
    "fight_duration_model": {"finishing", "opponent_weakness", "striking", "grappling", "division_context", "physical", "experience"},
    "finish_type_model": {"finishing", "striking", "grappling", "opponent_weakness", "physical"},
    "method_umbrella_model": {"finishing", "striking", "grappling", "opponent_weakness", "physical", "division_context"},
    "over_1_5_model": {"striking", "grappling", "finishing", "opponent_weakness", "division_context", "experience"},
    "over_2_5_model": {"striking", "grappling", "finishing", "opponent_weakness", "division_context", "experience"},
    "ends_before_round_3_model": {"striking", "grappling", "finishing", "opponent_weakness", "division_context", "experience"},
    "finish_in_round_1_model": {"striking", "grappling", "finishing", "opponent_weakness", "division_context", "experience"},
    "strike_volume_model": {"striking", "grappling", "opponent_weakness", "physical", "division_context", "experience"},
    "takedown_control_model": {"grappling", "opponent_weakness", "physical", "division_context", "experience"},
}


def safe_prefight_features(model_name: str, feature_names: list[str]) -> list[str]:
    schema = get_feature_schema(model_name)
    forbidden = set(FORBIDDEN_FEATURES) | set(schema.forbidden_features)
    return [feature for feature in feature_names if feature not in forbidden]


def group_features(model_name: str, feature_names: list[str]) -> dict[str, list[str]]:
    allowed_groups = MODEL_ALLOWED_GROUPS.get(model_name, set(FEATURE_GROUP_KEYWORDS))
    grouped = {group: [] for group in allowed_groups}
    for feature in safe_prefight_features(model_name, feature_names):
        lowered = feature.lower()
        for group, keywords in FEATURE_GROUP_KEYWORDS.items():
            if group in allowed_groups and any(keyword in lowered for keyword in keywords):
                grouped.setdefault(group, []).append(feature)
    return {group: sorted(set(values)) for group, values in grouped.items() if values}


def feature_group_report(model_name: str, feature_names: list[str]) -> dict[str, list[str]]:
    return group_features(model_name, feature_names)
