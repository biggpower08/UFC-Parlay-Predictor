"""Bettor-style target catalog and safe label construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import pandas as pd

from ufc_predictor.training.dataset_builder import normalize_method


TARGET_CATALOG = {
    "winner": ["f1_wins", "fighter_1_win_probability", "fighter_2_win_probability"],
    "finish_distance": ["fight_finished", "went_distance", "inside_distance"],
    "method": [
        "method_class",
        "fighter_1_by_ko_tko",
        "fighter_1_by_submission",
        "fighter_1_by_decision",
        "fighter_2_by_ko_tko",
        "fighter_2_by_submission",
        "fighter_2_by_decision",
    ],
    "timing": [
        "finish_round",
        "ends_round_1",
        "ends_round_2",
        "ends_round_3",
        "ends_before_round_2",
        "ends_before_round_3",
        "over_1_5",
        "over_2_5",
        "over_3_5",
        "goes_distance",
    ],
    "strike_volume": [
        "fighter_1_sig_strikes_landed",
        "fighter_2_sig_strikes_landed",
        "total_sig_strikes_landed",
        "fighter_1_over_25_sig_strikes",
        "fighter_1_over_50_sig_strikes",
        "fighter_1_over_75_sig_strikes",
        "fighter_2_over_25_sig_strikes",
        "fighter_2_over_50_sig_strikes",
        "fighter_2_over_75_sig_strikes",
    ],
    "takedown_control": [
        "fighter_1_takedowns_landed",
        "fighter_2_takedowns_landed",
        "fighter_1_over_0_5_takedowns",
        "fighter_1_over_1_5_takedowns",
        "fighter_1_over_2_5_takedowns",
        "fighter_2_over_0_5_takedowns",
        "fighter_2_over_1_5_takedowns",
        "fighter_2_over_2_5_takedowns",
        "fighter_1_control_time_seconds",
        "fighter_2_control_time_seconds",
        "fighter_1_control_time_over_300_seconds",
        "fighter_2_control_time_over_300_seconds",
    ],
    "odds_calibration": [
        "pre_fight_moneyline_f1",
        "pre_fight_moneyline_f2",
        "implied_probability_f1",
        "implied_probability_f2",
        "odds_available",
        "odds_source",
        "closing_line_available",
    ],
    "expert_signals": [
        "expert_pick_f1",
        "expert_confidence",
        "summary_style_tags",
        "source_timestamp",
        "source_name",
        "source_url_or_id",
        "pre_fight_verified",
    ],
}


@dataclass
class TargetBuildReport:
    rows: int
    valid_winner_targets: int
    invalid_winner_targets: int
    invalid_target_reasons: dict[str, int]
    label_availability: dict[str, int]

    def to_dict(self) -> dict:
        return asdict(self)


def build_bettor_targets(df: pd.DataFrame) -> tuple[pd.DataFrame, TargetBuildReport]:
    rows = df.copy()
    f1_col = _first_column(rows, ["f_1_name", "fighter_1", "fighter_a_name", "red_fighter", "r_fighter"])
    f2_col = _first_column(rows, ["f_2_name", "fighter_2", "fighter_b_name", "blue_fighter", "b_fighter"])
    winner_col = _first_column(rows, ["winner", "winner_name", "winning_fighter"])
    method_col = _first_column(rows, ["method", "method_group", "result_details", "win_by", "result"])
    round_col = _first_column(rows, ["finish_round", "round", "last_round"])
    time_col = _first_column(rows, ["finish_time", "time", "end_time"])

    f1_wins = []
    invalid_reasons: dict[str, int] = {}
    for _, row in rows.iterrows():
        value, reason = safe_f1_wins(row, f1_col, f2_col, winner_col)
        f1_wins.append(value)
        if value is None:
            invalid_reasons[reason] = invalid_reasons.get(reason, 0) + 1
    rows["f1_wins"] = pd.Series(f1_wins, dtype="Int64")
    rows["invalid_target_reason"] = [
        safe_f1_wins(row, f1_col, f2_col, winner_col)[1] if pd.isna(value) else None
        for value, (_, row) in zip(f1_wins, rows.iterrows())
    ]

    method_class = rows[method_col].apply(normalize_method) if method_col else pd.Series([None] * len(rows))
    rows["method_class"] = method_class
    rows["went_distance"] = (method_class == "Decision").astype("Int64")
    rows["fight_finished"] = (method_class.notna() & (method_class != "Decision")).astype("Int64")
    rows["inside_distance"] = rows["fight_finished"]
    rows["goes_distance"] = rows["went_distance"]

    rounds = rows[round_col].apply(_safe_int) if round_col else pd.Series([None] * len(rows))
    rows["finish_round"] = rounds.astype("Int64")
    for round_number in (1, 2, 3):
        rows[f"ends_round_{round_number}"] = ((rows["fight_finished"] == 1) & (rounds == round_number)).astype("Int64")
    rows["ends_before_round_2"] = ((rows["fight_finished"] == 1) & (rounds < 2)).astype("Int64")
    rows["ends_before_round_3"] = ((rows["fight_finished"] == 1) & (rounds < 3)).astype("Int64")
    elapsed_seconds = [_elapsed_fight_seconds(round_value, row.get(time_col) if time_col else None) for round_value, (_, row) in zip(rounds, rows.iterrows())]
    for marker, seconds in (("over_1_5", 450), ("over_2_5", 750), ("over_3_5", 1050)):
        rows[marker] = [int(value is not None and value > seconds) for value in elapsed_seconds]
        rows.loc[rows["went_distance"] == 1, marker] = 1

    _method_side_targets(rows, "KO/TKO", "ko_tko")
    _method_side_targets(rows, "Submission", "submission")
    _method_side_targets(rows, "Decision", "decision")
    _strike_targets(rows)
    _takedown_targets(rows)
    _expert_signal_flags(rows)

    target_columns = sorted({column for columns in TARGET_CATALOG.values() for column in columns if column in rows.columns})
    availability = {column: int(rows[column].notna().sum()) for column in target_columns}
    report = TargetBuildReport(
        rows=int(len(rows)),
        valid_winner_targets=int(rows["f1_wins"].notna().sum()),
        invalid_winner_targets=int(rows["f1_wins"].isna().sum()),
        invalid_target_reasons=invalid_reasons,
        label_availability=availability,
    )
    return rows, report


def safe_f1_wins(row: pd.Series, f1_col: str | None, f2_col: str | None, winner_col: str | None) -> tuple[int | None, str | None]:
    if not f1_col or not f2_col or not winner_col:
        return None, "missing_required_columns"
    f1 = _normalize_name(row.get(f1_col))
    f2 = _normalize_name(row.get(f2_col))
    winner = _normalize_name(row.get(winner_col))
    if not winner or winner in {"draw", "nc", "no contest", "no_contest"}:
        return None, "missing_or_non_win_winner"
    if winner == f1:
        return 1, None
    if winner == f2:
        return 0, None
    return None, "missing_or_unmatched_winner"


def _method_side_targets(rows: pd.DataFrame, method_name: str, suffix: str) -> None:
    rows[f"fighter_1_by_{suffix}"] = ((rows["f1_wins"] == 1) & (rows["method_class"] == method_name)).astype("Int64")
    rows[f"fighter_2_by_{suffix}"] = ((rows["f1_wins"] == 0) & (rows["method_class"] == method_name)).astype("Int64")
    rows.loc[rows["f1_wins"].isna(), [f"fighter_1_by_{suffix}", f"fighter_2_by_{suffix}"]] = pd.NA


def _strike_targets(rows: pd.DataFrame) -> None:
    f1 = _numeric_first(rows, ["f_1_sig_strikes_succ", "fighter_1_sig_strikes_landed", "fighter_a_sig_strikes", "r_sig_str_landed"])
    f2 = _numeric_first(rows, ["f_2_sig_strikes_succ", "fighter_2_sig_strikes_landed", "fighter_b_sig_strikes", "b_sig_str_landed"])
    rows["fighter_1_sig_strikes_landed"] = f1
    rows["fighter_2_sig_strikes_landed"] = f2
    rows["total_sig_strikes_landed"] = f1 + f2
    rows.loc[f1.isna() & f2.isna(), "total_sig_strikes_landed"] = pd.NA
    for threshold in (25, 50, 75):
        rows[f"fighter_1_over_{threshold}_sig_strikes"] = _threshold(f1, threshold)
        rows[f"fighter_2_over_{threshold}_sig_strikes"] = _threshold(f2, threshold)


def _takedown_targets(rows: pd.DataFrame) -> None:
    f1 = _numeric_first(rows, ["f_1_takedown_succ", "fighter_1_takedowns_landed", "fighter_a_takedowns", "r_td_landed"])
    f2 = _numeric_first(rows, ["f_2_takedown_succ", "fighter_2_takedowns_landed", "fighter_b_takedowns", "b_td_landed"])
    c1 = _numeric_first(rows, ["f_1_ctrl_time_sec", "fighter_1_control_time_seconds", "fighter_a_control_time_seconds", "r_ctrl"])
    c2 = _numeric_first(rows, ["f_2_ctrl_time_sec", "fighter_2_control_time_seconds", "fighter_b_control_time_seconds", "b_ctrl"])
    rows["fighter_1_takedowns_landed"] = f1
    rows["fighter_2_takedowns_landed"] = f2
    rows["fighter_1_control_time_seconds"] = c1
    rows["fighter_2_control_time_seconds"] = c2
    for decimal_threshold, label_threshold in ((0.5, "0_5"), (1.5, "1_5"), (2.5, "2_5")):
        rows[f"fighter_1_over_{label_threshold}_takedowns"] = _threshold(f1, decimal_threshold)
        rows[f"fighter_2_over_{label_threshold}_takedowns"] = _threshold(f2, decimal_threshold)
    rows["fighter_1_control_time_over_300_seconds"] = _threshold(c1, 300)
    rows["fighter_2_control_time_over_300_seconds"] = _threshold(c2, 300)


def _expert_signal_flags(rows: pd.DataFrame) -> None:
    if {"source_timestamp", "event_date"} <= set(rows.columns):
        source_time = pd.to_datetime(rows["source_timestamp"], errors="coerce")
        event_date = pd.to_datetime(rows["event_date"], errors="coerce")
        rows["pre_fight_verified"] = (source_time.notna() & event_date.notna() & (source_time < event_date)).astype("Int64")
    elif "expert_pick_f1" in rows.columns:
        rows["pre_fight_verified"] = 0


def _first_column(df: pd.DataFrame, names: list[str]) -> str | None:
    normalized = {_column_key(column): column for column in df.columns}
    for name in names:
        key = _column_key(name)
        if key in normalized:
            return normalized[key]
    return None


def _numeric_first(df: pd.DataFrame, names: list[str]) -> pd.Series:
    column = _first_column(df, names)
    if not column:
        return pd.Series([pd.NA] * len(df), dtype="Float64")
    return pd.to_numeric(df[column], errors="coerce").astype("Float64")


def _threshold(values: pd.Series, threshold: float) -> pd.Series:
    result = (values >= threshold).astype("Int64")
    result[values.isna()] = pd.NA
    return result


def _elapsed_fight_seconds(round_number, finish_time) -> int | None:
    round_int = _safe_int(round_number)
    if round_int is None:
        return None
    seconds = _time_seconds(finish_time)
    if seconds is None:
        seconds = 300
    return max(0, round_int - 1) * 300 + seconds


def _time_seconds(value: Any) -> int | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if ":" not in text:
        return _safe_int(text)
    left, right = text.split(":", 1)
    minutes = _safe_int(left)
    seconds = _safe_int(right)
    if minutes is None or seconds is None:
        return None
    return minutes * 60 + seconds


def _safe_int(value) -> int | None:
    try:
        if value is None or pd.isna(value):
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _normalize_name(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return " ".join("".join(ch if ch.isalnum() or ch.isspace() else " " for ch in str(value).lower()).split())


def _column_key(value: str) -> str:
    return str(value).strip().lower().replace(" ", "_").replace(".", "").replace("-", "_").replace("%", "pct")
