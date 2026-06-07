"""Flexible CSV import for manually downloaded MMA training datasets."""

from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Any

import pandas as pd

from ufc_predictor.training.dataset_builder import normalize_method, round_phase_label

SUPPORTED_FILE_NAMES = {
    "ufc_events.csv",
    "ufc_fight_details.csv",
    "ufc_fight_results.csv",
    "ufc_fight_stats.csv",
    "ufc_fighter_details.csv",
    "ufc_fighter_tott.csv",
    "fights.csv",
    "fighters.csv",
    "enhanced_fights.csv",
    "fighter_stats.csv",
}

EVENT_ALIASES = ["event_name", "event", "event_title", "event_url"]
DATE_ALIASES = ["event_date", "eventdate", "event_date_utc", "date", "fight_date", "event_date_local"]
WEIGHT_ALIASES = ["weight_class", "weightclass", "bout_weight", "division"]
METHOD_ALIASES = ["method", "win_by", "finish", "finish_method", "method_group", "result"]
ROUND_ALIASES = ["round", "round_num", "last_round", "end_round", "end_round_num", "finish_round"]
TIME_ALIASES = ["time", "finish_time", "finish_round_time", "end_time", "end_time_sec", "match_time_sec"]
SCHEDULED_ROUNDS_ALIASES = ["scheduled_rounds", "format", "time_format", "total_rounds", "num_rounds", "no_of_rounds"]
WINNER_ALIASES = ["winner", "winner_name", "winning_fighter", "winner_fighter", "w_fighter"]
LOSER_ALIASES = ["loser", "loser_name", "losing_fighter", "fighter_2", "l_fighter"]
RED_ALIASES = ["r_fighter", "r_name", "red_fighter", "redfighter", "fighter_a", "fighter_a_name", "f_1_name", "fighter_1"]
BLUE_ALIASES = ["b_fighter", "b_name", "blue_fighter", "bluefighter", "fighter_b", "fighter_b_name", "f_2_name", "fighter_2"]
RED_RESULT_ALIASES = ["winner_red_blue", "winner_color", "winner_corner"]

RED_SIG_LANDED = ["r_sig_str_landed", "r_sig_str", "r_sig_strikes_landed", "red_sig_str_landed", "fighter_a_sig_strikes_landed", "f1_sig_str_landed", "f_1_sig_strikes_succ", "f_1_sig_strikes_succ_total", "f_1_sig_landed"]
BLUE_SIG_LANDED = ["b_sig_str_landed", "b_sig_str", "b_sig_strikes_landed", "blue_sig_str_landed", "fighter_b_sig_strikes_landed", "f2_sig_str_landed", "f_2_sig_strikes_succ", "f_2_sig_strikes_succ_total", "f_2_sig_landed"]
RED_SIG_ATTEMPTED = ["r_sig_str_attempted", "r_sig_str_atmpted", "r_sig_str_att", "red_sig_str_attempted", "fighter_a_sig_strikes_attempted", "f1_sig_str_attempted", "f_1_sig_strikes_att", "f_1_sig_strikes_att_total", "f_1_sig_att"]
BLUE_SIG_ATTEMPTED = ["b_sig_str_attempted", "b_sig_str_atmpted", "b_sig_str_att", "blue_sig_str_attempted", "fighter_b_sig_strikes_attempted", "f2_sig_str_attempted", "f_2_sig_strikes_att", "f_2_sig_strikes_att_total", "f_2_sig_att"]
RED_TD_LANDED = ["r_td_landed", "r_td", "r_takedowns_landed", "red_takedowns_landed", "fighter_a_takedowns_landed", "f1_td_landed", "f_1_takedown_succ", "f_1_td_1_succ_total"]
BLUE_TD_LANDED = ["b_td_landed", "b_td", "b_takedowns_landed", "blue_takedowns_landed", "fighter_b_takedowns_landed", "f2_td_landed", "f_2_takedown_succ", "f_2_td_1_succ_total"]
RED_TD_ATTEMPTED = ["r_td_attempted", "r_td_atmpted", "r_td_att", "red_takedowns_attempted", "fighter_a_takedowns_attempted", "f1_td_attempted", "f_1_takedown_att", "f_1_td_1_att_total"]
BLUE_TD_ATTEMPTED = ["b_td_attempted", "b_td_atmpted", "b_td_att", "blue_takedowns_attempted", "fighter_b_takedowns_attempted", "f2_td_attempted", "f_2_takedown_att", "f_2_td_1_att_total"]
RED_CONTROL = ["r_ctrl", "r_control", "red_control_time", "fighter_a_control_time_seconds", "f1_ctrl", "f_1_ctrl_time_sec", "f1_ctrl_time_sec"]
BLUE_CONTROL = ["b_ctrl", "b_control", "blue_control_time", "fighter_b_control_time_seconds", "f2_ctrl", "f_2_ctrl_time_sec", "f2_ctrl_time_sec"]
RED_SUB_ATT = ["r_sub_att", "r_submission_att", "f1_sub_att", "f_1_submission_att", "fighter_a_submission_attempts"]
BLUE_SUB_ATT = ["b_sub_att", "b_submission_att", "f2_sub_att", "f_2_submission_att", "fighter_b_submission_attempts"]
RED_KD = ["r_kd", "r_knockdowns", "f1_kd", "f_1_knockdowns", "fighter_a_knockdowns"]
BLUE_KD = ["b_kd", "b_knockdowns", "f2_kd", "f_2_knockdowns", "fighter_b_knockdowns"]
ODDS_ALIASES = ["moneyline", "odds", "opening_odds", "closing_odds", "r_odds", "b_odds", "fighter_odds", "odds_1", "odds_2", "f_1_odds", "f_2_odds"]
SPORTSBOOK_ALIASES = ["sportsbook", "book", "provider", "source"]
SNAPSHOT_DATE_ALIASES = ["snapshot_date", "scrape_date", "odds_date", "timestamp", "fetched_at"]


