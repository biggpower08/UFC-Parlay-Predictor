"""Versioned feature schemas for runtime-compatible MMA models."""

from __future__ import annotations

from dataclasses import asdict, dataclass


BASELINE_HISTORY_FEATURES = [
    "a_prior_fights",
    "b_prior_fights",
    "a_prior_wins",
    "b_prior_wins",
    "a_prior_finishes",
    "b_prior_finishes",
    "a_prior_decisions",
    "b_prior_decisions",
]

PROFILE_FEATURES = [
    "fighter_1_age",
    "fighter_2_age",
    "age_diff",
    "fighter_1_height",
    "fighter_2_height",
    "height_diff",
    "fighter_1_reach",
    "fighter_2_reach",
    "reach_diff",
    "fighter_1_stance_known",
    "fighter_2_stance_known",
]

RECORD_FEATURES = [
    "fighter_1_history_count",
    "fighter_2_history_count",
    "minimum_history_count",
    "fighter_1_win_rate_before",
    "fighter_2_win_rate_before",
    "win_rate_diff",
    "fighter_1_finish_win_rate_before",
    "fighter_2_finish_win_rate_before",
    "finish_rate_diff",
    "fighter_1_decision_win_rate_before",
    "fighter_2_decision_win_rate_before",
    "decision_rate_diff",
    "fighter_1_ko_tko_win_rate_before",
    "fighter_2_ko_tko_win_rate_before",
    "ko_tko_rate_diff",
    "fighter_1_submission_win_rate_before",
    "fighter_2_submission_win_rate_before",
    "submission_rate_diff",
    "fighter_1_finish_loss_rate_before",
    "fighter_2_finish_loss_rate_before",
    "fighter_1_decision_loss_rate_before",
    "fighter_2_decision_loss_rate_before",
]

RECENT_FORM_FEATURES = [
    "fighter_1_recent_3_win_rate",
    "fighter_2_recent_3_win_rate",
    "recent_3_win_rate_diff",
    "fighter_1_recent_5_win_rate",
    "fighter_2_recent_5_win_rate",
    "recent_5_win_rate_diff",
    "fighter_1_recent_3_finish_rate",
    "fighter_2_recent_3_finish_rate",
    "fighter_1_recent_5_finish_rate",
    "fighter_2_recent_5_finish_rate",
    "fighter_1_days_since_last_fight",
    "fighter_2_days_since_last_fight",
    "days_since_last_fight_diff",
    "fighter_1_fights_last_12_months",
    "fighter_2_fights_last_12_months",
    "fighter_1_fights_last_24_months",
    "fighter_2_fights_last_24_months",
]

ELO_FEATURES = [
    "fighter_1_elo_before_fight",
    "fighter_2_elo_before_fight",
    "elo_diff",
    "elo_expected_fighter_1",
    "fighter_1_elo_fights_count_before",
    "fighter_2_elo_fights_count_before",
    "fighter_1_elo_available",
    "fighter_2_elo_available",
]

STRIKING_FEATURES = [
    "fighter_1_avg_sig_strikes_landed_before",
    "fighter_2_avg_sig_strikes_landed_before",
    "sig_strike_landed_avg_diff",
    "fighter_1_avg_sig_strikes_absorbed_before",
    "fighter_2_avg_sig_strikes_absorbed_before",
    "sig_strike_absorbed_avg_diff",
    "fighter_1_avg_sig_strike_attempts_before",
    "fighter_2_avg_sig_strike_attempts_before",
    "fighter_1_sig_strike_accuracy_before",
    "fighter_2_sig_strike_accuracy_before",
    "fighter_1_sig_strike_defense_before",
    "fighter_2_sig_strike_defense_before",
    "fighter_1_recent_3_sig_strikes_landed_avg",
    "fighter_2_recent_3_sig_strikes_landed_avg",
    "fighter_1_recent_5_sig_strikes_landed_avg",
    "fighter_2_recent_5_sig_strikes_landed_avg",
]

