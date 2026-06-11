from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings  # noqa: E402


EVENT_DATE_HINTS = ("event_date", "fight_date", "date", "commence_time", "event_start")
SNAPSHOT_HINTS = ("snapshot", "scrape", "collected", "collection", "downloaded", "timestamp", "last_update", "last_updated")
BOOKMAKER_HINTS = ("bookmaker", "sportsbook", "book", "provider", "site")
MARKET_HINTS = ("market", "prop", "bet_type", "outcome_type")
SELECTION_HINTS = ("fighter", "selection", "outcome", "participant", "name")
ODDS_HINTS = ("american", "decimal", "odds", "price", "moneyline")
METHOD_MARKET_TERMS = ("ko", "tko", "submission", "decision", "method")
MONEYLINE_TERMS = ("moneyline", "h2h", "winner", "win")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit local Kaggle odds files for timestamp-safe modeling use.")
    parser.add_argument("--input-dir", default="data/imports/kaggle/ufc_betting_odds_daily")
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "odds_timestamp_audit.json"))
    parser.add_argument("--output-md", default="docs/odds_timestamp_audit.md")
    args = parser.parse_args()

    payload = audit_odds_directory(Path(args.input_dir))
    write_outputs(payload, Path(args.output_json), Path(args.output_md))
    print(json.dumps({"status": payload["status"], "output_json": args.output_json, "output_md": args.output_md}, indent=2))
    return 0 if payload["status"] in {"timestamp_audit_passed_research_only", "blocked_no_files"} else 1


def audit_odds_directory(input_dir: Path) -> dict[str, Any]:
    files = discover_data_files(input_dir)
    file_reports = [audit_odds_file(path) for path in files]
    totals = summarize_reports(file_reports)
    status = classify_timestamp_safety(totals)
    return {
        "generated_at": utc_now(),
        "input_dir": str(input_dir),
        "status": status,
        "plain_english_summary": summary_text(status),
        "odds_calibration_model_status": "blocked",
        "safe_for": safe_modes(status, totals),
        "totals": totals,
        "files": file_reports,
        "decision_rules": [
            "Rows without trusted snapshot timestamps cannot train production odds models.",
            "Rows where snapshot timestamps are after event/fight dates are blocked for pre-fight prediction.",
            "Closing odds can only train closing-line mode unless earlier collection timestamps exist.",
            "odds_calibration_model remains blocked until timestamp safety passes and production modeling review is complete.",
        ],
    }


def discover_data_files(input_dir: Path) -> list[Path]:
    if not input_dir.exists():
        return []
    suffixes = {".csv", ".tsv", ".json", ".jsonl", ".parquet"}
    return [path for path in sorted(input_dir.rglob("*")) if path.is_file() and path.suffix.lower() in suffixes]


