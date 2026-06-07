"""Time-aware fighter snapshots for training and live matchup features."""

from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import normalize_name, safe_float
from ufc_predictor.utils.weight_classes import detect_weight_class


def build_fighter_snapshot(
    fighter: str | dict | pd.Series,
    fights: pd.DataFrame | None = None,
    as_of_date: str | datetime | pd.Timestamp | None = None,
    profile: dict | pd.Series | None = None,
) -> dict[str, Any]:
    """Build a fighter state snapshot using only fights before as_of_date."""

    profile_dict = _profile_dict(profile if profile is not None else fighter)
    name = _fighter_name(fighter, profile_dict)
    key = normalize_name(name)
    history = _history_before(key, fights, as_of_date)
    snapshot = {
        "fighter_name": name,
        "normalized_name": key,
        "as_of_date": _date_string(as_of_date),
        **_profile_features(profile_dict, as_of_date),
        **history,
    }
    _fill_profile_record_fallbacks(snapshot, profile_dict)
    return snapshot


def empty_fighter_snapshot(name: str = "Unknown") -> dict[str, Any]:
    return build_fighter_snapshot({"name": name}, fights=None)


def _history_before(normalized_name: str, fights: pd.DataFrame | None, as_of_date) -> dict[str, Any]:
    base = _empty_history()
    if fights is None or fights.empty or not normalized_name:
        return base
    rows = fights.copy()
    rows["_event_date"] = pd.to_datetime(rows.get("event_date"), errors="coerce") if "event_date" in rows.columns else pd.NaT
    cutoff = pd.to_datetime(as_of_date, errors="coerce") if as_of_date is not None else pd.NaT
    if not pd.isna(cutoff) and "_event_date" in rows.columns:
        rows = rows[rows["_event_date"].isna() | (rows["_event_date"] < cutoff)]
    rows["_source_order"] = range(len(rows))
    rows = rows.sort_values(["_event_date", "_source_order"], na_position="last")

    fight_summaries = []
    for _, row in rows.iterrows():
        side = _fighter_side(row, normalized_name)
        if not side:
            continue
        summary = _fight_summary(row, side)
        if summary is None:
            continue
        fight_summaries.append(summary)
    if not fight_summaries:
        return base
    return _summarize_history(fight_summaries, as_of_date)


def _empty_history() -> dict[str, Any]:
    return {
        "wins_before": 0,
        "losses_before": 0,
        "draws_before": 0,
        "no_contests_before": 0,
        "total_fights_before": 0,
        "win_rate_before": None,
        "finish_win_rate_before": None,
        "decision_win_rate_before": None,
        "ko_tko_win_rate_before": None,
        "submission_win_rate_before": None,
        "finish_loss_rate_before": None,
        "decision_loss_rate_before": None,
        "recent_3_win_rate": None,
        "recent_5_win_rate": None,
        "recent_3_finish_rate": None,
        "recent_5_finish_rate": None,
        "days_since_last_fight": None,
        "fights_last_12_months": None,
        "fights_last_24_months": None,
        "avg_sig_strikes_landed_before": None,
        "avg_sig_strikes_absorbed_before": None,
        "avg_sig_strike_attempts_before": None,
        "sig_strike_accuracy_before": None,
        "sig_strike_defense_before": None,
        "recent_3_sig_strikes_landed_avg": None,
        "recent_5_sig_strikes_landed_avg": None,
        "avg_takedowns_landed_before": None,
        "avg_takedowns_attempted_before": None,
        "takedown_accuracy_before": None,
        "takedown_defense_before": None,
        "avg_control_time_before": None,
        "avg_submission_attempts_before": None,
        "recent_3_takedowns_avg": None,
        "recent_5_takedowns_avg": None,
    }


