"""Pre-fight MMA style scores derived only from prior fighter history."""

from __future__ import annotations

from typing import Any


def compute_style_scores(history: dict[str, Any]) -> dict[str, float | None]:
    """Return transparent 0-1 style scores from accumulated pre-fight history."""
    fights = int(history.get("fights", 0) or 0)
    wins = int(history.get("wins", 0) or 0)
    losses = int(history.get("losses", 0) or 0)
    if fights <= 0:
        return {}

    avg_sig_for = _avg(history, "sig_landed_for", fights)
    avg_attempts = _avg(history, "sig_attempted_for", fights)
    avg_td_for = _avg(history, "takedowns_for", fights)
    avg_control_for = _avg(history, "control_for_seconds", fights)
    finish_rate = _rate(int(history.get("finishes", 0) or 0), wins) or 0.0
    ko_rate = _rate(int(history.get("ko_tko_wins", 0) or 0), wins) or 0.0
    sub_rate = _rate(int(history.get("submission_wins", 0) or 0), wins) or 0.0
    finish_loss_rate = _rate(int(history.get("finish_losses", 0) or 0), losses) or 0.0
    decision_rate = _rate(int(history.get("decisions", 0) or 0), wins) or 0.0
    early_finish_rate = _rate(int(history.get("early_finishes", 0) or 0), wins) or 0.0
    control_score = _clip01(avg_control_for / 300.0)
    high_pace = _clip01((avg_attempts / 90.0 + avg_td_for / 3.0) / 2.0)
    return {
        "striker_score": _clip01(avg_sig_for / 50.0),
        "high_volume_striker_score": _clip01(avg_attempts / 90.0),
        "power_finisher_score": _clip01((finish_rate + ko_rate) / 2.0),
        "wrestler_score": _clip01(avg_td_for / 3.0),
        "grappler_score": _clip01((avg_td_for / 3.0 + avg_control_for / 300.0 + sub_rate) / 3.0),
        "submission_threat_score": _clip01(sub_rate),
        "control_fighter_score": control_score,
        "high_pace_score": high_pace,
        "durability_score": _clip01(1.0 - finish_loss_rate),
        "decision_tendency_score": _clip01(decision_rate),
        "early_finish_threat_score": _clip01(early_finish_rate),
        "low_volume_control_score": _clip01(control_score * (1.0 - _clip01(avg_sig_for / 50.0))),
        "volatility_score": _clip01((finish_rate + finish_loss_rate + early_finish_rate) / 3.0),
        "avg_sig_strikes_landed_before": round(avg_sig_for, 4),
        "avg_sig_strike_attempts_before": round(avg_attempts, 4),
        "avg_takedowns_landed_before": round(avg_td_for, 4),
        "avg_takedowns_attempted_before": round(_avg(history, "takedowns_attempted_for", fights), 4),
        "avg_control_time_before": round(avg_control_for, 4),
    }


def _avg(history: dict[str, Any], key: str, fights: int) -> float:
    return float(history.get(key, 0.0) or 0.0) / max(1, fights)


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return float(numerator) / float(denominator)


def _clip01(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return round(max(0.0, min(1.0, number)), 4)