GRAPPLING_FEATURES = [
    "fighter_1_avg_takedowns_landed_before",
    "fighter_2_avg_takedowns_landed_before",
    "takedown_avg_diff",
    "fighter_1_avg_takedowns_attempted_before",
    "fighter_2_avg_takedowns_attempted_before",
    "fighter_1_takedown_accuracy_before",
    "fighter_2_takedown_accuracy_before",
    "fighter_1_takedown_defense_before",
    "fighter_2_takedown_defense_before",
    "fighter_1_avg_control_time_before",
    "fighter_2_avg_control_time_before",
    "control_time_avg_diff",
    "fighter_1_avg_submission_attempts_before",
    "fighter_2_avg_submission_attempts_before",
    "fighter_1_recent_3_takedowns_avg",
    "fighter_2_recent_3_takedowns_avg",
    "fighter_1_recent_5_takedowns_avg",
    "fighter_2_recent_5_takedowns_avg",
]

STYLE_SCORE_FEATURES = [
    "fighter_1_striker_score",
    "fighter_2_striker_score",
    "striker_score_diff",
    "fighter_1_high_volume_striker_score",
    "fighter_2_high_volume_striker_score",
    "high_volume_striker_score_diff",
    "fighter_1_power_finisher_score",
    "fighter_2_power_finisher_score",
    "power_finisher_score_diff",
    "fighter_1_wrestler_score",
    "fighter_2_wrestler_score",
    "wrestler_score_diff",
    "fighter_1_grappler_score",
    "fighter_2_grappler_score",
    "grappler_score_diff",
    "fighter_1_submission_threat_score",
    "fighter_2_submission_threat_score",
    "submission_threat_score_diff",
    "fighter_1_control_fighter_score",
    "fighter_2_control_fighter_score",
    "control_fighter_score_diff",
    "fighter_1_high_pace_score",
    "fighter_2_high_pace_score",
    "high_pace_score_diff",
    "fighter_1_durability_score",
    "fighter_2_durability_score",
    "durability_score_diff",
    "fighter_1_decision_tendency_score",
    "fighter_2_decision_tendency_score",
    "decision_tendency_score_diff",
    "fighter_1_early_finish_threat_score",
    "fighter_2_early_finish_threat_score",
    "early_finish_threat_score_diff",
    "fighter_1_low_volume_control_score",
    "fighter_2_low_volume_control_score",
    "low_volume_control_score_diff",
    "fighter_1_volatility_score",
    "fighter_2_volatility_score",
    "volatility_score_diff",
]

OPPONENT_WEAKNESS_FEATURES = [
    "fighter_1_strike_absorption_weakness",
    "fighter_2_strike_absorption_weakness",
    "strike_absorption_weakness_diff",
    "fighter_1_takedown_defense_weakness_proxy",
    "fighter_2_takedown_defense_weakness_proxy",
    "takedown_defense_weakness_proxy_diff",
    "fighter_1_low_defensive_volume_weakness",
    "fighter_2_low_defensive_volume_weakness",
    "low_defensive_volume_weakness_diff",
    "fighter_1_submission_defense_weakness_proxy",
    "fighter_2_submission_defense_weakness_proxy",
    "submission_defense_weakness_proxy_diff",
    "fighter_1_grappling_exposure_weakness",
    "fighter_2_grappling_exposure_weakness",
    "grappling_exposure_weakness_diff",
    "fighter_1_control_vulnerability_proxy",
    "fighter_2_control_vulnerability_proxy",
    "control_vulnerability_proxy_diff",
    "fighter_1_durability_weakness",
    "fighter_2_durability_weakness",
    "durability_weakness_diff",
    "fighter_1_early_finish_vulnerability",
    "fighter_2_early_finish_vulnerability",
    "early_finish_vulnerability_diff",
    "fighter_1_low_activity_weakness",
    "fighter_2_low_activity_weakness",
    "low_activity_weakness_diff",
    "fighter_1_poor_recent_form_weakness",
    "fighter_2_poor_recent_form_weakness",
    "poor_recent_form_weakness_diff",
    "fighter_1_pace_breakdown_risk",
    "fighter_2_pace_breakdown_risk",
    "pace_breakdown_risk_diff",
    "fighter_1_cardio_late_fight_risk_proxy",
    "fighter_2_cardio_late_fight_risk_proxy",
    "cardio_late_fight_risk_proxy_diff",
]