@dataclass
class ImportReport:
    input_dir: str
    output: str | None
    detected_files: list[str] = field(default_factory=list)
    supported_files: list[str] = field(default_factory=list)
    unknown_files: list[str] = field(default_factory=list)
    file_types: dict[str, str] = field(default_factory=dict)
    rows_read: int = 0
    rows_normalized: int = 0
    duplicate_fights: int = 0
    missing_columns: dict[str, list[str]] = field(default_factory=dict)
    label_availability: dict[str, int] = field(default_factory=dict)
    date_range: dict[str, str | None] = field(default_factory=dict)
    odds_availability: dict[str, int] = field(default_factory=dict)
    source_files: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "input_dir": self.input_dir,
            "output": self.output,
            "detected_files": self.detected_files,
            "supported_files": self.supported_files,
            "unknown_files": self.unknown_files,
            "file_types": self.file_types,
            "rows_read": self.rows_read,
            "rows_normalized": self.rows_normalized,
            "duplicate_fights": self.duplicate_fights,
            "missing_columns": self.missing_columns,
            "label_availability": self.label_availability,
            "date_range": self.date_range,
            "odds_availability": self.odds_availability,
            "source_files": self.source_files,
            "warnings": self.warnings,
        }


def import_training_csvs(input_dir: str | Path, output: str | Path | None = None, dry_run: bool = False) -> tuple[pd.DataFrame, ImportReport]:
    input_path = Path(input_dir)
    report = ImportReport(input_dir=str(input_path), output=str(output) if output else None)
    if not input_path.exists():
        report.warnings.append("Input directory does not exist.")
        return pd.DataFrame(), report

    csv_files = sorted(input_path.rglob("*.csv"))
    report.detected_files = [str(path) for path in csv_files]
    normalized_frames = []
    odds_rows = []
    for path in csv_files:
        file_type = _classify_csv(path)
        report.file_types[str(path)] = file_type
        if file_type == "fight":
            report.supported_files.append(str(path))
            frame, missing = _normalize_csv(path)
            report.rows_read += int(len(frame)) if not frame.empty else _count_csv_rows(path)
            report.missing_columns[str(path)] = missing
            if not frame.empty:
                normalized_frames.append(frame)
        elif file_type in {"fighter", "odds"}:
            report.supported_files.append(str(path))
            rows = _count_csv_rows(path)
            report.rows_read += rows
            report.missing_columns[str(path)] = []
            if file_type == "odds":
                odds_rows.append((path, rows))
        else:
            report.unknown_files.append(str(path))

    if normalized_frames:
        normalized = pd.concat(normalized_frames, ignore_index=True)
        normalized = _finalize_normalized(normalized)
        duplicate_mask = normalized.duplicated(subset=["event_name", "event_date", "fighter_1", "fighter_2", "method", "round"], keep="first")
        report.duplicate_fights = int(duplicate_mask.sum())
        normalized = normalized[~duplicate_mask].reset_index(drop=True)
    else:
        normalized = pd.DataFrame()

    report.rows_normalized = int(len(normalized))
    report.source_files = sorted(normalized["source_file"].dropna().unique().tolist()) if not normalized.empty else []
    report.label_availability = _label_availability(normalized)
    report.odds_availability = _odds_availability(odds_rows)
    dates = pd.to_datetime(normalized.get("event_date"), errors="coerce") if not normalized.empty else pd.Series(dtype="datetime64[ns]")
    valid_dates = dates.dropna()
    report.date_range = {
        "min": str(valid_dates.min().date()) if not valid_dates.empty else None,
        "max": str(valid_dates.max().date()) if not valid_dates.empty else None,
    }
    if report.rows_normalized == 0:
        report.warnings.append("No supported fight rows were normalized. Place downloaded CSVs under data/imports or ufc_predictor/data/imports.")
    if report.label_availability.get("event_date", 0) == 0 and report.rows_normalized:
        report.warnings.append("Imported rows are missing event dates; downstream training must remain experimental.")
    if report.label_availability.get("fighter_a_sig_strikes", 0) == 0:
        report.warnings.append("No significant-strike labels detected in imported CSVs.")
    if report.label_availability.get("fighter_a_takedowns", 0) == 0:
        report.warnings.append("No takedown/control labels detected in imported CSVs.")
    if report.odds_availability.get("rows", 0) == 0:
        report.warnings.append("No odds snapshot rows detected; odds calibration/value models remain blocked.")

    if output and not dry_run and not normalized.empty:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        normalized.to_csv(output_path, index=False)
        report_path = output_path.with_suffix(".import_report.json")
        report_path.write_text(__import__("json").dumps(report.to_dict(), indent=2, default=str), encoding="utf-8")
    return normalized, report


