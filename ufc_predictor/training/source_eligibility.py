"""Source eligibility rules for model training and reporting."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd


RESULT_LABEL_MODELS = {
    "winner_model",
    "fight_duration_model",
    "finish_model",
    "goes_distance_model",
    "over_1_5_model",
    "over_2_5_model",
    "ends_before_round_3_model",
    "finish_in_round_1_model",
    "finish_type_model",
    "method_umbrella_model",
    "method_model",
}

STAT_LABEL_MODELS = {"strike_volume_model", "takedown_control_model"}


@dataclass(frozen=True)
class SourceEligibility:
    source: str
    safe_uses: list[str]
    unsafe_uses: list[str]
    model_eligibility: dict[str, str]
    notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SOURCE_ELIGIBILITY_RULES: dict[str, SourceEligibility] = {
    "ufc_stats_complete": SourceEligibility(
        source="ufc_stats_complete",
        safe_uses=["strike labels", "takedown/control labels", "stat coverage cross-checks"],
        unsafe_uses=["universal winner labels", "universal duration labels", "universal method labels", "universal round labels"],
        model_eligibility={
            "winner_model": "ineligible_result_labels_unsafe",
            "fight_duration_model": "ineligible_result_labels_unsafe",
            "finish_model": "ineligible_result_labels_unsafe",
            "goes_distance_model": "ineligible_result_labels_unsafe",
            "over_1_5_model": "ineligible_round_result_labels_unsafe",
            "over_2_5_model": "ineligible_round_result_labels_unsafe",
            "ends_before_round_3_model": "ineligible_round_result_labels_unsafe",
            "finish_in_round_1_model": "ineligible_round_result_labels_unsafe",
            "finish_type_model": "ineligible_method_labels_unsafe",
            "method_umbrella_model": "ineligible_method_labels_unsafe",
            "method_model": "ineligible_method_labels_unsafe",
            "strike_volume_model": "eligible_stat_labels",
            "takedown_control_model": "eligible_stat_labels",
            "odds_calibration_model": "ineligible_no_trusted_prefight_odds",
        },
        notes=[
            "Treat primarily as a stat-rich source, not a universal result-label source.",
            "No-contest, draw, unknown, or missing result rows must not create fake target labels.",
        ],
    ),
    "mdabbert_ultimate": SourceEligibility(
        source="mdabbert_ultimate",
        safe_uses=["broad result history", "winner/duration/method labels where present", "odds-aware research review"],
        unsafe_uses=["primary strike/takedown/control labels when detailed stats are missing"],
        model_eligibility={
            "winner_model": "eligible_safe_result_labels",
            "fight_duration_model": "eligible_safe_result_labels",
            "finish_model": "eligible_safe_result_labels",
            "goes_distance_model": "eligible_safe_result_labels",
            "over_1_5_model": "eligible_if_round_time_present",
            "over_2_5_model": "eligible_if_round_time_present",
            "ends_before_round_3_model": "eligible_if_round_time_present",
            "finish_in_round_1_model": "eligible_if_round_time_present",
            "finish_type_model": "eligible_clean_method_labels",
            "method_umbrella_model": "eligible_if_components_eligible",
            "method_model": "eligible_if_components_eligible",
            "strike_volume_model": "ineligible_missing_stat_labels",
            "takedown_control_model": "ineligible_missing_stat_labels",
            "odds_calibration_model": "blocked_until_prefight_timestamps_trusted",
        },
        notes=["Useful broad history source, but detailed stat coverage is weaker."],
    ),
    "ufc_1994_2025": SourceEligibility(
        source="ufc_1994_2025",
        safe_uses=["broad fight history", "result/method/round labels", "stat labels with drift review"],
        unsafe_uses=["unreviewed production stat modeling"],
        model_eligibility={
            "winner_model": "eligible_safe_result_labels",
            "fight_duration_model": "eligible_safe_result_labels",
            "finish_model": "eligible_safe_result_labels",
            "goes_distance_model": "eligible_safe_result_labels",
            "over_1_5_model": "eligible_if_round_time_present",
            "over_2_5_model": "eligible_if_round_time_present",
            "ends_before_round_3_model": "eligible_if_round_time_present",
            "finish_in_round_1_model": "eligible_if_round_time_present",
            "finish_type_model": "eligible_clean_method_labels",
            "method_umbrella_model": "eligible_if_components_eligible",
            "method_model": "eligible_if_components_eligible",
            "strike_volume_model": "eligible_with_drift_review",
            "takedown_control_model": "eligible_with_drift_review",
            "odds_calibration_model": "ineligible_no_trusted_prefight_odds",
        },
        notes=["Broad source, but method/stat drift still needs monitoring."],
    ),
    "ufc_1994_2026": SourceEligibility(
        source="ufc_1994_2026",
        safe_uses=["broad fight history", "result/method/round labels"],
        unsafe_uses=["unreviewed production use where holdout drift is high"],
        model_eligibility={
            "winner_model": "eligible_but_source_transfer_review_needed",
            "fight_duration_model": "eligible_safe_result_labels",
            "finish_model": "eligible_safe_result_labels",
            "goes_distance_model": "eligible_safe_result_labels",
            "over_1_5_model": "eligible_if_round_time_present",
            "over_2_5_model": "eligible_if_round_time_present",
            "ends_before_round_3_model": "eligible_if_round_time_present",
            "finish_in_round_1_model": "eligible_if_round_time_present",
            "finish_type_model": "eligible_clean_method_labels",
            "method_umbrella_model": "eligible_if_components_eligible",
            "method_model": "eligible_if_components_eligible",
            "strike_volume_model": "ineligible_missing_stat_labels",
            "takedown_control_model": "eligible_with_drift_review",
            "odds_calibration_model": "ineligible_no_trusted_prefight_odds",
        },
        notes=["Useful broad history source with high drift in some holdouts."],
    ),
    "ufc_fight_forecast": SourceEligibility(
        source="ufc_fight_forecast",
        safe_uses=["broad result history", "result/method/round labels", "some stat labels"],
        unsafe_uses=["winner production claims until transfer stabilizes"],
        model_eligibility={
            "winner_model": "eligible_but_source_transfer_review_needed",
            "fight_duration_model": "eligible_safe_result_labels",
            "finish_model": "eligible_safe_result_labels",
            "goes_distance_model": "eligible_safe_result_labels",
            "over_1_5_model": "eligible_if_round_time_present",
            "over_2_5_model": "eligible_if_round_time_present",
            "ends_before_round_3_model": "eligible_if_round_time_present",
            "finish_in_round_1_model": "eligible_if_round_time_present",
            "finish_type_model": "eligible_clean_method_labels",
            "method_umbrella_model": "eligible_if_components_eligible",
            "method_model": "eligible_if_components_eligible",
            "strike_volume_model": "eligible_with_drift_review",
            "takedown_control_model": "eligible_with_drift_review",
            "odds_calibration_model": "ineligible_no_trusted_prefight_odds",
        },
        notes=["Medium drift source; winner transfer remains mixed."],
    ),
}


def source_rules_as_dict() -> dict[str, dict[str, Any]]:
    return {source: rule.to_dict() for source, rule in SOURCE_ELIGIBILITY_RULES.items()}


def model_source_status(source: str, model_name: str) -> str:
    rule = SOURCE_ELIGIBILITY_RULES.get(source)
    if not rule:
        return "unknown_source_review_needed"
    return rule.model_eligibility.get(model_name, "unknown_model_review_needed")


def source_is_eligible_for_model(source: str, model_name: str) -> bool:
    status = model_source_status(source, model_name)
    return status.startswith("eligible")


def eligible_sources_for_model(model_name: str) -> list[str]:
    return [source for source in sorted(SOURCE_ELIGIBILITY_RULES) if source_is_eligible_for_model(source, model_name)]


def filter_rows_for_model_source_eligibility(rows: pd.DataFrame, model_name: str) -> pd.DataFrame:
    if rows.empty or "source_dataset" not in rows.columns:
        return rows.copy()
    eligible = set(eligible_sources_for_model(model_name))
    return rows[rows["source_dataset"].astype(str).isin(eligible)].copy()
