from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings  # noqa: E402


MARKET_COLUMNS = {
    "odds_1": ("moneyline", None, "fighter_1"),
    "odds_2": ("moneyline", None, "fighter_2"),
    "f1_ko_odds": ("ko_tko_prop", "ko_tko", "fighter_1"),
    "f2_ko_odds": ("ko_tko_prop", "ko_tko", "fighter_2"),
    "f1_sub_odds": ("submission_prop", "submission", "fighter_1"),
    "f2_sub_odds": ("submission_prop", "submission", "fighter_2"),
    "f1_dec_odds": ("decision_prop", "decision", "fighter_1"),
    "f2_dec_odds": ("decision_prop", "decision", "fighter_2"),
}
REJECTION_KEYS = [
    "missing_snapshot_timestamp",
    "missing_event_date",
    "snapshot_after_event",
    "invalid_odds",
    "unmapped_selection",
    "unknown_market_type",
    "duplicate_snapshot",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize timestamp-safe UFC daily odds rows into a research-only preview.")
    parser.add_argument("--input-file", default="data/imports/kaggle/ufc_betting_odds_daily/UFC_betting_odds.csv")
    parser.add_argument("--preview-json", default=str(settings.DATA_PROCESSED_DIR / "odds_snapshots_preview.json"))
    parser.add_argument("--summary-json", default=str(settings.DATA_PROCESSED_DIR / "odds_snapshots_preview_summary.json"))
    parser.add_argument("--full-output-csv", default=str(settings.DATA_PROCESSED_DIR / "training_imports" / "odds_snapshots_preview.csv"))
    parser.add_argument("--report-md", default="docs/odds_snapshot_normalization_report.md")
    parser.add_argument("--preview-limit", type=int, default=500)
    args = parser.parse_args()

    result = normalize_odds_file(Path(args.input_file))
    write_outputs(
        result,
        preview_json=Path(args.preview_json),
        summary_json=Path(args.summary_json),
        full_output_csv=Path(args.full_output_csv),
        report_md=Path(args.report_md),
        preview_limit=args.preview_limit,
    )
    print(json.dumps({"status": "ok", "accepted_snapshots": result["summary"]["accepted_snapshots"], "summary_json": args.summary_json}, indent=2))
    return 0


def normalize_odds_file(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Odds input file not found: {path}")
    raw = pd.read_csv(path, low_memory=False)
    event_dates = parse_datetime(raw.get("event_date"))
    snapshot_dates = parse_datetime(raw.get("adding_date"))
    accepted: list[dict[str, Any]] = []
    rejection_counts = Counter({key: 0 for key in REJECTION_KEYS})
    raw_rejected_rows = set()
    duplicate_keys = set()
    seen_snapshot_keys = set()

    records = raw.to_dict("records")
    event_date_values = event_dates.tolist()
    snapshot_date_values = snapshot_dates.tolist()
    available_market_columns = [column for column in MARKET_COLUMNS if column in raw.columns]

    for index, row in enumerate(records):
        event_date = event_date_values[index]
        snapshot_timestamp = snapshot_date_values[index]
        base_reasons = []
        if pd.isna(snapshot_timestamp):
            base_reasons.append("missing_snapshot_timestamp")
        if pd.isna(event_date):
            base_reasons.append("missing_event_date")
        if not pd.isna(snapshot_timestamp) and not pd.isna(event_date) and snapshot_timestamp > event_date:
            base_reasons.append("snapshot_after_event")
        if base_reasons:
            for reason in base_reasons:
                rejection_counts[reason] += 1
            raw_rejected_rows.add(index)
            continue
        for column in available_market_columns:
            market_type, prop_type, side = MARKET_COLUMNS[column]
            snapshot = normalize_market_row(row, column, market_type, prop_type, side, event_date, snapshot_timestamp, path, index)
            if snapshot.get("reject_reason"):
                rejection_counts[snapshot["reject_reason"]] += 1
                continue
            duplicate_key = (
                snapshot["fight_key_candidate"],
                snapshot["snapshot_timestamp"],
                snapshot["selection"],
                snapshot["market_type"],
                snapshot["bookmaker"],
                snapshot["region"],
                snapshot["decimal_odds"],
            )
            if duplicate_key in seen_snapshot_keys:
                rejection_counts["duplicate_snapshot"] += 1
                duplicate_keys.add(duplicate_key)
                continue
            seen_snapshot_keys.add(duplicate_key)
            accepted.append(snapshot)

    accepted_df = pd.DataFrame(accepted)
    summary = build_summary(path, raw, accepted_df, rejection_counts, raw_rejected_rows, duplicate_keys)
    return {"summary": summary, "snapshots": accepted}


def normalize_market_row(
    row: dict[str, Any],
    odds_column: str,
    market_type: str,
    prop_type: str | None,
    side: str,
    event_date,
    snapshot_timestamp,
    source_file: Path,
    row_index: int,
) -> dict[str, Any]:
    fighter = clean_text(row.get(side))
    opponent_side = "fighter_2" if side == "fighter_1" else "fighter_1"
    opponent = clean_text(row.get(opponent_side))
    if not fighter or not opponent:
        return {"reject_reason": "unmapped_selection"}
    odds = parse_odds(row.get(odds_column))
    if odds is None:
        return {"reject_reason": "invalid_odds"}
    days_before = (event_date - snapshot_timestamp).total_seconds() / 86400
    fight_url = clean_text(row.get("fight_url"))
    source_row_hash = stable_hash([str(source_file), str(row_index), fight_url, odds_column, fighter, str(row.get(odds_column)), str(snapshot_timestamp)])
    snapshot_id = stable_hash([source_row_hash, market_type, fighter, clean_text(row.get("source")), clean_text(row.get("region"))])
    return {
        "snapshot_id": snapshot_id,
        "fight_url": fight_url,
        "fight_key_candidate": fight_key_candidate(fight_url, row),
        "event_date": event_date.isoformat(),
        "snapshot_timestamp": snapshot_timestamp.isoformat(),
        "days_before_event": round(days_before, 4),
        "fighter_1": clean_text(row.get("fighter_1")),
        "fighter_2": clean_text(row.get("fighter_2")),
        "selection": fighter,
        "selection_side": side,
        "opponent": opponent,
        "market_type": market_type,
        "prop_type": prop_type,
        "bookmaker": clean_text(row.get("source")),
        "region": clean_text(row.get("region")),
        "source_dataset": "ufc_betting_odds_daily",
        "source_file": str(source_file),
        "source_raw_row_index": row_index,
        "source_row_hash": source_row_hash,
        "raw_odds": row.get(odds_column),
        "american_odds": odds["american_odds"],
        "decimal_odds": odds["decimal_odds"],
        "implied_probability": odds["implied_probability"],
        "timestamp_audit_status": "timestamp_safe_prefight_candidate",
        "prediction_modes_allowed": prediction_modes(days_before, event_date),
        "normalization_warnings": [],
    }


def parse_odds(value) -> dict[str, float | None] | None:
    if value is None or pd.isna(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number) or number == 0:
        return None
    if abs(number) >= 100:
        return american_odds_to_decimal_probability(number)
    # The downloaded UFC daily file stores decimal odds. Keep American odds null
    # unless a future source clearly uses American odds.
    if number > 1:
        return {"american_odds": None, "decimal_odds": round(number, 6), "implied_probability": round(1 / number, 8)}
    return None


def american_odds_to_decimal_probability(american_odds: float) -> dict[str, float] | None:
    if american_odds == 0 or abs(american_odds) < 100:
        return None
    if american_odds > 0:
        decimal = 1 + american_odds / 100
        implied = 100 / (american_odds + 100)
    else:
        absolute = abs(american_odds)
        decimal = 1 + 100 / absolute
        implied = absolute / (absolute + 100)
    return {"american_odds": round(american_odds, 2), "decimal_odds": round(decimal, 6), "implied_probability": round(implied, 8)}


def prediction_modes(days_before_event: float, event_date) -> list[str]:
    modes = ["research_only"]
    if days_before_event >= 7:
        modes.append("early_prefight_candidate")
    if days_before_event >= 1:
        modes.append("day_before_candidate")
    if 0 <= days_before_event < 1:
        modes.append("closing_line_candidate")
    now = pd.Timestamp(datetime.now(timezone.utc))
    if event_date > now:
        modes.append("future_event_candidate")
    return modes


def build_summary(path: Path, raw: pd.DataFrame, accepted_df: pd.DataFrame, rejection_counts: Counter, raw_rejected_rows: set[int], duplicate_keys: set) -> dict[str, Any]:
    event_dates = parse_datetime(raw.get("event_date"))
    snapshot_dates = parse_datetime(raw.get("adding_date"))
    mode_counts = Counter()
    if not accepted_df.empty:
        for modes in accepted_df["prediction_modes_allowed"]:
            for mode in modes:
                mode_counts[mode] += 1
    market_counts = counter_dict(accepted_df, "market_type")
    for market_type in ("moneyline", "ko_tko_prop", "submission_prop", "decision_prop"):
        market_counts.setdefault(market_type, 0)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(path),
        "source_file_size_bytes": path.stat().st_size,
        "total_raw_rows": int(len(raw)),
        "accepted_raw_rows": int(accepted_df["source_raw_row_index"].nunique()) if not accepted_df.empty else 0,
        "rejected_raw_rows": int(len(raw_rejected_rows)),
        "accepted_snapshots": int(len(accepted_df)),
        "rejected_snapshots_by_reason": {key: int(rejection_counts.get(key, 0)) for key in REJECTION_KEYS},
        "normalized_market_counts": market_counts,
        "bookmaker_counts": counter_dict(accepted_df, "bookmaker", limit=20),
        "region_counts": counter_dict(accepted_df, "region", limit=20),
        "event_date_range": date_range(event_dates),
        "snapshot_timestamp_range": date_range(snapshot_dates),
        "accepted_event_date_range": date_range(pd.to_datetime(accepted_df["event_date"], errors="coerce", utc=True)) if not accepted_df.empty else {"min": None, "max": None},
        "accepted_snapshot_timestamp_range": date_range(pd.to_datetime(accepted_df["snapshot_timestamp"], errors="coerce", utc=True)) if not accepted_df.empty else {"min": None, "max": None},
        "days_before_event_distribution": days_distribution(accepted_df),
        "future_event_snapshot_count": int(mode_counts.get("future_event_candidate", 0)),
        "duplicate_snapshot_count": int(rejection_counts.get("duplicate_snapshot", 0)),
        "duplicate_snapshot_unique_keys": int(len(duplicate_keys)),
        "safe_modes_summary": dict(sorted(mode_counts.items())),
        "odds_calibration_model_status": "blocked",
        "odds_snapshots_preview_status": "research_only",
        "limitations": [
            "Timestamp-safe subset exists, but fight mapping/modeling review is incomplete.",
            "Historical coverage starts from snapshot dates, not from earliest event dates.",
            "Rows with missing adding_date or adding_date after event_date are excluded from pre-fight preview.",
            "No odds-aware model has been trained or audited.",
        ],
    }


def write_outputs(result: dict[str, Any], preview_json: Path, summary_json: Path, full_output_csv: Path, report_md: Path, preview_limit: int) -> None:
    summary = result["summary"]
    snapshots = result["snapshots"]
    summary_json.parent.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    preview_json.parent.mkdir(parents=True, exist_ok=True)
    preview_json.write_text(json.dumps({"summary": summary, "preview_limit": preview_limit, "snapshots": snapshots[:preview_limit]}, indent=2, default=str), encoding="utf-8")
    full_output_csv.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(snapshots).to_csv(full_output_csv, index=False)
    report_md.parent.mkdir(parents=True, exist_ok=True)
    report_md.write_text(markdown_report(summary, preview_json, full_output_csv), encoding="utf-8")


def markdown_report(summary: dict[str, Any], preview_json: Path, full_output_csv: Path) -> str:
    lines = [
        "# Odds Snapshot Normalization Report",
        "",
        "## Plain-English Summary",
        "Timestamp-safe UFC daily odds rows were normalized into a research-only odds_snapshots preview. Odds calibration remains blocked because mapping/modeling review is incomplete and the source contains missing/post-event timestamp rows.",
        "",
        "## Source File",
        f"- File: `{summary['source_file']}`",
        f"- Raw rows: {summary['total_raw_rows']}",
        f"- File size bytes: {summary['source_file_size_bytes']}",
        "",
        "## Accepted And Rejected Rows",
        f"- Accepted raw rows: {summary['accepted_raw_rows']}",
        f"- Rejected raw rows: {summary['rejected_raw_rows']}",
        f"- Accepted normalized snapshots: {summary['accepted_snapshots']}",
    ]
    lines.append("")
    lines.append("## Rejections By Reason")
    for key, value in summary["rejected_snapshots_by_reason"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Normalized Market Counts")
    for key, value in summary["normalized_market_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Bookmaker / Source Counts")
    for key, value in summary["bookmaker_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## Region Counts")
    for key, value in summary["region_counts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Date Ranges",
            f"- Raw event date range: {summary['event_date_range']}",
            f"- Raw snapshot timestamp range: {summary['snapshot_timestamp_range']}",
            f"- Accepted event date range: {summary['accepted_event_date_range']}",
            f"- Accepted snapshot timestamp range: {summary['accepted_snapshot_timestamp_range']}",
            "",
            "## Days Before Event Distribution",
        ]
    )
    for key, value in summary["days_before_event_distribution"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Safe Modes Summary",
        ]
    )
    for key, value in summary["safe_modes_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Outputs",
            f"- Committed preview JSON: `{preview_json}`",
            f"- Full local CSV preview: `{full_output_csv}` (ignored by Git)",
            "",
            "## Why odds_calibration_model Remains Blocked",
            "- The source contains missing snapshot timestamps and post-event snapshots.",
            "- The normalized subset is research-only until fight mapping and prediction cutoff review are complete.",
            "- No odds-aware model has been trained or audited.",
        ]
    )
    return "\n".join(lines)