def _classify_csv(path: Path) -> str:
    lower_name = path.name.lower()
    if lower_name in SUPPORTED_FILE_NAMES or _looks_like_fight_csv(path):
        if lower_name in {"fighters.csv", "fighter_stats.csv", "ufc_fighter_details.csv", "ufc_fighter_tott.csv"} and not _looks_like_fight_csv(path):
            return "fighter"
        return "fight"
    try:
        columns = _standardize_columns(pd.read_csv(path, nrows=0)).columns
    except Exception:
        return "unknown"
    if _first_existing(columns, ODDS_ALIASES):
        return "odds"
    fighter_profile_markers = {"wins", "losses", "draws", "height", "weight", "reach", "stance", "date_of_birth", "dob"}
    if ({"fighter", "fighter_name"} & set(columns)) or ("name" in columns and fighter_profile_markers & set(columns)):
        return "fighter"
    return "unknown"


def _looks_like_fight_csv(path: Path) -> bool:
    try:
        columns = _standardize_columns(pd.read_csv(path, nrows=0)).columns
    except Exception:
        return False
    has_fighters = bool(_first_existing(columns, WINNER_ALIASES) and _first_existing(columns, LOSER_ALIASES)) or bool(
        _first_existing(columns, RED_ALIASES) and _first_existing(columns, BLUE_ALIASES)
    )
    return has_fighters and bool(_first_existing(columns, METHOD_ALIASES))