def audit_odds_file(path: Path) -> dict[str, Any]:
    try:
        frame = read_data_file(path)
    except Exception as exc:
        return {"source_file": str(path), "status": "failed_read", "error": str(exc)[-1000:]}
    columns = list(frame.columns)
    event_cols = matching_columns(columns, EVENT_DATE_HINTS)
    snapshot_cols = [col for col in matching_columns(columns, SNAPSHOT_HINTS) if col not in event_cols]
    bookmaker_cols = matching_columns(columns, BOOKMAKER_HINTS)
    market_cols = matching_columns(columns, MARKET_HINTS)
    selection_cols = matching_columns(columns, SELECTION_HINTS)
    odds_cols = matching_columns(columns, ODDS_HINTS)
    event_col = first_parseable_datetime_column(frame, event_cols)
    snapshot_col = first_parseable_datetime_column(frame, snapshot_cols)
    event_dates = parse_datetime_series(frame[event_col]) if event_col else empty_datetime_series(len(frame))
    snapshot_dates = parse_datetime_series(frame[snapshot_col]) if snapshot_col else empty_datetime_series(len(frame))
    market_values = combined_text(frame, market_cols)
    odds_values = combined_text(frame, odds_cols)
    timestamp_after_event = int(((snapshot_dates.notna()) & (event_dates.notna()) & (snapshot_dates > event_dates)).sum())
    duplicate_subset = [col for col in [event_col, snapshot_col, *(market_cols[:2]), *(selection_cols[:2]), *(bookmaker_cols[:1])] if col]
    duplicate_snapshots = int(frame.duplicated(subset=duplicate_subset).sum()) if duplicate_subset else 0
    timezone_ambiguous = timestamp_col_timezone_ambiguous(frame, snapshot_col)
    return {
        "source_file": str(path),
        "status": "audited",
        "rows": int(len(frame)),
        "sha256": sha256(path),
        "columns_present": columns,
        "event_date_columns": event_cols,
        "fight_date_columns": [col for col in event_cols if "fight" in col.lower()],
        "collection_timestamp_columns": snapshot_cols,
        "selected_event_date_column": event_col,
        "selected_snapshot_timestamp_column": snapshot_col,
        "bookmaker_columns": bookmaker_cols,
        "market_type_columns": market_cols,
        "fighter_selection_columns": selection_cols,
        "odds_columns": odds_cols,
        "moneyline_rows": int(market_values.str.contains("|".join(MONEYLINE_TERMS), case=False, na=False).sum()) if not market_values.empty else int(odds_values.str.contains("moneyline", case=False, na=False).sum()),
        "method_prop_rows": int(market_values.str.contains("|".join(METHOD_MARKET_TERMS), case=False, na=False).sum()) if not market_values.empty else 0,
        "missing_snapshot_timestamp_rows": int(snapshot_dates.isna().sum()) if snapshot_col else int(len(frame)),
        "missing_event_date_rows": int(event_dates.isna().sum()) if event_col else int(len(frame)),
        "snapshot_after_event_rows": timestamp_after_event,
        "timestamp_timezone_ambiguous": timezone_ambiguous,
        "duplicate_snapshots": duplicate_snapshots,
        "append_only_history_supported": bool(snapshot_col and snapshot_dates.nunique(dropna=True) > 1),
    }


def read_data_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, low_memory=False)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t", low_memory=False)
    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        return pd.read_json(path)
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise ValueError(f"Unsupported odds audit file type: {path.suffix}")


def matching_columns(columns: list[str], hints: tuple[str, ...]) -> list[str]:
    return [column for column in columns if any(hint in column.lower() for hint in hints)]


def first_parseable_datetime_column(frame: pd.DataFrame, candidates: list[str]) -> str | None:
    best = None
    best_count = 0
    for column in candidates:
        parsed = pd.to_datetime(frame[column], errors="coerce", utc=True)
        count = int(parsed.notna().sum())
        if count > best_count:
            best = column
            best_count = count
    return best if best_count > 0 else None


