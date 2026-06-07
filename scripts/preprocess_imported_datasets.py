from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.training.dataset_manifest import DATASET_MANIFEST, manifest_as_dict
from ufc_predictor.training.deduping import add_deduping_columns, dedupe_summary
from ufc_predictor.training.importers.github_adapter import adapt_github_dataset
from ufc_predictor.training.importers.kaggle_adapter import adapt_kaggle_dataset
from ufc_predictor.training.leakage import scan_dataframe


def main() -> int:
    parser = argparse.ArgumentParser(description="Preprocess supported local UFC/MMA raw datasets into normalized audit outputs.")
    parser.add_argument("--input-root", default="data/imports")
    parser.add_argument("--only", choices=sorted(DATASET_MANIFEST))
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output-dir", default="ufc_predictor/data/processed/imports")
    parser.add_argument("--write-normalized", action="store_true")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--max-preview-rows", type=int, default=20)
    args = parser.parse_args()

    if not args.all and not args.only:
        print(json.dumps({"error": "choose --all or --only DATASET_KEY"}, indent=2))
        return 1

    keys = [args.only] if args.only else sorted(DATASET_MANIFEST, key=lambda key: DATASET_MANIFEST[key].priority)
    input_root = Path(args.input_root)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = []
    source_reports = {}
    for key in keys:
        entry = DATASET_MANIFEST[key]
        source_path = _resolve_source_path(input_root, entry)
        frame, report = _adapt(entry.source_type, key, source_path, dry_run=args.dry_run)
        normalized = add_deduping_columns(frame) if not frame.empty else frame
        if not normalized.empty:
            combined.append(normalized)
        source_reports[key] = _source_report(key, source_path, normalized, report, args.max_preview_rows)

    combined_frame = pd.concat(combined, ignore_index=True) if combined else pd.DataFrame()
    combined_summary = _combined_report(combined_frame)
    inventory = manifest_as_dict(input_root)
    payload = {
        "input_root": str(input_root),
        "datasets": source_reports,
        "combined": combined_summary,
        "source_7_note": "UFCStats live scraping is intentionally not part of this pass; use it later for refresh/cross-checking after local datasets are stable.",
    }

    if args.write_summary or args.dry_run:
        _write_json(output_dir / "import_summary.json", payload)
        _write_json(output_dir / "source_file_inventory.json", inventory)
        _write_json(output_dir / "normalized_schema_report.json", _schema_report(combined_frame))
        markdown = _markdown(payload)
        Path("docs").mkdir(exist_ok=True)
        Path("docs/imported_dataset_preprocessing_report.md").write_text(markdown, encoding="utf-8")
    if args.write_normalized and not args.dry_run and not combined_frame.empty:
        combined_frame.to_csv(output_dir / "normalized_fights_combined.csv", index=False)

    print(json.dumps({"output_dir": str(output_dir), "datasets": list(source_reports), "combined": combined_summary}, indent=2, default=str))
    return 0


def _resolve_source_path(input_root: Path, entry) -> Path:
    clean_path = input_root / Path(entry.local_path).relative_to("data/imports")
    slug_path = input_root / entry.source_slug_or_repo.replace("/", "__")
    kaggle_slug_path = input_root / "kaggle" / entry.source_slug_or_repo.replace("/", "__")
    github_name_path = input_root / "github" / Path(entry.local_path).name
    for path in [clean_path, slug_path, kaggle_slug_path, github_name_path]:
        if path.exists():
            return path
    return clean_path


def _adapt(source_type: str, key: str, folder: Path, dry_run: bool):
    if source_type == "github":
        return adapt_github_dataset(key, folder, dry_run=dry_run)
    return adapt_kaggle_dataset(key, folder, dry_run=dry_run)


def _source_report(key: str, path: Path, frame: pd.DataFrame, adapter_report: dict, preview_rows: int) -> dict:
    leakage = scan_dataframe(frame.head(preview_rows)) if not frame.empty else {"summary": {}, "blocked_feature_columns": []}
    odds_quality = _odds_quality(frame)
    return {
        "dataset_key": key,
        "path": str(path),
        "available": path.exists(),
        "files_found": [str(file) for file in sorted(path.rglob("*")) if file.is_file()] if path.exists() else [],
        "rows_normalized": int(len(frame)),
        "column_count": int(len(frame.columns)) if not frame.empty else 0,
        "date_range": _date_range(frame),
        "unique_fighters": _unique_fighters(frame),
        "deduping": dedupe_summary(frame),
        "labels_available": _labels_available(frame),
        "leakage_summary": leakage.get("summary", {}),
        "blocked_columns_preview": leakage.get("blocked_feature_columns", [])[:30],
        "odds_timestamp_quality": odds_quality,
        "recommended_uses": DATASET_MANIFEST[key].intended_uses,
        "known_risks": DATASET_MANIFEST[key].known_risks,
        "adapter_report": adapter_report,
    }


