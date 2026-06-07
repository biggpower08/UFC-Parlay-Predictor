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

from ufc_predictor.features.feature_schema import get_feature_schema
from ufc_predictor.features.matchup_features import build_features_from_snapshots


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
    feature_schema_name: str | None = None
    feature_schema_version: str | None = None
    feature_validation: dict[str, Any] = field(default_factory=dict)
    runtime_compatibility: dict[str, Any] = field(default_factory=dict)
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
            "feature_schema_name": self.feature_schema_name,
            "feature_schema_version": self.feature_schema_version,
            "feature_validation": self.feature_validation,
            "runtime_compatibility": self.runtime_compatibility,
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
        fighter_a = str(fight.get("fighter_1") or "").strip()
        fighter_b = str(fight.get("fighter_2") or "").strip()
        if not fighter_a or not fighter_b:
            continue

        method = normalize_method(fight.get("method_group") or fight.get("method"))
        is_decision = method == "Decision"
        round_phase = round_phase_label(fight.get("round"), is_decision)
        a_hist = history[fighter_a]
        b_hist = history[fighter_b]
        feature_set = build_features_from_snapshots(
            _snapshot_from_running_history(fighter_a, a_hist),
            _snapshot_from_running_history(fighter_b, b_hist),
            schema=get_feature_schema("finish"),
            as_of_date=_date_string(fight.get("_event_date")),
            mode="historical",
            feature_mode="actual_fight",
            scheduled_rounds=_safe_int(fight.get("scheduled_rounds")),
            weight_class=fight.get("weight_class"),
        )
        if not feature_set.validation["valid"]:
            warnings.append(f"Feature validation warning for {fighter_a} vs {fighter_b}: {feature_set.validation['warnings']}")
        rows.append(
            {
                "event": fight.get("event"),
                "event_date": _date_string(fight.get("_event_date")),
                "fight_key": fight.get("fight_key") or fight.get("source_row_id") or fight.get("source_id"),
                "source_dataset": fight.get("source_dataset") or source,
                "source_file": fight.get("source_file"),
                "weight_class": fight.get("weight_class"),
                "fighter_a": fighter_a,
                "fighter_b": fighter_b,
                "source": source,
                **feature_set.features,
                "source_order": int(fight.get("_source_order", len(rows))),
                "winner": fight.get("winner_name") if pd.notna(fight.get("winner_name")) else (fighter_a if result == "win" else None),
                "f1_wins_safe": fight.get("f1_wins_safe") if "f1_wins_safe" in fight.index else None,
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

        if result == "win":
            _update_history(history[fighter_a], won=True, method=method)
            _update_history(history[fighter_b], won=False, method=None)
        else:
            _update_history(history[fighter_a], won=None, method=None)
            _update_history(history[fighter_b], won=None, method=None)

    dataset = pd.DataFrame(rows)
    audit = audit_training_dataset(dataset, fights, source, warnings)
    return dataset, audit


def audit_training_dataset(dataset: pd.DataFrame, raw_fights: pd.DataFrame, source: str, warnings: list[str] | None = None) -> TrainingDatasetAudit:
    warnings = list(warnings or [])
    schema = get_feature_schema("finish")
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
    feature_columns = schema.all_features()
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
    runtime_report = feature_availability_report(dataset, "finish")
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
        feature_schema_name=schema.schema_name,
        feature_schema_version=schema.schema_version,
        feature_validation={
            "forbidden_features_present": sorted(set(feature_columns) & set(schema.forbidden_features)),
            "labels_kept_separate": sorted(set(dataset.columns) & set(schema.forbidden_features)),
            "required_features": schema.required_features,
        },
        runtime_compatibility=runtime_report,
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


def _snapshot_from_running_history(fighter_name: str, history: dict[str, int]) -> dict[str, Any]:
    fights = int(history.get("fights", 0) or 0)
    wins = int(history.get("wins", 0) or 0)
    finishes = int(history.get("finishes", 0) or 0)
    decisions = int(history.get("decisions", 0) or 0)
    return {
        "fighter_name": fighter_name,
        "normalized_name": str(fighter_name).lower(),
        "wins_before": wins,
        "losses_before": max(0, fights - wins),
        "draws_before": 0,
        "no_contests_before": 0,
        "total_fights_before": fights,
        "win_rate_before": _rate(wins, fights),
        "finish_win_rate_before": _rate(finishes, wins),
        "decision_win_rate_before": _rate(decisions, wins),
        "ko_tko_win_rate_before": None,
        "submission_win_rate_before": None,
        "finish_loss_rate_before": None,
        "decision_loss_rate_before": None,
        "elo_before_fight": None,
        "elo_fights_count_before": 0,
        "elo_source": "baseline",
        "elo_available": False,
    }


def feature_availability_report(dataset: pd.DataFrame, model_family: str = "finish") -> dict[str, Any]:
    schema = get_feature_schema(model_family)
    rows = int(len(dataset))
    if rows == 0:
        return {
            "schema_name": schema.schema_name,
            "schema_version": schema.schema_version,
            "rows": 0,
            "required_features_available": False,
            "required_feature_missing_rates": {name: 1.0 for name in schema.required_features},
            "optional_feature_coverage": 0.0,
            "missing_runtime_features": schema.required_features,
        }
    required_missing_rates = {
        name: round(float(dataset[name].isna().sum()) / rows, 4) if name in dataset.columns else 1.0
        for name in schema.required_features
    }
    optional_present = [
        name for name in schema.optional_features
        if name in dataset.columns and dataset[name].notna().any()
    ]
    return {
        "schema_name": schema.schema_name,
        "schema_version": schema.schema_version,
        "rows": rows,
        "required_features_available": all(rate == 0 for rate in required_missing_rates.values()),
        "required_feature_missing_rates": required_missing_rates,
        "optional_feature_coverage": round(len(optional_present) / max(1, len(schema.optional_features)), 4),
        "missing_runtime_features": [name for name, rate in required_missing_rates.items() if rate > 0],
    }


def _update_history(history: dict[str, int], won: bool | None, method: str | None) -> None:
    history["fights"] += 1
    if won is True:
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


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 4)