def _normalize_csv(path: Path) -> tuple[pd.DataFrame, list[str]]:
    raw = _standardize_columns(pd.read_csv(path, low_memory=False))
    columns = raw.columns
    missing = []
    winner_col = _first_existing(columns, WINNER_ALIASES)
    loser_col = _first_existing(columns, LOSER_ALIASES)
    red_col = _first_existing(columns, RED_ALIASES)
    blue_col = _first_existing(columns, BLUE_ALIASES)
    method_col = _first_existing(columns, METHOD_ALIASES)
    round_col = _first_existing(columns, ROUND_ALIASES)
    if not method_col:
        missing.append("method")
        return pd.DataFrame(), missing
    if not ((winner_col and loser_col) or (red_col and blue_col)):
        missing.append("fighter columns")
        return pd.DataFrame(), missing

    records = []
    for index, row in raw.iterrows():
        names = _winner_loser(row, winner_col, loser_col, red_col, blue_col)
        if not names:
            continue
        fighter_one, fighter_two, fighter_one_side, winner_name = names
        method = normalize_method(row.get(method_col))
        is_decision = method == "Decision"
        round_number = _safe_int(row.get(round_col)) if round_col else None
        red_sig_landed = _stat_value(row, RED_SIG_LANDED)
        blue_sig_landed = _stat_value(row, BLUE_SIG_LANDED)
        red_sig_attempted = _stat_attempt(row, RED_SIG_LANDED, RED_SIG_ATTEMPTED)
        blue_sig_attempted = _stat_attempt(row, BLUE_SIG_LANDED, BLUE_SIG_ATTEMPTED)
        red_td_landed = _stat_value(row, RED_TD_LANDED)
        blue_td_landed = _stat_value(row, BLUE_TD_LANDED)
        red_td_attempted = _stat_attempt(row, RED_TD_LANDED, RED_TD_ATTEMPTED)
        blue_td_attempted = _stat_attempt(row, BLUE_TD_LANDED, BLUE_TD_ATTEMPTED)
        red_control = _control_seconds(_first_value(row, RED_CONTROL))
        blue_control = _control_seconds(_first_value(row, BLUE_CONTROL))
        red_sub_att = _stat_value(row, RED_SUB_ATT)
        blue_sub_att = _stat_value(row, BLUE_SUB_ATT)
        red_kd = _stat_value(row, RED_KD)
        blue_kd = _stat_value(row, BLUE_KD)
        winner_is_red = fighter_one_side == "red"
        records.append(
            {
                "event": _first_value(row, EVENT_ALIASES),
                "event_name": _first_value(row, EVENT_ALIASES),
                "event_date": _date_value(_first_value(row, DATE_ALIASES)),
                "fight_order": row.get("fight_order", index),
                "source_order": index,
                "source_file": str(path),
                "source_dataset": path.parent.name or "local_csv",
                "source_id": _source_id(path, index, fighter_one, fighter_two, row.get(method_col), round_number),
                "fight_id_source": row.get("fight_id") or row.get("fight_url"),
                "event_id_source": row.get("event_id") or row.get("event_url"),
                "weight_class": _first_value(row, WEIGHT_ALIASES),
                "scheduled_rounds": _first_value(row, SCHEDULED_ROUNDS_ALIASES),
                "fighter_1": fighter_one,
                "fighter_2": fighter_two,
                "fighter_a_name": fighter_one,
                "fighter_b_name": fighter_two,
                "fighter_a_normalized_name": _normalize_name(fighter_one),
                "fighter_b_normalized_name": _normalize_name(fighter_two),
                "winner_name": winner_name,
                "loser_name": _opponent_name(winner_name, fighter_one, fighter_two),
                "result": "win" if winner_name else None,
                "method": row.get(method_col),
                "method_group": method,
                "finish_binary": 0 if is_decision else 1,
                "goes_distance_binary": 1 if is_decision else 0,
                "round": round_number,
                "time": _first_value(row, TIME_ALIASES),
                "round_phase_class": round_phase_label(round_number, is_decision),
                "fighter_a_sig_strikes": red_sig_landed if winner_is_red else blue_sig_landed,
                "fighter_b_sig_strikes": blue_sig_landed if winner_is_red else red_sig_landed,
                "fighter_a_sig_strikes_attempted": red_sig_attempted if winner_is_red else blue_sig_attempted,
                "fighter_b_sig_strikes_attempted": blue_sig_attempted if winner_is_red else red_sig_attempted,
                "fighter_a_takedowns": red_td_landed if winner_is_red else blue_td_landed,
                "fighter_b_takedowns": blue_td_landed if winner_is_red else red_td_landed,
                "fighter_a_takedowns_attempted": red_td_attempted if winner_is_red else blue_td_attempted,
                "fighter_b_takedowns_attempted": blue_td_attempted if winner_is_red else red_td_attempted,
                "fighter_a_control_time_seconds": red_control if winner_is_red else blue_control,
                "fighter_b_control_time_seconds": blue_control if winner_is_red else red_control,
                "fighter_a_submission_attempts": red_sub_att if winner_is_red else blue_sub_att,
                "fighter_b_submission_attempts": blue_sub_att if winner_is_red else red_sub_att,
                "fighter_a_knockdowns": red_kd if winner_is_red else blue_kd,
                "fighter_b_knockdowns": blue_kd if winner_is_red else red_kd,
                "fighter_1_height": _first_value(row, ["r_height", "f1_height_cm", "f_1_fighter_height_cm"]) if winner_is_red else _first_value(row, ["b_height", "f2_height_cm", "f_2_fighter_height_cm"]),
                "fighter_2_height": _first_value(row, ["b_height", "f2_height_cm", "f_2_fighter_height_cm"]) if winner_is_red else _first_value(row, ["r_height", "f1_height_cm", "f_1_fighter_height_cm"]),
                "fighter_1_reach": _first_value(row, ["r_reach", "f1_reach_cm", "f_1_fighter_reach_cm"]) if winner_is_red else _first_value(row, ["b_reach", "f2_reach_cm", "f_2_fighter_reach_cm"]),
                "fighter_2_reach": _first_value(row, ["b_reach", "f2_reach_cm", "f_2_fighter_reach_cm"]) if winner_is_red else _first_value(row, ["r_reach", "f1_reach_cm", "f_1_fighter_reach_cm"]),
                "fighter_1_stance": _first_value(row, ["r_stance", "f1_stance", "f_1_fighter_stance"]) if winner_is_red else _first_value(row, ["b_stance", "f2_stance", "f_2_fighter_stance"]),
                "fighter_2_stance": _first_value(row, ["b_stance", "f2_stance", "f_2_fighter_stance"]) if winner_is_red else _first_value(row, ["r_stance", "f1_stance", "f_1_fighter_stance"]),
                "fighter_1_dob": _date_value(_first_value(row, ["r_dob", "f1_dob", "f_1_fighter_dob"])) if winner_is_red else _date_value(_first_value(row, ["b_dob", "f2_dob", "f_2_fighter_dob"])),
                "fighter_2_dob": _date_value(_first_value(row, ["b_dob", "f2_dob", "f_2_fighter_dob"])) if winner_is_red else _date_value(_first_value(row, ["r_dob", "f1_dob", "f_1_fighter_dob"])),
                "fighter_1_moneyline": _first_value(row, ["r_odds", "f_1_odds", "odds_1"]) if winner_is_red else _first_value(row, ["b_odds", "f_2_odds", "odds_2"]),
                "fighter_2_moneyline": _first_value(row, ["b_odds", "f_2_odds", "odds_2"]) if winner_is_red else _first_value(row, ["r_odds", "f_1_odds", "odds_1"]),
                "odds_source": _first_value(row, SPORTSBOOK_ALIASES),
                "odds_snapshot_date": _date_value(_first_value(row, SNAPSHOT_DATE_ALIASES)),
                "odds_is_prefight": _prefight_flag(_first_value(row, SNAPSHOT_DATE_ALIASES), _first_value(row, DATE_ALIASES)),
            }
        )
    return pd.DataFrame(records), missing