def _summarize_history(fights: list[dict[str, Any]], as_of_date) -> dict[str, Any]:
    wins = sum(1 for fight in fights if fight["result"] == "win")
    losses = sum(1 for fight in fights if fight["result"] == "loss")
    draws = sum(1 for fight in fights if fight["result"] == "draw")
    no_contests = sum(1 for fight in fights if fight["result"] == "nc")
    completed = [fight for fight in fights if fight["result"] in {"win", "loss", "draw"}]
    win_fights = [fight for fight in fights if fight["result"] == "win"]
    loss_fights = [fight for fight in fights if fight["result"] == "loss"]
    total = len(completed)
    recent_3 = completed[-3:]
    recent_5 = completed[-5:]
    cutoff = pd.to_datetime(as_of_date, errors="coerce") if as_of_date is not None else pd.NaT
    dated = [fight for fight in fights if fight.get("event_date") is not None]
    last_date = max((fight["event_date"] for fight in dated), default=None)
    return {
        "wins_before": wins,
        "losses_before": losses,
        "draws_before": draws,
        "no_contests_before": no_contests,
        "total_fights_before": total,
        "win_rate_before": _rate(wins, total),
        "finish_win_rate_before": _rate(sum(1 for fight in win_fights if not fight["is_decision"]), len(win_fights)),
        "decision_win_rate_before": _rate(sum(1 for fight in win_fights if fight["is_decision"]), len(win_fights)),
        "ko_tko_win_rate_before": _rate(sum(1 for fight in win_fights if fight["method"] == "KO/TKO"), len(win_fights)),
        "submission_win_rate_before": _rate(sum(1 for fight in win_fights if fight["method"] == "Submission"), len(win_fights)),
        "finish_loss_rate_before": _rate(sum(1 for fight in loss_fights if not fight["is_decision"]), len(loss_fights)),
        "decision_loss_rate_before": _rate(sum(1 for fight in loss_fights if fight["is_decision"]), len(loss_fights)),
        "recent_3_win_rate": _rate(sum(1 for fight in recent_3 if fight["result"] == "win"), len(recent_3)),
        "recent_5_win_rate": _rate(sum(1 for fight in recent_5 if fight["result"] == "win"), len(recent_5)),
        "recent_3_finish_rate": _rate(sum(1 for fight in recent_3 if fight["result"] == "win" and not fight["is_decision"]), len(recent_3)),
        "recent_5_finish_rate": _rate(sum(1 for fight in recent_5 if fight["result"] == "win" and not fight["is_decision"]), len(recent_5)),
        "days_since_last_fight": _days_between(last_date, cutoff),
        "fights_last_12_months": _fights_since(dated, cutoff, 365),
        "fights_last_24_months": _fights_since(dated, cutoff, 730),
        "avg_sig_strikes_landed_before": _avg(fights, "sig_strikes_landed"),
        "avg_sig_strikes_absorbed_before": _avg(fights, "sig_strikes_absorbed"),
        "avg_sig_strike_attempts_before": _avg(fights, "sig_strike_attempts"),
        "sig_strike_accuracy_before": _rate(_sum(fights, "sig_strikes_landed"), _sum(fights, "sig_strike_attempts")),
        "sig_strike_defense_before": _defense_rate(fights, "opponent_sig_strike_attempts", "sig_strikes_absorbed"),
        "recent_3_sig_strikes_landed_avg": _avg(recent_3, "sig_strikes_landed"),
        "recent_5_sig_strikes_landed_avg": _avg(recent_5, "sig_strikes_landed"),
        "avg_takedowns_landed_before": _avg(fights, "takedowns_landed"),
        "avg_takedowns_attempted_before": _avg(fights, "takedowns_attempted"),
        "takedown_accuracy_before": _rate(_sum(fights, "takedowns_landed"), _sum(fights, "takedowns_attempted")),
        "takedown_defense_before": _defense_rate(fights, "opponent_takedowns_attempted", "opponent_takedowns_landed"),
        "avg_control_time_before": _avg(fights, "control_time_seconds"),
        "avg_submission_attempts_before": _avg(fights, "submission_attempts"),
        "recent_3_takedowns_avg": _avg(recent_3, "takedowns_landed"),
        "recent_5_takedowns_avg": _avg(recent_5, "takedowns_landed"),
    }