def _combined_report(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "datasets_present": sorted(frame["source_dataset"].dropna().unique().tolist()) if "source_dataset" in frame.columns and not frame.empty else [],
        "date_range": _date_range(frame),
        "deduping": dedupe_summary(frame),
        "model_readiness": {
            "winner_model": _ready(frame, "f1_wins_safe"),
            "finish_model": _ready(frame, "fight_finished"),
            "goes_distance_model": _ready(frame, "went_distance"),
            "method_model": _ready(frame, "method_class"),
            "round_phase_model": _ready(frame, "finish_round"),
            "strike_volume_model": _ready(frame, "fighter_1_sig_strikes_landed"),
            "takedown_control_model": _ready(frame, "fighter_1_takedowns_landed"),
            "odds_calibration_model": _ready(frame, "fighter_1_moneyline", require_prefight_odds=True),
        },
    }


def _ready(frame: pd.DataFrame, column: str, require_prefight_odds: bool = False) -> dict:
    rows = int(frame[column].notna().sum()) if column in frame.columns and not frame.empty else 0
    has_dates = "event_date" in frame.columns and frame["event_date"].notna().any() if not frame.empty else False
    if require_prefight_odds and ("odds_is_prefight" not in frame.columns or not frame["odds_is_prefight"].fillna(False).any()):
        return {"status": "review_needed", "rows": rows, "reason": "Odds timestamp quality is not confirmed as pre-fight."}
    if rows >= 500 and has_dates:
        return {"status": "training_data_ready", "rows": rows}
    if rows:
        return {"status": "experimental_or_insufficient_dates", "rows": rows}
    return {"status": "insufficient_data", "rows": 0}


def _schema_report(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "columns": sorted(frame.columns.tolist()) if not frame.empty else [],
        "non_null_counts": {column: int(frame[column].notna().sum()) for column in frame.columns} if not frame.empty else {},
    }


def _labels_available(frame: pd.DataFrame) -> dict:
    columns = [
        "f1_wins_safe",
        "fight_finished",
        "went_distance",
        "method_class",
        "finish_round",
        "fighter_1_sig_strikes_landed",
        "fighter_1_takedowns_landed",
        "fighter_1_moneyline",
    ]
    return {column: int(frame[column].notna().sum()) if column in frame.columns and not frame.empty else 0 for column in columns}


def _date_range(frame: pd.DataFrame) -> dict:
    if frame.empty or "event_date" not in frame.columns:
        return {"min": None, "max": None}
    dates = pd.to_datetime(frame["event_date"], errors="coerce").dropna()
    return {"min": str(dates.min().date()) if not dates.empty else None, "max": str(dates.max().date()) if not dates.empty else None}


def _unique_fighters(frame: pd.DataFrame) -> int:
    if frame.empty:
        return 0
    fighters = set()
    for column in ["fighter_1_name", "fighter_2_name", "winner_name", "loser_name"]:
        if column in frame.columns:
            fighters.update(str(value) for value in frame[column].dropna())
    return len(fighters)


def _odds_quality(frame: pd.DataFrame) -> str:
    if frame.empty or "fighter_1_moneyline" not in frame.columns or frame["fighter_1_moneyline"].notna().sum() == 0:
        return "unavailable"
    if "odds_is_prefight" in frame.columns and frame["odds_is_prefight"].fillna(False).any():
        return "prefight_available"
    return "review_needed"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def _markdown(payload: dict) -> str:
    lines = [
        "# Imported Dataset Preprocessing Report",
        "",
        "Raw data remains under `data/imports/` and is not committed.",
        "",
        "## Combined Readiness",
    ]
    for model, status in payload["combined"]["model_readiness"].items():
        lines.append(f"- `{model}`: {status.get('status')} ({status.get('rows', 0)} rows). {status.get('reason', '')}")
    lines.extend(["", "## Dataset Summaries"])
    for key, report in payload["datasets"].items():
        lines.append(f"### {key}")
        lines.append(f"- Available: {report['available']}")
        lines.append(f"- Rows normalized: {report['rows_normalized']}")
        lines.append(f"- Date range: {report['date_range']}")
        lines.append(f"- Odds quality: {report['odds_timestamp_quality']}")
        lines.append(f"- Uses: {', '.join(report['recommended_uses'])}")
    lines.extend(["", "## Source 7", payload["source_7_note"]])
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
