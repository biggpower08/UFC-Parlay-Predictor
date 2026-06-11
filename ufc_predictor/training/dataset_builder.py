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

from ufc_predictor.config import settings
from ufc_predictor.features.feature_schema import get_feature_schema
from ufc_predictor.features.matchup_features import build_features_from_snapshots
from ufc_predictor.features.opponent_weakness_features import compute_opponent_weakness_scores
from ufc_predictor.features.style_features import compute_style_scores
from ufc_predictor.models.elo.elo_engine import expected_score, update_elo_draw, update_elo_win
from ufc_predictor.utils.helpers import normalize_name


DECISION_METHODS = {"u-dec", "s-dec", "m-dec", "dec", "decision", "majority decision", "split decision"}
NO_CONTEST_RESULTS = {"nc", "no contest", "no-contest", "no_contest", "overturned"}
DRAW_RESULTS = {"draw", "majority draw", "split draw"}


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
    elo_state: dict[str, dict[str, Any]] = defaultdict(_empty_elo_state)
    rows: list[dict[str, Any]] = []
    warnings: list[str] = []
    if not has_event_date:
        warnings.append("No event_date column is available; chronological order falls back to CSV row order.")
        if assume_reverse_chronological:
            warnings.append("Rows were processed in reverse source order for experimental training because the cached CSV appears newest-first.")

    df["_elo_event_key"] = _elo_event_keys(df, has_event_date)
    for _, event_group in df.groupby("_elo_event_key", sort=False):
        elo_pre_event = {name: state.copy() for name, state in elo_state.items()}
        pending_elo_updates: list[dict[str, Any]] = []
        for _, fight in event_group.iterrows():
            pending = _build_training_row(
                fight=fight,
                source=source,
                history=history,
                elo_pre_event=elo_pre_event,
                rows=rows,
                warnings=warnings,
                has_event_date=has_event_date,
            )
            if pending:
                pending_elo_updates.append(pending)
        for pending in pending_elo_updates:
            _apply_pending_elo_update(elo_state, pending)

    dataset = pd.DataFrame(rows)
    audit = audit_training_dataset(dataset, fights, source, warnings)
    return dataset, audit


