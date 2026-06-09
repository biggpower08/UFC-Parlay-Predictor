"""Runtime-compatible matchup feature factory.

This module is intentionally separate from the older winner-model
`matchup_builder` module. It creates one schema-aligned feature payload that can
be used for historical training rows and live user-selected matchups.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from ufc_predictor.features.feature_schema import FeatureSchema, get_feature_schema, normalize_model_family
from ufc_predictor.features.fighter_snapshots import build_fighter_snapshot
from ufc_predictor.features.runtime_availability import summarize_feature_availability
from ufc_predictor.training.leakage import scan_dataframe
from ufc_predictor.training.size_context import build_size_context
from ufc_predictor.utils.helpers import normalize_name


@dataclass
class MatchupFeatureSet:
    features: dict[str, Any]
    feature_schema_name: str
    feature_schema_version: str
    model_family: str
    mode: str
    feature_mode: str
    missing_features: list[str]
    unavailable_features: list[str]
    estimated_features: list[str]
    leakage_excluded_features: list[str]
    data_quality_warnings: list[str]
    validation: dict[str, Any]
    model_feature_coverage: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_matchup_feature_set(
    fighter_1: str | dict | pd.Series,
    fighter_2: str | dict | pd.Series,
    fights: pd.DataFrame | None = None,
    as_of_date: str | None = None,
    mode: str = "live",
    model_family: str = "winner",
    feature_mode: str = "actual_fight",
    scheduled_rounds: int | None = None,
    weight_class: str | None = None,
) -> MatchupFeatureSet:
    schema = get_feature_schema(model_family)
    pound_for_pound = feature_mode == "pound_for_pound"
    snapshot_1 = build_fighter_snapshot(fighter_1, fights=fights, as_of_date=as_of_date)
    snapshot_2 = build_fighter_snapshot(fighter_2, fights=fights, as_of_date=as_of_date)
    return build_features_from_snapshots(
        snapshot_1,
        snapshot_2,
        schema=schema,
        as_of_date=as_of_date,
        mode=mode,
        feature_mode=feature_mode,
        scheduled_rounds=scheduled_rounds,
        weight_class=weight_class,
        pound_for_pound=pound_for_pound,
    )


def build_historical_feature_set(
    fight: dict | pd.Series,
    fights: pd.DataFrame,
    model_family: str = "winner",
    feature_mode: str = "actual_fight",
) -> MatchupFeatureSet:
    row = fight.to_dict() if isinstance(fight, pd.Series) else dict(fight)
    return build_matchup_feature_set(
        row.get("fighter_1") or row.get("fighter_a") or row.get("fighter_1_name"),
        row.get("fighter_2") or row.get("fighter_b") or row.get("fighter_2_name"),
        fights=fights,
        as_of_date=row.get("event_date"),
        mode="historical",
        model_family=model_family,
        feature_mode=feature_mode,
        scheduled_rounds=_safe_int(row.get("scheduled_rounds")),
        weight_class=row.get("weight_class"),
    )


def get_runtime_matchup_features(
    fighter_1: dict | pd.Series,
    fighter_2: dict | pd.Series,
    model_family: str = "winner",
    feature_mode: str = "actual_fight",
) -> dict[str, Any]:
    return build_matchup_feature_set(
        fighter_1,
        fighter_2,
        mode="live",
        model_family=model_family,
        feature_mode=feature_mode,
    ).to_dict()


def build_features_from_snapshots(
    snapshot_1: dict[str, Any],
    snapshot_2: dict[str, Any],
    schema: FeatureSchema | None = None,
    as_of_date: str | None = None,
    mode: str = "live",
    feature_mode: str = "actual_fight",
    scheduled_rounds: int | None = None,
    weight_class: str | None = None,
    pound_for_pound: bool = False,
) -> MatchupFeatureSet:
    schema = schema or get_feature_schema("winner")
    size_context = build_size_context(
        _size_profile(snapshot_1, weight_class),
        _size_profile(snapshot_2, weight_class),
        pound_for_pound=pound_for_pound,
    )
    features = _empty_features(schema)
    features.update(
        {
            "a_prior_fights": _number(snapshot_1.get("total_fights_before"), 0),
            "b_prior_fights": _number(snapshot_2.get("total_fights_before"), 0),
            "a_prior_wins": _number(snapshot_1.get("wins_before"), 0),
            "b_prior_wins": _number(snapshot_2.get("wins_before"), 0),
            "a_prior_finishes": _rate_count(snapshot_1, "finish_win_rate_before", "wins_before"),
            "b_prior_finishes": _rate_count(snapshot_2, "finish_win_rate_before", "wins_before"),
            "a_prior_decisions": _rate_count(snapshot_1, "decision_win_rate_before", "wins_before"),
            "b_prior_decisions": _rate_count(snapshot_2, "decision_win_rate_before", "wins_before"),
            "fighter_1_age": snapshot_1.get("age_at_fight_date"),
            "fighter_2_age": snapshot_2.get("age_at_fight_date"),
            "age_diff": _diff(snapshot_1.get("age_at_fight_date"), snapshot_2.get("age_at_fight_date")),
            "fighter_1_height": snapshot_1.get("height"),
            "fighter_2_height": snapshot_2.get("height"),
            "height_diff": _diff(snapshot_1.get("height"), snapshot_2.get("height")),
            "fighter_1_reach": snapshot_1.get("reach"),
            "fighter_2_reach": snapshot_2.get("reach"),
            "reach_diff": _diff(snapshot_1.get("reach"), snapshot_2.get("reach")),
            "fighter_1_stance_known": _known(snapshot_1.get("stance")),
            "fighter_2_stance_known": _known(snapshot_2.get("stance")),
            "fighter_1_history_count": _number(snapshot_1.get("total_fights_before"), 0),
            "fighter_2_history_count": _number(snapshot_2.get("total_fights_before"), 0),
            "minimum_history_count": min(_number(snapshot_1.get("total_fights_before"), 0), _number(snapshot_2.get("total_fights_before"), 0)),
            "fighter_1_win_rate_before": snapshot_1.get("win_rate_before"),
            "fighter_2_win_rate_before": snapshot_2.get("win_rate_before"),
            "win_rate_diff": _diff(snapshot_1.get("win_rate_before"), snapshot_2.get("win_rate_before")),
            "fighter_1_finish_win_rate_before": snapshot_1.get("finish_win_rate_before"),
            "fighter_2_finish_win_rate_before": snapshot_2.get("finish_win_rate_before"),
            "finish_rate_diff": _diff(snapshot_1.get("finish_win_rate_before"), snapshot_2.get("finish_win_rate_before")),
            "fighter_1_decision_win_rate_before": snapshot_1.get("decision_win_rate_before"),
            "fighter_2_decision_win_rate_before": snapshot_2.get("decision_win_rate_before"),
            "decision_rate_diff": _diff(snapshot_1.get("decision_win_rate_before"), snapshot_2.get("decision_win_rate_before")),
            "fighter_1_ko_tko_win_rate_before": snapshot_1.get("ko_tko_win_rate_before"),
            "fighter_2_ko_tko_win_rate_before": snapshot_2.get("ko_tko_win_rate_before"),
            "ko_tko_rate_diff": _diff(snapshot_1.get("ko_tko_win_rate_before"), snapshot_2.get("ko_tko_win_rate_before")),
            "fighter_1_submission_win_rate_before": snapshot_1.get("submission_win_rate_before"),
            "fighter_2_submission_win_rate_before": snapshot_2.get("submission_win_rate_before"),
            "submission_rate_diff": _diff(snapshot_1.get("submission_win_rate_before"), snapshot_2.get("submission_win_rate_before")),
            "fighter_1_finish_loss_rate_before": snapshot_1.get("finish_loss_rate_before"),
            "fighter_2_finish_loss_rate_before": snapshot_2.get("finish_loss_rate_before"),
            "fighter_1_decision_loss_rate_before": snapshot_1.get("decision_loss_rate_before"),
            "fighter_2_decision_loss_rate_before": snapshot_2.get("decision_loss_rate_before"),
            "fighter_1_recent_3_win_rate": snapshot_1.get("recent_3_win_rate"),
            "fighter_2_recent_3_win_rate": snapshot_2.get("recent_3_win_rate"),
            "recent_3_win_rate_diff": _diff(snapshot_1.get("recent_3_win_rate"), snapshot_2.get("recent_3_win_rate")),
            "fighter_1_recent_5_win_rate": snapshot_1.get("recent_5_win_rate"),
            "fighter_2_recent_5_win_rate": snapshot_2.get("recent_5_win_rate"),
            "recent_5_win_rate_diff": _diff(snapshot_1.get("recent_5_win_rate"), snapshot_2.get("recent_5_win_rate")),
            "fighter_1_recent_3_finish_rate": snapshot_1.get("recent_3_finish_rate"),
            "fighter_2_recent_3_finish_rate": snapshot_2.get("recent_3_finish_rate"),
            "fighter_1_recent_5_finish_rate": snapshot_1.get("recent_5_finish_rate"),
            "fighter_2_recent_5_finish_rate": snapshot_2.get("recent_5_finish_rate"),
            "fighter_1_days_since_last_fight": snapshot_1.get("days_since_last_fight"),
            "fighter_2_days_since_last_fight": snapshot_2.get("days_since_last_fight"),
            "days_since_last_fight_diff": _diff(snapshot_1.get("days_since_last_fight"), snapshot_2.get("days_since_last_fight")),
            "fighter_1_fights_last_12_months": snapshot_1.get("fights_last_12_months"),
            "fighter_2_fights_last_12_months": snapshot_2.get("fights_last_12_months"),
            "fighter_1_fights_last_24_months": snapshot_1.get("fights_last_24_months"),
            "fighter_2_fights_last_24_months": snapshot_2.get("fights_last_24_months"),
            "fighter_1_elo_before_fight": snapshot_1.get("elo_before_fight"),
            "fighter_2_elo_before_fight": snapshot_2.get("elo_before_fight"),
            "elo_diff": _diff(snapshot_1.get("elo_before_fight"), snapshot_2.get("elo_before_fight")),
            "elo_expected_fighter_1": _elo_expected(snapshot_1.get("elo_before_fight"), snapshot_2.get("elo_before_fight")),
            "fighter_1_elo_fights_count_before": snapshot_1.get("elo_fights_count_before"),
            "fighter_2_elo_fights_count_before": snapshot_2.get("elo_fights_count_before"),
            "fighter_1_elo_available": bool(snapshot_1.get("elo_available")),
            "fighter_2_elo_available": bool(snapshot_2.get("elo_available")),
            "scheduled_rounds": scheduled_rounds,
            "low_sample_warning": min(_number(snapshot_1.get("total_fights_before"), 0), _number(snapshot_2.get("total_fights_before"), 0)) < 3,
            "missing_profile_warning": _profile_missing(snapshot_1) or _profile_missing(snapshot_2),
            "missing_stats_warning": _stats_missing(snapshot_1) or _stats_missing(snapshot_2),
            "cross_division_warning": bool(size_context.get("warning")),
        }
    )
    _add_optional_stat_features(features, snapshot_1, snapshot_2)
    _add_style_weakness_features(features, snapshot_1, snapshot_2)
    features.update(
        {
            "same_division": size_context["same_division"],
            "cross_division": size_context["cross_division"],
            "catchweight": size_context["catchweight"],
            "weight_class_gap": size_context["weight_class_gap"],
            "estimated_weight_gap_lbs": size_context["estimated_weight_gap_lbs"],
            "height_gap": size_context["height_gap"],
            "reach_gap": size_context["reach_gap"],
            "unknown_size_context": size_context["unknown_size_context"],
            "size_context_quality": size_context["severity"],
            "pound_for_pound_mode": pound_for_pound,
            "size_features_used": size_context["size_features_used"],
        }
    )
    warnings = _warnings(features, snapshot_1, snapshot_2, size_context)
    validation = validate_feature_set(features, schema.model_family)
    availability = summarize_feature_availability(features, schema)
    return MatchupFeatureSet(
        features=features,
        feature_schema_name=schema.schema_name,
        feature_schema_version=schema.schema_version,
        model_family=schema.model_family,
        mode=mode,
        feature_mode=feature_mode,
        missing_features=availability["missing_required_features"],
        unavailable_features=availability["missing_optional_features"],
        estimated_features=_estimated_features(features),
        leakage_excluded_features=validation["leakage_columns_found"],
        data_quality_warnings=warnings,
        validation=validation,
        model_feature_coverage=availability,
    )


def validate_feature_set(features: dict[str, Any], model_family: str = "winner") -> dict[str, Any]:
    schema = get_feature_schema(model_family)
    feature_names = set(features)
    forbidden = sorted(feature_names & set(schema.forbidden_features))
    unknown = sorted(feature_names - set(schema.all_features()))
    missing_required = [name for name in schema.required_features if name not in features]
    scan = scan_dataframe(pd.DataFrame([features]), allowlist=schema.all_features(), denylist=schema.forbidden_features)
    leakage = sorted(set(forbidden + scan.get("blocked_feature_columns", [])))
    return {
        "valid": not leakage and not missing_required,
        "schema_name": schema.schema_name,
        "schema_version": schema.schema_version,
        "leakage_columns_found": leakage,
        "unknown_columns": unknown,
        "missing_required_columns": missing_required,
        "warnings": _validation_warnings(unknown, missing_required),
    }


def _empty_features(schema: FeatureSchema) -> dict[str, Any]:
    return {name: None for name in schema.all_features()}


def _add_optional_stat_features(features: dict[str, Any], s1: dict[str, Any], s2: dict[str, Any]) -> None:
    pairs = {
        "avg_sig_strikes_landed_before": "sig_strike_landed_avg_diff",
        "avg_sig_strikes_absorbed_before": "sig_strike_absorbed_avg_diff",
        "avg_takedowns_landed_before": "takedown_avg_diff",
        "avg_control_time_before": "control_time_avg_diff",
    }
    for key, diff_key in pairs.items():
        _set_if_declared(features, f"fighter_1_{key}", s1.get(key))
        _set_if_declared(features, f"fighter_2_{key}", s2.get(key))
        _set_if_declared(features, diff_key, _diff(s1.get(key), s2.get(key)))
    for key in [
        "avg_sig_strike_attempts_before",
        "sig_strike_accuracy_before",
        "sig_strike_defense_before",
        "recent_3_sig_strikes_landed_avg",
        "recent_5_sig_strikes_landed_avg",
        "avg_takedowns_attempted_before",
        "takedown_accuracy_before",
        "takedown_defense_before",
        "avg_submission_attempts_before",
        "recent_3_takedowns_avg",
        "recent_5_takedowns_avg",
    ]:
        _set_if_declared(features, f"fighter_1_{key}", s1.get(key))
        _set_if_declared(features, f"fighter_2_{key}", s2.get(key))


def _add_style_weakness_features(features: dict[str, Any], s1: dict[str, Any], s2: dict[str, Any]) -> None:
    keys = [
        "striker_score",
        "high_volume_striker_score",
        "power_finisher_score",
        "wrestler_score",
        "grappler_score",
        "submission_threat_score",
        "control_fighter_score",
        "high_pace_score",
        "durability_score",
        "decision_tendency_score",
        "early_finish_threat_score",
        "low_volume_control_score",
        "volatility_score",
        "strike_absorption_weakness",
        "low_defensive_volume_weakness",
        "takedown_defense_weakness_proxy",
        "submission_defense_weakness_proxy",
        "grappling_exposure_weakness",
        "control_vulnerability_proxy",
        "durability_weakness",
        "early_finish_vulnerability",
        "low_activity_weakness",
        "poor_recent_form_weakness",
        "pace_breakdown_risk",
        "cardio_late_fight_risk_proxy",
    ]
    for key in keys:
        _set_if_declared(features, f"fighter_1_{key}", s1.get(key))
        _set_if_declared(features, f"fighter_2_{key}", s2.get(key))
        _set_if_declared(features, f"{key}_diff", _diff(s1.get(key), s2.get(key)))


def _set_if_declared(features: dict[str, Any], key: str, value) -> None:
    if key in features:
        features[key] = value


def _size_profile(snapshot: dict[str, Any], matchup_weight_class: str | None) -> dict[str, Any]:
    weight_class = matchup_weight_class or snapshot.get("current_or_matchup_weight_class") or snapshot.get("usual_weight_class")
    return {
        "weight_class": weight_class,
        "height_cm": snapshot.get("height"),
        "reach_cm": snapshot.get("reach"),
        "age": snapshot.get("age_at_fight_date"),
    }


def _rate_count(snapshot: dict[str, Any], rate_key: str, count_key: str) -> int:
    rate = _number(snapshot.get(rate_key), None)
    count = _number(snapshot.get(count_key), 0)
    if rate is None:
        return 0
    return int(round(rate * count))


def _diff(left, right):
    left_number = _number(left, None)
    right_number = _number(right, None)
    if left_number is None or right_number is None:
        return None
    return round(left_number - right_number, 4)


def _elo_expected(elo_1, elo_2) -> float | None:
    left = _number(elo_1, None)
    right = _number(elo_2, None)
    if left is None or right is None:
        return None
    return round(1 / (1 + 10 ** ((right - left) / 400)), 6)


def _number(value, default=0):
    if value is None or value == "":
        return default
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(number):
        return default
    return number


def _safe_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _known(value) -> bool:
    return bool(value is not None and str(value).strip() and str(value).strip().lower() not in {"n/a", "unknown", "nan"})


def _profile_missing(snapshot: dict[str, Any]) -> bool:
    return not snapshot.get("height") or not snapshot.get("reach") or not snapshot.get("usual_weight_class")


def _stats_missing(snapshot: dict[str, Any]) -> bool:
    keys = [
        "avg_sig_strikes_landed_before",
        "avg_takedowns_landed_before",
        "avg_control_time_before",
    ]
    return all(snapshot.get(key) is None for key in keys)


def _estimated_features(features: dict[str, Any]) -> list[str]:
    estimated = []
    if features.get("unknown_size_context"):
        estimated.extend(["weight_class_gap", "estimated_weight_gap_lbs"])
    return estimated


def _warnings(features: dict[str, Any], snapshot_1: dict[str, Any], snapshot_2: dict[str, Any], size_context: dict[str, Any]) -> list[str]:
    warnings = []
    if features.get("low_sample_warning"):
        warnings.append("One or both fighters have limited prior fight history.")
    if features.get("missing_profile_warning"):
        warnings.append("Profile size data is incomplete for one or both fighters.")
    if features.get("missing_stats_warning"):
        warnings.append("Detailed strike/grappling history is incomplete; optional style features are unavailable.")
    if size_context.get("warning"):
        warnings.append(size_context["warning"])
    if not snapshot_1.get("elo_available") or not snapshot_2.get("elo_available"):
        warnings.append("Computed Elo is missing for one or both fighters.")
    return list(dict.fromkeys(warnings))


def _validation_warnings(unknown: list[str], missing_required: list[str]) -> list[str]:
    warnings = []
    if unknown:
        warnings.append("Feature set contains columns not declared in the active schema.")
    if missing_required:
        warnings.append("Feature set is missing required model inputs.")
    return warnings


def feature_schema_for_model(model_family: str) -> dict[str, Any]:
    return get_feature_schema(normalize_model_family(model_family)).to_dict()
