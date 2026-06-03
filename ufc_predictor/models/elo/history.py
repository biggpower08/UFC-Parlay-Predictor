"""Fight-by-fight Elo history helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import normalize_name


def build_elo_fight_history_rows(
    fights_elo: pd.DataFrame,
    elo_version: str | None = None,
    computed_at: str | None = None,
    include_no_change: bool = False,
) -> list[dict]:
    """Convert Elo trace fights into one history row per fighter per tracked fight.

    No-contests and unknown results are skipped by default because they do not
    change ratings and should not count as Elo-tracked fights.
    """
    if fights_elo is None or fights_elo.empty:
        return []

    version = elo_version or settings.ELO_ENGINE_VERSION
    timestamp = computed_at or datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for _, fight in fights_elo.iterrows():
        result_type = str(fight.get("elo_result_type", "")).lower().strip()
        if result_type == "no_change" and not include_no_change:
            continue

        fighter_1 = fight.get("fighter_1")
        fighter_2 = fight.get("fighter_2")
        if not _has_value(fighter_1) or not _has_value(fighter_2):
            continue

        fighter_1_result, fighter_2_result = _per_fighter_results(fight)
        shared = {
            "event": _optional_text(fight.get("event")),
            "event_date": _optional_date(fight.get("event_date")),
            "fight_id": _optional_text(fight.get("fight_id") if _has_value(fight.get("fight_id")) else fight.get("id")),
            "source_hash": _optional_text(fight.get("source_hash")),
            "weight_class": _optional_text(fight.get("weight_class")),
            "method": _optional_text(fight.get("method")),
            "round": _optional_text(fight.get("round")),
            "elo_version": version,
            "order_source": _optional_text(fight.get("elo_order_source")) or "source_order_inferred",
            "computed_at": timestamp,
        }

        rows.append(
            {
                **shared,
                "fighter_name": str(fighter_1),
                "normalized_name": normalize_name(fighter_1),
                "opponent_name": str(fighter_2),
                "opponent_normalized_name": normalize_name(fighter_2),
                "result": fighter_1_result,
                "elo_before": _float_or_none(fight.get("fighter_1_elo_start")),
                "elo_after": _float_or_none(fight.get("fighter_1_elo_end")),
                "elo_change": _float_or_none(fight.get("fighter_1_elo_change")),
                "opponent_elo_before": _float_or_none(fight.get("fighter_2_elo_start")),
                "expected_score": _float_or_none(fight.get("elo_expected_fighter_1")),
            }
        )
        rows.append(
            {
                **shared,
                "fighter_name": str(fighter_2),
                "normalized_name": normalize_name(fighter_2),
                "opponent_name": str(fighter_1),
                "opponent_normalized_name": normalize_name(fighter_1),
                "result": fighter_2_result,
                "elo_before": _float_or_none(fight.get("fighter_2_elo_start")),
                "elo_after": _float_or_none(fight.get("fighter_2_elo_end")),
                "elo_change": _float_or_none(fight.get("fighter_2_elo_change")),
                "opponent_elo_before": _float_or_none(fight.get("fighter_1_elo_start")),
                "expected_score": _float_or_none(fight.get("elo_expected_fighter_2")),
            }
        )

    return rows


def summarize_elo_trend(
    history_rows: list[dict],
    current_elo: float | None = None,
    peak_elo: float | None = None,
    elo_fights_count: int | None = None,
    elo_version: str | None = None,
) -> dict:
    """Build a small trend summary from chronological per-fight history rows."""
    version = elo_version or settings.ELO_ENGINE_VERSION
    rows = sorted(history_rows or [], key=_history_sort_key)
    if not rows:
        trend = "baseline" if (elo_fights_count or 0) == 0 else "unavailable"
        return {
            "current_elo": _round_or_none(current_elo),
            "peak_elo": _round_or_none(peak_elo),
            "elo_fights_count": int(elo_fights_count or 0),
            "last_elo_change": None,
            "last_3_change": None,
            "last_5_change": None,
            "trend": trend,
            "biggest_gain": None,
            "biggest_loss": None,
            "last_fight_date": None,
            "elo_version": version,
        }

    changes = [_safe_float(row.get("elo_change"), 0.0) for row in rows]
    last_3_change = round(sum(changes[-3:]), 2)
    last_5_change = round(sum(changes[-5:]), 2)
    recent_change = last_5_change if len(rows) >= 5 else last_3_change
    trend = "stable"
    if recent_change >= 5:
        trend = "rising"
    elif recent_change <= -5:
        trend = "falling"

    final_row = rows[-1]
    return {
        "current_elo": _round_or_none(current_elo if current_elo is not None else final_row.get("elo_after")),
        "peak_elo": _round_or_none(peak_elo if peak_elo is not None else max(_safe_float(row.get("elo_after"), 0.0) for row in rows)),
        "elo_fights_count": int(elo_fights_count if elo_fights_count is not None else len(rows)),
        "last_elo_change": round(changes[-1], 2),
        "last_3_change": last_3_change,
        "last_5_change": last_5_change,
        "trend": trend,
        "biggest_gain": _compact_history_row(max(rows, key=lambda row: _safe_float(row.get("elo_change"), 0.0))),
        "biggest_loss": _compact_history_row(min(rows, key=lambda row: _safe_float(row.get("elo_change"), 0.0))),
        "last_fight_date": _optional_text(final_row.get("event_date")),
        "elo_version": version,
    }


def _per_fighter_results(fight: pd.Series) -> tuple[str, str]:
    result_type = str(fight.get("elo_result_type", "")).lower().strip()
    if result_type == "draw":
        return "draw", "draw"
    if result_type == "win":
        fighter_1_change = _safe_float(fight.get("fighter_1_elo_change"), 0.0)
        fighter_2_change = _safe_float(fight.get("fighter_2_elo_change"), 0.0)
        if fighter_2_change > fighter_1_change:
            return "loss", "win"
        return "win", "loss"
    return "nc", "nc"


def _compact_history_row(row: dict) -> dict:
    return {
        "event": row.get("event"),
        "event_date": row.get("event_date"),
        "opponent_name": row.get("opponent_name"),
        "result": row.get("result"),
        "elo_change": _round_or_none(row.get("elo_change")),
        "elo_after": _round_or_none(row.get("elo_after")),
    }


def _history_sort_key(row: dict) -> tuple[str, str]:
    return (_optional_text(row.get("event_date")) or "", _optional_text(row.get("id")) or "")


def _optional_text(value: Any) -> str | None:
    if not _has_value(value):
        return None
    return str(value)


def _optional_date(value: Any) -> str | None:
    if not _has_value(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return str(parsed.date())


def _float_or_none(value: Any) -> float | None:
    if not _has_value(value):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    parsed = _float_or_none(value)
    return default if parsed is None else parsed


def _round_or_none(value: Any) -> float | None:
    parsed = _float_or_none(value)
    return None if parsed is None else round(parsed, 2)


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    try:
        return not pd.isna(value)
    except (TypeError, ValueError):
        return True
