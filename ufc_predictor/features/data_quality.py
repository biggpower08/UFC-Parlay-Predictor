"""Matchup-level data-quality scoring for selective prediction policies."""

from __future__ import annotations

from typing import Any


def score_matchup_data_quality(features: dict[str, Any], model_statuses: dict[str, str] | None = None) -> dict[str, Any]:
    model_statuses = model_statuses or {}
    reasons: list[str] = []
    severity = 0

    minimum_history = _number(features.get("minimum_history_count"), 0)
    if minimum_history <= 0:
        severity += 4
        reasons.append("debutant_or_no_prior_history")
    elif minimum_history < 3:
        severity += 2
        reasons.append("low_fighter_history")

    if features.get("missing_profile_warning"):
        severity += 1
        reasons.append("missing_reach_height_or_stance")
    if features.get("missing_stats_warning"):
        severity += 2
        reasons.append("missing_strike_takedown_control_history")
    if features.get("cross_division_warning") or features.get("cross_division"):
        severity += 2
        reasons.append("cross_division_or_catchweight_context")
    if features.get("unknown_size_context"):
        severity += 1
        reasons.append("unknown_weight_class_or_size_context")
    if not features.get("fighter_1_elo_available") or not features.get("fighter_2_elo_available"):
        severity += 1
        reasons.append("computed_elo_missing_for_one_or_both_fighters")
    if model_statuses.get("winner_model") in {"blocked", "not_trained", "weak_or_failed_baseline"}:
        severity += 3
        reasons.append("winner_model_not_available_for_matchup")
    if model_statuses.get("odds_calibration_model") in {"blocked", "not_trained", None}:
        reasons.append("no_trusted_odds_calibration")

    label = "strong"
    if severity >= 6:
        label = "dangerous"
    elif severity >= 3:
        label = "limited"
    elif severity >= 1:
        label = "medium"

    hidden = [
        name
        for name, status in model_statuses.items()
        if status in {"blocked", "not_trained", "weak_or_failed_baseline"}
    ]
    allowed = [
        name
        for name, status in model_statuses.items()
        if status in {"production_ready", "production_candidate", "high_confidence_only", "experimental"}
    ]
    return {
        "data_quality": label,
        "score": severity,
        "warning_reasons": list(dict.fromkeys(reasons)),
        "models_allowed_for_matchup": sorted(set(allowed)),
        "models_hidden_or_context_only": sorted(set(hidden)),
    }


def _number(value, default=0):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return default if number != number else number
