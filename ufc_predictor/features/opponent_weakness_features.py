"""Pre-fight opponent weakness proxies derived only from prior fighter history."""

from __future__ import annotations

from typing import Any


def compute_opponent_weakness_scores(history: dict[str, Any]) -> dict[str, float | None]:
    """Return 0-1 weakness proxies from prior fight history.

    These are intentionally labeled as proxies where the underlying data does
    not directly contain defensive events such as submission attempts allowed.
    """
    fights = int(history.get("fights", 0) or 0)
    losses = int(history.get("losses", 0) or 0)
    if fights <= 0:
        return {}

    avg_sig_against = _avg(history, "sig_landed_against", fights)
    avg_td_against = _avg(history, "takedowns_against", fights)
    avg_td_attempts_against = _avg(history, "takedowns_attempted_against", fights)
    avg_control_against = _avg(history, "control_against_seconds", fights)
    finish_loss_rate = _rate(int(history.get("finish_losses", 0) or 0), losses) or 0.0
    recent_win_rate = _recent_rate(list(history.get("recent_results", [])), 5)
    poor_recent = 1.0 - recent_win_rate if recent_win_rate is not None else None
    low_activity = 1.0 - min(1.0, fights / 8.0)
    return {
        "avg_sig_strikes_absorbed_before": round(avg_sig_against, 4),
        "strike_absorption_weakness": _clip01(avg_sig_against / 50.0),
        "low_defensive_volume_weakness": _clip01((avg_sig_against / 50.0 + low_activity) / 2.0),
        "takedown_defense_weakness_proxy": _clip01(avg_td_against / max(1.0, avg_td_attempts_against)),
        "control_vulnerability_proxy": _clip01(avg_control_against / 300.0),
        "submission_defense_weakness_proxy": _clip01(finish_loss_rate),
        "grappling_exposure_weakness": _clip01((avg_td_against / 3.0 + avg_control_against / 300.0) / 2.0),
        "durability_weakness": _clip01(finish_loss_rate),
        "early_finish_vulnerability": _clip01(_rate(int(history.get("early_finish_losses", 0) or 0), losses) or finish_loss_rate),
        "low_activity_weakness": _clip01(low_activity),
        "poor_recent_form_weakness": _clip01(poor_recent) if poor_recent is not None else None,
        "pace_breakdown_risk": _clip01((low_activity + (poor_recent or 0.0) + avg_sig_against / 50.0) / 3.0),
        "cardio_late_fight_risk_proxy": _clip01((low_activity + avg_control_against / 300.0) / 2.0),
    }


def _avg(history: dict[str, Any], key: str, fights: int) -> float:
    return float(history.get(key, 0.0) or 0.0) / max(1, fights)


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return float(numerator) / float(denominator)


def _recent_rate(values: list[Any], limit: int) -> float | None:
    recent = [value for value in values[-limit:] if value is not None]
    if not recent:
        return None
    return float(sum(recent)) / len(recent)


def _clip01(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(max(0.0, min(1.0, number)), 4)