def _build_training_row(
    fight: pd.Series,
    source: str,
    history: dict[str, dict[str, Any]],
    elo_pre_event: dict[str, dict[str, Any]],
    rows: list[dict[str, Any]],
    warnings: list[str],
    has_event_date: bool,
) -> dict[str, Any] | None:
    result = normalize_result_type(fight.get("result"))
    source_fighter_1 = str(fight.get("fighter_1") or "").strip()
    source_fighter_2 = str(fight.get("fighter_2") or "").strip()
    if not source_fighter_1 or not source_fighter_2:
        return None
    fighter_a, fighter_b, orientation = deterministic_fighter_orientation(source_fighter_1, source_fighter_2)
    winner_name = _clean_name(fight.get("winner_name"))
    if not winner_name and result == "win":
        winner_name = source_fighter_1
    loser_name = _clean_name(fight.get("loser_name"))
    if not loser_name and result == "win":
        loser_name = source_fighter_2
    f1_wins_safe = safe_winner_target(fighter_a, fighter_b, winner_name)

    method = normalize_method(fight.get("method_group") or fight.get("method"))
    outcome_has_labels = result == "win" and winner_name is not None
    is_decision = method == "Decision" if outcome_has_labels else None
    finish_round = _safe_int(fight.get("round"))
    finish_time_seconds = parse_round_time_seconds(fight.get("time") or fight.get("finish_time"))
    round_phase = round_phase_label(fight.get("round"), bool(is_decision)) if outcome_has_labels else None
    a_hist = history[fighter_a]
    b_hist = history[fighter_b]
    a_elo = _elo_snapshot(fighter_a, elo_pre_event)
    b_elo = _elo_snapshot(fighter_b, elo_pre_event)
    elo_quality_flag = "pre_event" if has_event_date else "source_order_inferred"
    elo_expected_a = round(expected_score(a_elo["elo"], b_elo["elo"]), 6)
    feature_set = build_features_from_snapshots(
        _snapshot_from_running_history(fighter_a, a_hist, a_elo),
        _snapshot_from_running_history(fighter_b, b_hist, b_elo),
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
            "source_fighter_1": source_fighter_1,
            "source_fighter_2": source_fighter_2,
            "safe_orientation": orientation,
            "source": source,
            **feature_set.features,
            "fighter_a_elo_pre": a_elo["elo"],
            "fighter_b_elo_pre": b_elo["elo"],
            "elo_diff_pre": round(a_elo["elo"] - b_elo["elo"], 6),
            "elo_expected_fighter_a_pre": elo_expected_a,
            "fighter_a_elo_fights_before": a_elo["fights"],
            "fighter_b_elo_fights_before": b_elo["fights"],
            "elo_quality_flag": elo_quality_flag,
            "elo_feature_mode": "strict_pre_event" if has_event_date else "strict_source_order_pre_fight",
            "source_order": int(fight.get("_source_order", len(rows))),
            "winner": winner_name,
            "f1_wins_safe": f1_wins_safe,
            "result_type": result,
            "finish_binary": (0 if is_decision else 1) if outcome_has_labels else None,
            "goes_distance_binary": (1 if is_decision else 0) if outcome_has_labels else None,
            "method_class": method if outcome_has_labels else None,
            "finish_type_class": None if (not outcome_has_labels or is_decision) else method,
            "round_number": finish_round if outcome_has_labels else None,
            "round_phase_class": round_phase,
            "over_1_5_binary": over_round_half_label(finish_round, finish_time_seconds, bool(is_decision), threshold_round=1) if outcome_has_labels else None,
            "over_2_5_binary": over_round_half_label(finish_round, finish_time_seconds, bool(is_decision), threshold_round=2) if outcome_has_labels else None,
            "ends_before_round_3_binary": ends_before_round_3_label(finish_round, bool(is_decision)) if outcome_has_labels else None,
            "finish_in_round_1_binary": finish_in_round_1_label(finish_round, bool(is_decision)) if outcome_has_labels else None,
            "fighter_a_sig_strikes": _oriented_value(fight, "fighter_a_sig_strikes", "fighter_b_sig_strikes", orientation),
            "fighter_b_sig_strikes": _oriented_value(fight, "fighter_b_sig_strikes", "fighter_a_sig_strikes", orientation),
            "combined_sig_strikes": fight.get("combined_sig_strikes"),
            "fighter_a_strike_volume_bucket": _oriented_value(fight, "fighter_a_strike_volume_bucket", "fighter_b_strike_volume_bucket", orientation),
            "fighter_b_strike_volume_bucket": _oriented_value(fight, "fighter_b_strike_volume_bucket", "fighter_a_strike_volume_bucket", orientation),
            "combined_strike_volume_bucket": fight.get("strike_volume_bucket") or fight.get("combined_strike_volume_bucket"),
            "fighter_a_50plus_sig_strikes": _oriented_value(fight, "fighter_a_50plus_sig_strikes", "fighter_b_50plus_sig_strikes", orientation),
            "fighter_b_50plus_sig_strikes": _oriented_value(fight, "fighter_b_50plus_sig_strikes", "fighter_a_50plus_sig_strikes", orientation),
            "combined_100plus_sig_strikes": fight.get("combined_100plus_sig_strikes"),
            "fighter_a_takedowns": _oriented_value(fight, "fighter_a_takedowns", "fighter_b_takedowns", orientation),
            "fighter_b_takedowns": _oriented_value(fight, "fighter_b_takedowns", "fighter_a_takedowns", orientation),
            "fighter_a_takedown_1plus": _oriented_value(fight, "fighter_a_takedown_1plus", "fighter_b_takedown_1plus", orientation),
            "fighter_b_takedown_1plus": _oriented_value(fight, "fighter_b_takedown_1plus", "fighter_a_takedown_1plus", orientation),
            "grappling_heavy_binary": fight.get("grappling_heavy_binary"),
            "takedown_control_bucket": fight.get("takedown_control_bucket"),
        }
    )

    a_won = f1_wins_safe is True or f1_wins_safe == 1
    b_won = f1_wins_safe is False or f1_wins_safe == 0
    _update_history(
        history[fighter_a],
        won=a_won if outcome_has_labels else None,
        method=method,
        fight=fight,
        orientation=orientation,
        side="a",
        finish_round=finish_round,
    )
    _update_history(
        history[fighter_b],
        won=b_won if outcome_has_labels else None,
        method=method,
        fight=fight,
        orientation=orientation,
        side="b",
        finish_round=finish_round,
    )

    if result == "draw":
        actual_a = 0.5
    elif outcome_has_labels and a_won:
        actual_a = 1.0
    elif outcome_has_labels and b_won:
        actual_a = 0.0
    else:
        return None
    return {
        "fighter_a": fighter_a,
        "fighter_b": fighter_b,
        "actual_a": actual_a,
    }