def _count_csv_rows(path: Path) -> int:
    try:
        with path.open("rb") as handle:
            line_count = sum(1 for _ in handle)
    except OSError:
        return 0
    return max(0, line_count - 1)


def _finalize_normalized(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["combined_sig_strikes"] = _sum_columns(df, "fighter_a_sig_strikes", "fighter_b_sig_strikes")
    df["combined_sig_strikes_attempted"] = _sum_columns(df, "fighter_a_sig_strikes_attempted", "fighter_b_sig_strikes_attempted")
    df["strike_volume_bucket"] = df["combined_sig_strikes"].apply(_strike_bucket)
    df["fighter_a_50plus_sig_strikes"] = df["fighter_a_sig_strikes"].apply(lambda value: _threshold(value, 50))
    df["fighter_b_50plus_sig_strikes"] = df["fighter_b_sig_strikes"].apply(lambda value: _threshold(value, 50))
    df["combined_100plus_sig_strikes"] = df["combined_sig_strikes"].apply(lambda value: _threshold(value, 100))
    df["fighter_a_takedown_1plus"] = df["fighter_a_takedowns"].apply(lambda value: _threshold(value, 1))
    df["fighter_b_takedown_1plus"] = df["fighter_b_takedowns"].apply(lambda value: _threshold(value, 1))
    total_tds = _sum_columns(df, "fighter_a_takedowns", "fighter_b_takedowns")
    total_control = _sum_columns(df, "fighter_a_control_time_seconds", "fighter_b_control_time_seconds")
    df["grappling_heavy_binary"] = ((total_tds.fillna(0) >= 3) | (total_control.fillna(0) >= 300)).astype("Int64")
    df.loc[total_tds.isna() & total_control.isna(), "grappling_heavy_binary"] = pd.NA
    df["takedown_control_bucket"] = total_tds.apply(_takedown_bucket)
    return df


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    renamed = {column: _column_key(column) for column in df.columns}
    return df.rename(columns=renamed)


def _column_key(value: str) -> str:
    return str(value).strip().lower().replace(" ", "_").replace(".", "").replace("%", "pct").replace("-", "_")


def _first_existing(columns, aliases: list[str]) -> str | None:
    normalized_aliases = [_column_key(alias) for alias in aliases]
    for alias in normalized_aliases:
        if alias in columns:
            return alias
    return None


def _first_value(row: pd.Series, aliases: list[str]):
    for alias in aliases:
        key = _column_key(alias)
        if key in row.index and pd.notna(row.get(key)):
            return row.get(key)
    return None


def _winner_loser(row, winner_col, loser_col, red_col, blue_col):
    if winner_col and loser_col:
        winner = _clean_name(row.get(winner_col))
        loser = _clean_name(row.get(loser_col))
        if winner and loser and winner.lower() != loser.lower():
            winner_side = _winner_side_from_names(winner, row, red_col, blue_col)
            return winner, loser, winner_side, winner
    red = _clean_name(row.get(red_col)) if red_col else ""
    blue = _clean_name(row.get(blue_col)) if blue_col else ""
    if not red or not blue:
        return None
    marker = str(_first_value(row, RED_RESULT_ALIASES) or row.get("winner", "")).strip().lower()
    if marker in {"red", "r", "red_fighter", "r_fighter"}:
        return red, blue, "red", red
    if marker in {"blue", "b", "blue_fighter", "b_fighter"}:
        return blue, red, "blue", blue
    winner = _clean_name(row.get(winner_col)) if winner_col else ""
    if winner and winner.lower() == red.lower():
        return red, blue, "red", red
    if winner and winner.lower() == blue.lower():
        return blue, red, "blue", blue
    return red, blue, "red", None


def _opponent_name(winner_name: str | None, fighter_one: str, fighter_two: str) -> str | None:
    if not winner_name:
        return None
    if winner_name.lower() == fighter_one.lower():
        return fighter_two
    if winner_name.lower() == fighter_two.lower():
        return fighter_one
    return None


def _winner_side_from_names(winner: str, row, red_col, blue_col) -> str:
    red = _clean_name(row.get(red_col)) if red_col else ""
    blue = _clean_name(row.get(blue_col)) if blue_col else ""
    if winner.lower() == red.lower():
        return "red"
    if winner.lower() == blue.lower():
        return "blue"
    return "red"


def _clean_name(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_name(value) -> str:
    text = _clean_name(value).lower()
    return " ".join("".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text).split())


def _source_id(path: Path, index: int, winner: str, loser: str, method, round_number) -> str:
    raw = "|".join([str(path), str(index), winner, loser, str(method), str(round_number)])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _stat_value(row: pd.Series, aliases: list[str]) -> int | None:
    value = _first_value(row, aliases)
    if value is None:
        return None
    parsed = _parse_stat_pair(value)
    return parsed[0] if parsed else _safe_int(value)


def _stat_attempt(row: pd.Series, landed_aliases: list[str], attempted_aliases: list[str]) -> int | None:
    attempted = _first_value(row, attempted_aliases)
    if attempted is not None:
        return _safe_int(attempted)
    landed = _first_value(row, landed_aliases)
    parsed = _parse_stat_pair(landed)
    return parsed[1] if parsed else None


def _parse_stat_pair(value) -> tuple[int, int] | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip().lower().replace(" ", "")
    separator = "of" if "of" in text else "/" if "/" in text else None
    if not separator:
        return None
    parts = text.split(separator)
    if len(parts) != 2:
        return None
    landed = _safe_int(parts[0])
    attempted = _safe_int(parts[1])
    if landed is None or attempted is None:
        return None
    return landed, attempted


def _control_seconds(value) -> int | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if ":" in text:
        parts = text.split(":")
        if len(parts) == 2:
            minutes = _safe_int(parts[0])
            seconds = _safe_int(parts[1])
            if minutes is not None and seconds is not None:
                return minutes * 60 + seconds
    return _safe_int(value)


def _date_value(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return str(parsed.date())


def _prefight_flag(snapshot_value, event_value) -> bool | None:
    snapshot = pd.to_datetime(snapshot_value, errors="coerce")
    event = pd.to_datetime(event_value, errors="coerce")
    if pd.isna(snapshot) or pd.isna(event):
        return None
    return bool(snapshot <= event)


def _safe_int(value) -> int | None:
    try:
        if value is None or pd.isna(value):
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


def _sum_columns(df: pd.DataFrame, a: str, b: str) -> pd.Series:
    left = pd.to_numeric(df.get(a), errors="coerce")
    right = pd.to_numeric(df.get(b), errors="coerce")
    total = left.fillna(0) + right.fillna(0)
    total[left.isna() & right.isna()] = pd.NA
    return total


def _strike_bucket(value) -> str | None:
    if pd.isna(value):
        return None
    if value < 50:
        return "low"
    if value < 100:
        return "medium"
    return "high"


def _takedown_bucket(value) -> str | None:
    if pd.isna(value):
        return None
    if value < 1:
        return "none"
    if value < 3:
        return "moderate"
    return "heavy"


def _threshold(value, threshold: int) -> int | None:
    if pd.isna(value):
        return None
    return int(float(value) >= threshold)


def _label_availability(df: pd.DataFrame) -> dict[str, int]:
    labels = [
        "event_date",
        "method_group",
        "finish_binary",
        "goes_distance_binary",
        "round_phase_class",
        "fighter_a_sig_strikes",
        "fighter_b_sig_strikes",
        "combined_sig_strikes",
        "fighter_a_takedowns",
        "fighter_b_takedowns",
        "grappling_heavy_binary",
        "takedown_control_bucket",
    ]
    return {label: int(df[label].notna().sum()) if label in df.columns else 0 for label in labels}


def _odds_availability(odds_rows: list[tuple[Path, int]]) -> dict[str, int]:
    return {
        "files": len(odds_rows),
        "rows": sum(rows for _path, rows in odds_rows),
    }