def _fight_summary(row: pd.Series, side: str) -> dict[str, Any] | None:
    method = _normalize_method(row.get("method_group") or row.get("method"))
    result = _result_for_side(row, side)
    if result is None:
        return None
    prefix = "fighter_a" if side == "fighter_1" else "fighter_b"
    opponent_prefix = "fighter_b" if side == "fighter_1" else "fighter_a"
    return {
        "event_date": _timestamp_or_none(_first_present(row, ["_event_date", "event_date"])),
        "result": result,
        "method": method,
        "is_decision": method == "Decision",
        "sig_strikes_landed": _number(row.get(f"{prefix}_sig_strikes")),
        "sig_strikes_absorbed": _number(row.get(f"{opponent_prefix}_sig_strikes")),
        "sig_strike_attempts": _number(row.get(f"{prefix}_sig_strikes_attempted")),
        "opponent_sig_strike_attempts": _number(row.get(f"{opponent_prefix}_sig_strikes_attempted")),
        "takedowns_landed": _number(row.get(f"{prefix}_takedowns")),
        "takedowns_attempted": _number(row.get(f"{prefix}_takedowns_attempted")),
        "opponent_takedowns_landed": _number(row.get(f"{opponent_prefix}_takedowns")),
        "opponent_takedowns_attempted": _number(row.get(f"{opponent_prefix}_takedowns_attempted")),
        "control_time_seconds": _number(row.get(f"{prefix}_control_time_seconds")),
        "submission_attempts": _number(row.get(f"{prefix}_submission_attempts")),
    }


def _result_for_side(row: pd.Series, side: str) -> str | None:
    raw = str(row.get("result") or "").strip().lower()
    if raw in {"draw", "d"}:
        return "draw"
    if raw in {"nc", "no contest", "no-contest"}:
        return "nc"
    winner = normalize_name(row.get("winner_name") or row.get("winner") or "")
    fighter_name = normalize_name(row.get(side) or "")
    opponent_side = "fighter_2" if side == "fighter_1" else "fighter_1"
    opponent_name = normalize_name(row.get(opponent_side) or "")
    if winner:
        if winner == fighter_name:
            return "win"
        if winner == opponent_name:
            return "loss"
    if raw == "win":
        return "win" if side == "fighter_1" else "loss"
    return None


def _fighter_side(row: pd.Series, normalized_name: str) -> str | None:
    if normalize_name(row.get("fighter_1") or row.get("fighter_a") or "") == normalized_name:
        return "fighter_1"
    if normalize_name(row.get("fighter_2") or row.get("fighter_b") or "") == normalized_name:
        return "fighter_2"
    return None


def _profile_features(profile: dict[str, Any], as_of_date) -> dict[str, Any]:
    dob = _timestamp_or_none(profile.get("date_of_birth") or profile.get("dob"))
    cutoff = _timestamp_or_none(as_of_date)
    age = None
    if dob is not None and cutoff is not None:
        age = round((cutoff - dob).days / 365.25, 2)
    return {
        "age_at_fight_date": age if age is not None else _optional_number(profile.get("age") or profile.get("Age")),
        "height": _first_number(profile, ["height_cm", "height_in_cm", "Height (cm)", "height"]),
        "reach": _first_number(profile, ["reach_cm", "reach_in_cm", "Reach (cm)", "reach"]),
        "stance": _first_text(profile, ["stance", "Stance"]),
        "usual_weight_class": _first_text(profile, ["weight_class", "Weight Class", "division"]) or _detect_weight_class(profile),
        "current_or_matchup_weight_class": _first_text(profile, ["matchup_weight_class", "weight_class", "Weight Class", "division"]) or _detect_weight_class(profile),
        "elo_before_fight": _optional_number(profile.get("elo") or profile.get("Elo")),
        "elo_fights_count_before": int(_optional_number(profile.get("elo_fights_count") or profile.get("Elo Fights")) or 0),
        "elo_source": str(profile.get("elo_source") or profile.get("Elo Source") or "baseline"),
        "elo_available": bool(profile.get("elo_available") or profile.get("Elo Available") or str(profile.get("elo_source") or "").lower() == "computed"),
    }


