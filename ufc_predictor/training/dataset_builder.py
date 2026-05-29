"""Leakage-aware training dataset audit and builder.

This module intentionally starts as a dry-run friendly foundation. It can
summarize whether available fight data is good enough for dedicated prop-model
training without creating model artifacts.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import pandas as pd


DECISION_METHODS = {"u-dec", "s-dec", "m-dec", "dec", "decision", "majority decision", "split decision"}


@dataclass
class TrainingDatasetAudit:
    source: str
    fight_rows: int
    fighter_count: int
    feature_count: int
    date_range: dict[str, str | None]
    source_coverage: dict[str, Any]
    label_availability: dict[str, int]
    class_distributions: dict[str, dict[str, int]]
    missingness_report: dict[str, int]
    warnings: list[str] = field(default_factory=list)
    training_data_ready: bool = False

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "fight_rows": self.fight_rows,
            "fighter_count": self.fighter_count,
            "feature_count": self.feature_count,
            "date_range": self.date_range,
            "source_coverage": self.source_coverage,
            "label_availability": self.label_availability,
            "class_distributions": self.class_distributions,
            "missingness_report": self.missingness_report,
            "warnings": self.warnings,
            "training_data_ready": self.training_data_ready,
        }


def build_training_rows(
    fights: pd.DataFrame,
    source: str = "csv",
    assume_reverse_chronological: bool = False,
) -> tuple[pd.DataFrame, TrainingDatasetAudit]:
    required = {"fighter_1", "fighter_2", "result", "method", "round"}
    missing_columns = sorted(required - set(fights.columns))
    if missing_columns:
        raise ValueError(f"Missing required fight columns: {', '.join(missing_columns)}")

    df = fights.copy()
    df["_source_order"] = range(len(df))
    has_event_date = "event_date" in df.columns and df["event_date"].notna().any()
    if has_event_date:
        df["_event_date"] = pd.to_datetime(df["event_date"], errors="coerce")
        df = df.sort_values(["_event_date", "_source_order"], na_position="last")
    elif assume_reverse_chronological:
        df = df.sort_values("_source_order", ascending=False)
    else:
        df["_event_date"] = pd.NaT

    history: dict[str, dict[str, Any]] = defaultdict(_empty_history)
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not has_event_date:
        warnings.append("No event_date column is available; chronological order falls back to CSV row order.")
        if assume_reverse_chronological:
            warnings.append("Rows were processed in reverse source order for experimental training because the cached CSV appears newest-first.")

    for _, fight in df.iterrows():
        result = str(fight.get("result") or "").lower().strip().split("\n")[0]
        if result != "win":
            continue
        fighter_a = str(fight.get("fighter_1") or "").strip()
        fighter_b = str(fight.get("fighter_2") or "").strip()
        if not fighter_a or not fighter_b:
            continue

        method = normalize_method(fight.get("method_group") or fight.get("method"))
        is_decision = method == "Decision"
        round_phase = round_phase_label(fight.get("round"), is_decision)
        a_hist = history[fighter_a]
        b_hist = history[fighter_b]
        rows.append(
            {
                "event": fight.get("event"),
                "event_date": _date_string(fight.get("_event_date")),
                "fighter_a": fighter_a,
                "fighter_b": fighter_b,
                "source": source,
                "a_prior_fights": a_hist["fights"],
                "b_prior_fights": b_hist["fights"],
                "a_prior_wins": a_hist["wins"],
                "b_prior_wins": b_hist["wins"],
                "a_prior_finishes": a_hist["finishes"],
                "b_prior_finishes": b_hist["finishes"],
                "a_prior_decisions": a_hist["decisions"],
                "b_prior_decisions": b_hist["decisions"],
                "source_order": int(fight.get("_source_order", len(rows))),
                "winner": fighter_a,
                "finish_binary": 0 if is_decision else 1,
                "goes_distance_binary": 1 if is_decision else 0,
                "method_class": method,
                "round_number": _safe_int(fight.get("round")),
                "round_phase_class": round_phase,
                "fighter_a_sig_strikes": fight.get("fighter_a_sig_strikes"),
                "fighter_b_sig_strikes": fight.get("fighter_b_sig_strikes"),
                "combined_sig_strikes": fight.get("combined_sig_strikes"),
                "fighter_a_strike_volume_bucket": fight.get("fighter_a_strike_volume_bucket"),
                "fighter_b_strike_volume_bucket": fight.get("fighter_b_strike_volume_bucket"),
                "combined_strike_volume_bucket": fight.get("strike_volume_bucket") or fight.get("combined_strike_volume_bucket"),
                "fighter_a_50plus_sig_strikes": fight.get("fighter_a_50plus_sig_strikes"),
                "fighter_b_50plus_sig_strikes": fight.get("fighter_b_50plus_sig_strikes"),
                "combined_100plus_sig_strikes": fight.get("combined_100plus_sig_strikes"),
                "fighter_a_takedowns": fight.get("fighter_a_takedowns"),
                "fighter_b_takedowns": fight.get("fighter_b_takedowns"),
                "fighter_a_takedown_1plus": fight.get("fighter_a_takedown_1plus"),
                "fighter_b_takedown_1plus": fight.get("fighter_b_takedown_1plus"),
                "grappling_heavy_binary": fight.get("grappling_heavy_binary"),
                "takedown_control_bucket": fight.get("takedown_control_bucket"),
            }
        )

        _update_history(history[fighter_a], won=True, method=method)
        _update_history(history[fighter_b], won=False, method=None)

    dataset = pd.DataFrame(rows)
    audit = audit_training_dataset(dataset, fights, source, warnings)
    return dataset, audit


def audit_training_dataset(dataset: pd.DataFrame, raw_fights: pd.DataFrame, source: str, warnings: list[str] | None = None) -> TrainingDatasetAudit:
    warnings = list(warnings or [])
    label_columns = [
        "winner",
        "finish_binary",
        "goes_distance_binary",
        "method_class",
        "round_number",
        "round_phase_class",
        "fighter_a_sig_strikes",
        "fighter_b_sig_strikes",
        "combined_sig_strikes",
        "fighter_a_strike_volume_bucket",
        "fighter_b_strike_volume_bucket",
        "combined_strike_volume_bucket",
        "fighter_a_50plus_sig_strikes",
        "fighter_b_50plus_sig_strikes",
        "combined_100plus_sig_strikes",
        "fighter_a_takedowns",
        "fighter_b_takedowns",
        "fighter_a_takedown_1plus",
        "fighter_b_takedown_1plus",
        "grappling_heavy_binary",
        "takedown_control_bucket",
    ]
    label_availability = {
        column: int(dataset[column].notna().sum()) if column in dataset.columns else 0
        for column in label_columns
    }
    distributions = {
        column: {str(key): int(value) for key, value in Counter(dataset[column].dropna()).items()}
        for column in ("finish_binary", "goes_distance_binary", "method_class", "round_phase_class", "combined_strike_volume_bucket", "grappling_heavy_binary")
        if column in dataset.columns
    }
    feature_columns = [
        "a_prior_fights",
        "b_prior_fights",
        "a_prior_wins",
        "b_prior_wins",
        "a_prior_finishes",
        "b_prior_finishes",
        "a_prior_decisions",
        "b_prior_decisions",
    ]
    missingness = {
        column: int(dataset[column].isna().sum()) if column in dataset.columns else int(len(dataset))
        for column in feature_columns + label_columns
    }
    dates = dataset["event_date"].dropna() if "event_date" in dataset.columns else pd.Series(dtype=str)
    if label_availability["fighter_a_sig_strikes"] == 0:
        warnings.append("Significant-strike labels are unavailable; strike-volume model is blocked.")
    if label_availability["fighter_a_takedowns"] == 0:
        warnings.append("Takedown/control labels are unavailable; takedown-control model is blocked.")
    if not dates.empty and len(dates) < len(dataset):
        warnings.append("Some fights are missing event dates.")

    training_data_ready = bool(
        len(dataset) >= 500
        and label_availability["finish_binary"] >= 500
        and label_availability["method_class"] >= 500
        and bool(raw_fights.get("event_date") is not None and raw_fights.get("event_date").notna().any())
    )
    if not training_data_ready:
        warnings.append("Dedicated model training is blocked until credible chronological source data is available.")

    fighters = set(dataset.get("fighter_a", pd.Series(dtype=str)).dropna()) | set(dataset.get("fighter_b", pd.Series(dtype=str)).dropna())
    return TrainingDatasetAudit(
        source=source,
        fight_rows=int(len(dataset)),
        fighter_count=len(fighters),
        feature_count=len(feature_columns),
        date_range={"min": str(dates.min()) if not dates.empty else None, "max": str(dates.max()) if not dates.empty else None},
        source_coverage={
            "raw_rows": int(len(raw_fights)),
            "has_event_history": "event" in raw_fights.columns,
            "has_fight_results": "result" in raw_fights.columns,
            "has_method_round_time": all(column in raw_fights.columns for column in ("method", "round", "time")),
            "has_event_date": bool(raw_fights.get("event_date") is not None and raw_fights.get("event_date").notna().any()),
            "has_significant_strike_totals": any(column in raw_fights.columns for column in ("fighter_a_sig_strikes", "fighter_b_sig_strikes", "combined_sig_strikes")),
            "has_takedown_control_labels": any(column in raw_fights.columns for column in ("fighter_a_takedowns", "fighter_b_takedowns", "grappling_heavy_binary", "takedown_control_bucket")),
        },
        label_availability=label_availability,
        class_distributions=distributions,
        missingness_report=missingness,
        warnings=warnings,
        training_data_ready=training_data_ready,
    )


def load_fights_csv(path: str | Path) -> pd.DataFrame:
    return pd.read_csv(path)


def normalize_method(value) -> str:
    method = str(value or "").strip().lower()
    if method in DECISION_METHODS or "dec" in method:
        return "Decision"
    if "sub" in method:
        return "Submission"
    if "ko" in method or "tko" in method:
        return "KO/TKO"
    return "Other"


def round_phase_label(round_value, is_decision: bool) -> str:
    if is_decision:
        return "decision"
    round_number = _safe_int(round_value)
    if round_number is None:
        return "unknown"
    if round_number <= 1:
        return "early"
    if round_number <= 3:
        return "middle"
    return "late"


def _empty_history() -> dict[str, int]:
    return {"fights": 0, "wins": 0, "finishes": 0, "decisions": 0}


def _update_history(history: dict[str, int], won: bool, method: str | None) -> None:
    history["fights"] += 1
    if won:
        history["wins"] += 1
        if method == "Decision":
            history["decisions"] += 1
        elif method:
            history["finishes"] += 1


def _safe_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _date_string(value) -> str | None:
    if pd.isna(value):
        return None
    return str(pd.Timestamp(value).date())