def audit_training_dataset(dataset: pd.DataFrame, raw_fights: pd.DataFrame, source: str, warnings: list[str] | None = None) -> TrainingDatasetAudit:
    warnings = list(warnings or [])
    schema = get_feature_schema("finish")
    label_columns = [
        "winner",
        "finish_binary",
        "goes_distance_binary",
        "method_class",
        "finish_type_class",
        "round_number",
        "round_phase_class",
        "over_1_5_binary",
        "over_2_5_binary",
        "ends_before_round_3_binary",
        "finish_in_round_1_binary",
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
        for column in (
            "finish_binary",
            "goes_distance_binary",
            "method_class",
            "finish_type_class",
            "round_phase_class",
            "over_1_5_binary",
            "over_2_5_binary",
            "ends_before_round_3_binary",
            "finish_in_round_1_binary",
            "combined_strike_volume_bucket",
            "grappling_heavy_binary",
        )
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
    return pd.read_csv(path, low_memory=False)


def normalize_result_type(value) -> str:
    text = str(value or "").lower().strip().split("\n")[0]
    if not text:
        return "unknown"
    if text in NO_CONTEST_RESULTS or "no contest" in text or "overturned" in text:
        return "nc"
    if text in DRAW_RESULTS or text == "d" or "draw" in text:
        return "draw"
    if text in {"win", "w", "winner"}:
        return "win"
    if "win" in text:
        return "win"
    return "unknown"


def normalize_method(value) -> str:
    method = str(value or "").strip().lower()
    if method in DECISION_METHODS or "dec" in method:
        return "Decision"
    if "sub" in method:
        return "Submission"
    if "ko" in method or "tko" in method:
        return "KO/TKO"
    return "Other"


def deterministic_fighter_orientation(fighter_1: str, fighter_2: str) -> tuple[str, str, str]:
    left = str(fighter_1 or "").strip()
    right = str(fighter_2 or "").strip()
    ordered = sorted([(normalize_name(left), left), (normalize_name(right), right)], key=lambda item: (item[0], item[1].lower()))
    first = ordered[0][1]
    second = ordered[1][1]
    return first, second, "source_order" if first == left and second == right else "name_sorted_swapped"


def safe_winner_target(fighter_1: str, fighter_2: str, winner_name: str | None) -> int | None:
    winner = normalize_name(winner_name or "")
    if not winner or winner in {"draw", "nc", "no contest", "no_contest"}:
        return None
    if winner == normalize_name(fighter_1):
        return 1
    if winner == normalize_name(fighter_2):
        return 0
    return None


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


def over_round_half_label(round_number: int | None, round_time_seconds: int | None, is_decision: bool, threshold_round: int) -> int | None:
    """Return whether a fight passed X.5 rounds without guessing missing midpoint times."""
    if is_decision:
        return 1
    if round_number is None:
        return None
    if round_number <= threshold_round:
        return 0
    if round_number >= threshold_round + 2:
        return 1
    if round_number == threshold_round + 1:
        if round_time_seconds is None:
            return None
        return 1 if round_time_seconds > 150 else 0
    return None


def ends_before_round_3_label(round_number: int | None, is_decision: bool) -> int | None:
    if is_decision:
        return 0
    if round_number is None:
        return None
    return 1 if round_number < 3 else 0


def finish_in_round_1_label(round_number: int | None, is_decision: bool) -> int | None:
    if is_decision:
        return 0
    if round_number is None:
        return None
    return 1 if round_number == 1 else 0


def parse_round_time_seconds(value) -> int | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if not text:
        return None
    if ":" in text:
        left, right = text.split(":", 1)
        minutes = _safe_int(left)
        seconds = _safe_int(right)
        if minutes is None or seconds is None:
            return None
        return minutes * 60 + seconds
    return _safe_int(text)


def _empty_history() -> dict[str, Any]:
    return {
        "fights": 0,
        "wins": 0,
        "losses": 0,
        "finishes": 0,
        "decisions": 0,
        "ko_tko_wins": 0,
        "submission_wins": 0,
        "finish_losses": 0,
        "early_finish_losses": 0,
        "decision_losses": 0,
        "early_finishes": 0,
        "sig_landed_for": 0.0,
        "sig_landed_against": 0.0,
        "sig_attempted_for": 0.0,
        "takedowns_for": 0.0,
        "takedowns_against": 0.0,
        "takedowns_attempted_for": 0.0,
        "takedowns_attempted_against": 0.0,
        "control_for_seconds": 0.0,
        "control_against_seconds": 0.0,
        "recent_results": [],
    }


def _empty_elo_state() -> dict[str, Any]:
    return {"elo": float(settings.ELO_INITIAL), "fights": 0}


def _elo_event_keys(df: pd.DataFrame, has_event_date: bool) -> pd.Series:
    if not has_event_date:
        return df["_source_order"].astype(str)
    event_name = df["event"].fillna("").astype(str) if "event" in df.columns else pd.Series([""] * len(df), index=df.index)
    event_dates = df["_event_date"].dt.strftime("%Y-%m-%d").fillna("missing-date")
    return event_dates + "|" + event_name


def _elo_snapshot(fighter_name: str, elo_state: dict[str, dict[str, Any]]) -> dict[str, Any]:
    state = elo_state.get(fighter_name) or _empty_elo_state()
    return {"elo": float(state.get("elo", settings.ELO_INITIAL)), "fights": int(state.get("fights", 0) or 0)}


def _apply_pending_elo_update(elo_state: dict[str, dict[str, Any]], pending: dict[str, Any]) -> None:
    fighter_a = pending["fighter_a"]
    fighter_b = pending["fighter_b"]
    a_state = elo_state[fighter_a]
    b_state = elo_state[fighter_b]
    a_elo = float(a_state.get("elo", settings.ELO_INITIAL))
    b_elo = float(b_state.get("elo", settings.ELO_INITIAL))
    actual_a = pending.get("actual_a")
    if actual_a == 1.0:
        new_a, new_b = update_elo_win(a_elo, b_elo)
    elif actual_a == 0.0:
        new_b, new_a = update_elo_win(b_elo, a_elo)
    elif actual_a == 0.5:
        new_a, new_b = update_elo_draw(a_elo, b_elo)
    else:
        return
    a_state["elo"] = float(new_a)
    b_state["elo"] = float(new_b)
    a_state["fights"] = int(a_state.get("fights", 0) or 0) + 1
    b_state["fights"] = int(b_state.get("fights", 0) or 0) + 1


def _snapshot_from_running_history(
    fighter_name: str,
    history: dict[str, int],
    elo_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fights = int(history.get("fights", 0) or 0)
    wins = int(history.get("wins", 0) or 0)
    finishes = int(history.get("finishes", 0) or 0)
    decisions = int(history.get("decisions", 0) or 0)
    losses = int(history.get("losses", 0) or 0)
    recent = list(history.get("recent_results", []))
    elo_state = elo_state or _empty_elo_state()
    elo_fights = int(elo_state.get("fights", 0) or 0)
    snapshot = {
        "fighter_name": fighter_name,
        "normalized_name": str(fighter_name).lower(),
        "wins_before": wins,
        "losses_before": losses,
        "draws_before": 0,
        "no_contests_before": 0,
        "total_fights_before": fights,
        "win_rate_before": _rate(wins, fights),
        "finish_win_rate_before": _rate(finishes, wins),
        "decision_win_rate_before": _rate(decisions, wins),
        "ko_tko_win_rate_before": _rate(int(history.get("ko_tko_wins", 0) or 0), wins),
        "submission_win_rate_before": _rate(int(history.get("submission_wins", 0) or 0), wins),
        "finish_loss_rate_before": _rate(int(history.get("finish_losses", 0) or 0), losses),
        "decision_loss_rate_before": _rate(int(history.get("decision_losses", 0) or 0), losses),
        "recent_3_win_rate": _recent_rate(recent, 3),
        "recent_5_win_rate": _recent_rate(recent, 5),
        "elo_before_fight": float(elo_state.get("elo", settings.ELO_INITIAL)),
        "elo_fights_count_before": elo_fights,
        "elo_source": "computed" if elo_fights > 0 else "baseline",
        "elo_available": elo_fights > 0,
    }
    snapshot.update(_style_weakness_scores(history))
    return snapshot


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


def _update_history(
    history: dict[str, Any],
    won: bool | None,
    method: str | None,
    fight: pd.Series,
    orientation: str,
    side: str,
    finish_round: int | None,
) -> None:
    history["fights"] += 1
    if won is True:
        history["wins"] += 1
        if method == "Decision":
            history["decisions"] += 1
        elif method:
            history["finishes"] += 1
            if method == "KO/TKO":
                history["ko_tko_wins"] += 1
            if method == "Submission":
                history["submission_wins"] += 1
            if finish_round == 1:
                history["early_finishes"] += 1
        history["recent_results"].append(1)
    elif won is False:
        history["losses"] += 1
        if method == "Decision":
            history["decision_losses"] += 1
        elif method:
            history["finish_losses"] += 1
            if finish_round == 1:
                history["early_finish_losses"] += 1
        history["recent_results"].append(0)
    else:
        history["recent_results"].append(None)
    history["recent_results"] = history["recent_results"][-5:]
    _update_style_stats(history, fight, orientation, side)


def _update_style_stats(history: dict[str, Any], fight: pd.Series, orientation: str, side: str) -> None:
    own_prefix = "fighter_a" if side == "a" else "fighter_b"
    opp_prefix = "fighter_b" if side == "a" else "fighter_a"
    own_sig = _oriented_value(fight, f"{own_prefix}_sig_strikes", f"{opp_prefix}_sig_strikes", orientation)
    opp_sig = _oriented_value(fight, f"{opp_prefix}_sig_strikes", f"{own_prefix}_sig_strikes", orientation)
    own_sig_attempted = _oriented_value(fight, f"{own_prefix}_sig_strikes_attempted", f"{opp_prefix}_sig_strikes_attempted", orientation)
    own_td = _oriented_value(fight, f"{own_prefix}_takedowns", f"{opp_prefix}_takedowns", orientation)
    opp_td = _oriented_value(fight, f"{opp_prefix}_takedowns", f"{own_prefix}_takedowns", orientation)
    own_td_attempted = _oriented_value(fight, f"{own_prefix}_takedowns_attempted", f"{opp_prefix}_takedowns_attempted", orientation)
    opp_td_attempted = _oriented_value(fight, f"{opp_prefix}_takedowns_attempted", f"{own_prefix}_takedowns_attempted", orientation)
    own_control = _oriented_value(fight, f"{own_prefix}_control_time_seconds", f"{opp_prefix}_control_time_seconds", orientation)
    opp_control = _oriented_value(fight, f"{opp_prefix}_control_time_seconds", f"{own_prefix}_control_time_seconds", orientation)
    _add_number(history, "sig_landed_for", own_sig)
    _add_number(history, "sig_landed_against", opp_sig)
    _add_number(history, "sig_attempted_for", own_sig_attempted)
    _add_number(history, "takedowns_for", own_td)
    _add_number(history, "takedowns_against", opp_td)
    _add_number(history, "takedowns_attempted_for", own_td_attempted)
    _add_number(history, "takedowns_attempted_against", opp_td_attempted)
    _add_number(history, "control_for_seconds", own_control)
    _add_number(history, "control_against_seconds", opp_control)


def _style_weakness_scores(history: dict[str, Any]) -> dict[str, float | None]:
    return {**compute_style_scores(history), **compute_opponent_weakness_scores(history)}


def _add_number(history: dict[str, Any], key: str, value) -> None:
    number = _safe_float(value)
    if number is not None:
        history[key] = float(history.get(key, 0.0) or 0.0) + number


def _oriented_value(row: pd.Series, source_key: str, swapped_key: str, orientation: str):
    if orientation == "name_sorted_swapped":
        return row.get(swapped_key)
    return row.get(source_key)


def _clean_name(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def _safe_int(value) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_float(value) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(number):
        return None
    return number


def _date_string(value) -> str | None:
    if pd.isna(value):
        return None
    return str(pd.Timestamp(value).date())


def _rate(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round(float(numerator) / float(denominator), 4)


def _recent_rate(values: list[Any], limit: int) -> float | None:
    recent = [value for value in values[-limit:] if value is not None]
    if not recent:
        return None
    return round(float(sum(recent)) / len(recent), 4)


def _clip01(value) -> float | None:
    number = _safe_float(value)
    if number is None:
        return None
    return round(max(0.0, min(1.0, number)), 4)