def parse_datetime(series) -> pd.Series:
    if series is None:
        return pd.Series(dtype="datetime64[ns, UTC]")
    try:
        return pd.to_datetime(series, errors="coerce", utc=True, format="mixed")
    except TypeError:
        return pd.to_datetime(series, errors="coerce", utc=True)


def clean_text(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    return text or None


def fight_key_candidate(fight_url: str | None, row: dict[str, Any]) -> str:
    if fight_url:
        return fight_url.rstrip("/").split("/")[-1]
    return stable_hash([row.get("event_date"), row.get("fighter_1"), row.get("fighter_2")])


def stable_hash(parts: list[Any]) -> str:
    joined = "|".join("" if part is None else str(part) for part in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:24]


def counter_dict(frame: pd.DataFrame, column: str, limit: int | None = None) -> dict[str, int]:
    if frame.empty or column not in frame.columns:
        return {}
    counts = frame[column].fillna("unknown").astype(str).value_counts()
    if limit:
        counts = counts.head(limit)
    return {str(key): int(value) for key, value in counts.items()}


def date_range(series: pd.Series) -> dict[str, str | None]:
    if series.empty or series.dropna().empty:
        return {"min": None, "max": None}
    return {"min": series.min().isoformat(), "max": series.max().isoformat()}


def days_distribution(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty:
        return {}
    values = pd.to_numeric(frame["days_before_event"], errors="coerce")
    return {
        "0_to_1_days": int(((values >= 0) & (values < 1)).sum()),
        "1_to_7_days": int(((values >= 1) & (values < 7)).sum()),
        "7_to_30_days": int(((values >= 7) & (values < 30)).sum()),
        "30_plus_days": int((values >= 30).sum()),
    }


if __name__ == "__main__":
    raise SystemExit(main())