def _fill_profile_record_fallbacks(snapshot: dict[str, Any], profile: dict[str, Any]) -> None:
    if snapshot["total_fights_before"] > 0:
        return
    wins = _optional_number(profile.get("wins") or profile.get("win"))
    losses = _optional_number(profile.get("losses") or profile.get("loss"))
    draws = _optional_number(profile.get("draws") or profile.get("draw"))
    if wins is None and losses is None:
        return
    wins = int(wins or 0)
    losses = int(losses or 0)
    draws = int(draws or 0)
    total = wins + losses + draws
    snapshot["wins_before"] = wins
    snapshot["losses_before"] = losses
    snapshot["draws_before"] = draws
    snapshot["total_fights_before"] = total
    snapshot["win_rate_before"] = _rate(wins, total)


def _profile_dict(value) -> dict[str, Any]:
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, dict):
        return dict(value)
    if isinstance(value, str):
        return {"name": value}
    return {}


def _fighter_name(fighter, profile: dict[str, Any]) -> str:
    if isinstance(fighter, str):
        return fighter
    if isinstance(fighter, pd.Series):
        profile = fighter.to_dict()
    if isinstance(fighter, dict):
        profile = {**fighter, **profile}
    return str(profile.get("name") or profile.get("Name") or profile.get("fighter_name") or profile.get("fighter") or "Unknown")


def _first_number(profile: dict[str, Any], keys: list[str]) -> float | None:
    for key in keys:
        value = _optional_number(profile.get(key))
        if value is not None:
            return value
    return None


def _first_present(row: pd.Series, keys: list[str]):
    for key in keys:
        value = row.get(key)
        if value is not None and not pd.isna(value):
            return value
    return None


def _first_text(profile: dict[str, Any], keys: list[str]) -> str | None:
    for key in keys:
        value = profile.get(key)
        if value is not None and not pd.isna(value) and str(value).strip():
            return str(value).strip()
    return None


def _detect_weight_class(profile: dict[str, Any]) -> str | None:
    try:
        return detect_weight_class(pd.Series(profile))
    except Exception:  # noqa: BLE001 - profile shape is intentionally flexible.
        return None


def _rate(numerator, denominator) -> float | None:
    numerator = _optional_number(numerator)
    denominator = _optional_number(denominator)
    if denominator is None or denominator <= 0 or numerator is None:
        return None
    return round(float(numerator) / float(denominator), 4)


def _avg(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [_optional_number(row.get(key)) for row in rows]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _sum(rows: list[dict[str, Any]], key: str) -> float | None:
    values = [_optional_number(row.get(key)) for row in rows]
    values = [value for value in values if value is not None]
    if not values:
        return None
    return sum(values)


def _defense_rate(rows: list[dict[str, Any]], attempts_key: str, landed_key: str) -> float | None:
    attempts = _sum(rows, attempts_key)
    landed = _sum(rows, landed_key)
    if attempts is None or landed is None:
        return None
    return _rate(max(0, attempts - landed), attempts)


def _number(value) -> float | None:
    return _optional_number(value)


def _optional_number(value) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = safe_float(value)
    except Exception:  # noqa: BLE001
        return None
    if pd.isna(number):
        return None
    return float(number)


def _timestamp_or_none(value):
    if value is None or pd.isna(value):
        return None
    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return None
    return pd.Timestamp(timestamp)


def _date_string(value) -> str | None:
    timestamp = _timestamp_or_none(value)
    return str(timestamp.date()) if timestamp is not None else None


def _days_between(start, end) -> int | None:
    if start is None or end is None or pd.isna(end):
        return None
    return int((end - start).days)


def _fights_since(fights: list[dict[str, Any]], cutoff, days: int) -> int | None:
    if cutoff is None or pd.isna(cutoff):
        return None
    return sum(1 for fight in fights if fight.get("event_date") is not None and 0 <= (cutoff - fight["event_date"]).days <= days)


def _normalize_method(value) -> str:
    method = str(value or "").strip().lower()
    if "dec" in method:
        return "Decision"
    if "sub" in method:
        return "Submission"
    if "ko" in method or "tko" in method:
        return "KO/TKO"
    return "Other"