SIZE_CONTEXT_FEATURES = [
    "same_division",
    "cross_division",
    "catchweight",
    "weight_class_gap",
    "estimated_weight_gap_lbs",
    "scheduled_rounds",
    "height_gap",
    "reach_gap",
    "unknown_size_context",
    "size_context_quality",
    "pound_for_pound_mode",
    "size_features_used",
]

DATA_QUALITY_FEATURES = [
    "low_sample_warning",
    "missing_profile_warning",
    "missing_stats_warning",
    "cross_division_warning",
]

FORBIDDEN_FEATURES = [
    "winner",
    "winner_name",
    "loser",
    "loser_name",
    "result",
    "method",
    "method_group",
    "method_class",
    "finish_type_class",
    "finish_binary",
    "goes_distance_binary",
    "over_1_5_binary",
    "over_2_5_binary",
    "ends_before_round_3_binary",
    "finish_in_round_1_binary",
    "round_phase_class",
    "round_number",
    "finish_round",
    "finish_time",
    "f1_wins",
    "went_distance",
    "over_2_5",
    "fighter_a_sig_strikes",
    "fighter_b_sig_strikes",
    "combined_sig_strikes",
    "fighter_a_takedowns",
    "fighter_b_takedowns",
    "grappling_heavy_binary",
]


@dataclass(frozen=True)
class FeatureSchema:
    model_family: str
    schema_name: str
    schema_version: str
    required_features: list[str]
    optional_features: list[str]
    forbidden_features: list[str]
    runtime_available_features: list[str]
    derived_possible_features: list[str]

    def all_features(self) -> list[str]:
        return list(dict.fromkeys(self.required_features + self.optional_features))

    def to_dict(self) -> dict:
        return asdict(self)


def get_feature_schema(model_family: str = "winner") -> FeatureSchema:
    family = normalize_model_family(model_family)
    optional = list(
        dict.fromkeys(
            PROFILE_FEATURES
            + RECORD_FEATURES
            + RECENT_FORM_FEATURES
            + ELO_FEATURES
            + STYLE_SCORE_FEATURES
            + OPPONENT_WEAKNESS_FEATURES
            + SIZE_CONTEXT_FEATURES
            + DATA_QUALITY_FEATURES
        )
    )
    derived = list(dict.fromkeys(STRIKING_FEATURES + GRAPPLING_FEATURES))
    if family in {"strike_volume", "takedown_control"}:
        optional = list(dict.fromkeys(optional + derived))
        derived = []
    return FeatureSchema(
        model_family=family,
        schema_name=f"{family}_v1",
        schema_version="1.0",
        required_features=list(BASELINE_HISTORY_FEATURES),
        optional_features=optional,
        forbidden_features=list(FORBIDDEN_FEATURES),
        runtime_available_features=list(dict.fromkeys(BASELINE_HISTORY_FEATURES + PROFILE_FEATURES + RECORD_FEATURES + RECENT_FORM_FEATURES + ELO_FEATURES + SIZE_CONTEXT_FEATURES + DATA_QUALITY_FEATURES)),
        derived_possible_features=derived,
    )


def normalize_model_family(model_family: str) -> str:
    key = str(model_family or "winner").strip().lower().replace("-", "_")
    aliases = {
        "winner_model": "winner",
        "fight_duration_model": "finish",
        "finish_model": "finish",
        "goes_distance_model": "goes_distance",
        "finish_type_model": "method",
        "method_umbrella_model": "method",
        "method_model": "method",
        "over_1_5_model": "round_phase",
        "over_2_5_model": "round_phase",
        "ends_before_round_3_model": "round_phase",
        "finish_in_round_1_model": "round_phase",
        "exact_finish_round_model": "round_phase",
        "round_model": "round_phase",
        "round_phase_model": "round_phase",
        "strike_volume_model": "strike_volume",
        "takedown_control_model": "takedown_control",
        "odds_calibration_model": "odds_calibration",
    }
    return aliases.get(key, key)