def parse_datetime_series(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce", utc=True)


def empty_datetime_series(length: int) -> pd.Series:
    return pd.to_datetime(pd.Series([None] * length), errors="coerce", utc=True)


def combined_text(frame: pd.DataFrame, columns: list[str]) -> pd.Series:
    if not columns:
        return pd.Series([], dtype=str)
    values = frame[columns].fillna("").astype(str)
    return values.apply(lambda row: " ".join(row.values), axis=1)


def timestamp_col_timezone_ambiguous(frame: pd.DataFrame, column: str | None) -> bool:
    if not column:
        return True
    sample = frame[column].dropna().astype(str).head(100)
    if sample.empty:
        return True
    return not sample.str.contains(r"Z|[+-]\d{2}:?\d{2}|UTC", case=False, regex=True).any()


def summarize_reports(reports: list[dict[str, Any]]) -> dict[str, Any]:
    audited = [report for report in reports if report.get("status") == "audited"]
    return {
        "available_files": len(reports),
        "audited_files": len(audited),
        "total_rows": sum(int(report.get("rows", 0)) for report in audited),
        "missing_snapshot_timestamp_rows": sum(int(report.get("missing_snapshot_timestamp_rows", 0)) for report in audited),
        "missing_event_date_rows": sum(int(report.get("missing_event_date_rows", 0)) for report in audited),
        "snapshot_after_event_rows": sum(int(report.get("snapshot_after_event_rows", 0)) for report in audited),
        "timezone_ambiguous_files": sum(1 for report in audited if report.get("timestamp_timezone_ambiguous")),
        "moneyline_rows": sum(int(report.get("moneyline_rows", 0)) for report in audited),
        "method_prop_rows": sum(int(report.get("method_prop_rows", 0)) for report in audited),
        "duplicate_snapshots": sum(int(report.get("duplicate_snapshots", 0)) for report in audited),
        "append_only_history_supported": any(report.get("append_only_history_supported") for report in audited),
    }


def classify_timestamp_safety(totals: dict[str, Any]) -> str:
    if totals["available_files"] == 0:
        return "blocked_no_files"
    if totals["audited_files"] == 0:
        return "blocked_unreadable_files"
    if totals["missing_snapshot_timestamp_rows"] > 0:
        return "blocked_missing_snapshot_timestamps"
    if totals["missing_event_date_rows"] > 0:
        return "blocked_missing_event_dates"
    if totals["snapshot_after_event_rows"] > 0:
        return "blocked_post_event_snapshots"
    if totals["timezone_ambiguous_files"] > 0:
        return "research_only_timezone_ambiguous"
    return "timestamp_audit_passed_research_only"


def safe_modes(status: str, totals: dict[str, Any]) -> dict[str, str]:
    if status != "timestamp_audit_passed_research_only":
        return {
            "research_only": "allowed_for_manual_review",
            "opening_odds_model": "blocked",
            "24h_prefight_model": "blocked",
            "closing_line_model": "blocked_or_manual_review_only",
            "production_odds_model": "blocked",
        }
    return {
        "research_only": "allowed",
        "opening_odds_model": "needs_cutoff_specific_review",
        "24h_prefight_model": "needs_cutoff_specific_review",
        "closing_line_model": "allowed_only_if_marked_closing",
        "production_odds_model": "blocked_until_model_review",
    }


def summary_text(status: str) -> str:
    if status == "timestamp_audit_passed_research_only":
        return "Odds files have parseable event dates and snapshot timestamps, but odds models remain blocked until cutoff-specific modeling review."
    if status == "blocked_no_files":
        return "No local odds files were found. Download or place raw Kaggle odds files locally before auditing."
    return "Odds timestamp safety is not proven, so odds modeling remains blocked."


def write_outputs(payload: dict[str, Any], output_json: Path, output_md: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown_report(payload), encoding="utf-8")


def markdown_report(payload: dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        "# Odds Timestamp Audit",
        "",
        "## Plain-English Summary",
        payload["plain_english_summary"],
        "",
        "## Decision",
        f"- Status: {payload['status']}",
        f"- Odds calibration model: {payload['odds_calibration_model_status']}",
        f"- Files found: {totals['available_files']}",
        f"- Rows audited: {totals['total_rows']}",
        f"- Missing snapshot timestamp rows: {totals['missing_snapshot_timestamp_rows']}",
        f"- Missing event date rows: {totals['missing_event_date_rows']}",
        f"- Snapshot-after-event rows: {totals['snapshot_after_event_rows']}",
        f"- Timezone ambiguous files: {totals['timezone_ambiguous_files']}",
        f"- Moneyline rows detected: {totals['moneyline_rows']}",
        f"- Method prop rows detected: {totals['method_prop_rows']}",
        "",
        "## Safe Modes",
    ]
    for mode, status in payload["safe_for"].items():
        lines.append(f"- {mode}: {status}")
    lines.extend(["", "## Files"])
    if not payload["files"]:
        lines.append("- No files found.")
    for report in payload["files"]:
        lines.append(f"- `{report.get('source_file')}`: {report.get('status')}, rows={report.get('rows', 0)}")
    lines.extend(
        [
            "",
            "## Leakage Rules",
            "- `snapshot_timestamp` must be before the prediction cutoff.",
            "- Prediction cutoff must be before fight/event start.",
            "- Rows without trusted timestamps cannot train production odds models.",
            "- Closing odds are only safe for closing-line mode.",
            "- Odds snapshots should be append-only and preserve collection history.",
        ]
    )
    return "\n".join(lines)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
