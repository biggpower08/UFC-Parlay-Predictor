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
from ufc_predictor.training.importers.common_schema import all_common_fields
from ufc_predictor.training.leakage import scan_dataframe
from ufc_predictor.training.dataset_builder import deterministic_fighter_orientation, safe_winner_target


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
    database_strength = _database_strength_report(combined_frame, source_reports)
    inventory = manifest_as_dict(input_root)
    payload = {
        "input_root": str(input_root),
        "datasets": source_reports,
        "combined": combined_summary,
        "database_strength": database_strength,
        "source_7_note": "UFCStats live scraping is intentionally not part of this pass; use it later for refresh/cross-checking after local datasets are stable.",
    }

    if args.write_summary or args.dry_run:
        _write_json(output_dir / "import_summary.json", payload)
        _write_json(output_dir / "source_file_inventory.json", inventory)
        _write_json(output_dir / "normalized_schema_report.json", _schema_report(combined_frame))
        _write_json(output_dir / "canonical_fights_summary.json", _canonical_fights_summary(combined_frame))
        _write_json(output_dir / "fighter_profile_summary.json", _fighter_profile_summary(combined_frame))
        _write_json(output_dir / "fighter_stats_summary.json", _fighter_stats_summary(combined_frame))
        _write_json(output_dir / "odds_summary.json", _odds_summary(combined_frame))
        _write_json(output_dir / "database_strength_report.json", database_strength)
        markdown = _markdown(payload)
        Path("docs").mkdir(exist_ok=True)
        Path("docs/imported_dataset_preprocessing_report.md").write_text(markdown, encoding="utf-8")
        Path("docs/database_strength_report.md").write_text(_database_strength_markdown(database_strength), encoding="utf-8")
    if (args.write_normalized or args.write_summary) and not args.dry_run and not combined_frame.empty:
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
        "zero_row_reason": _zero_row_reason(key, path, frame, adapter_report),
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
            "winner_model": _winner_ready(frame),
            "finish_model": _ready(frame, "fight_finished"),
            "goes_distance_model": _ready(frame, "went_distance"),
            "method_model": _ready(frame, "method_class"),
            "round_phase_model": _ready(frame, "finish_round"),
            "strike_volume_model": _ready(frame, "fighter_1_sig_strikes_landed"),
            "takedown_control_model": _ready(frame, "fighter_1_takedowns_landed"),
            "odds_calibration_model": _ready(frame, "fighter_1_moneyline", require_prefight_odds=True),
        },
    }


def _zero_row_reason(key: str, path: Path, frame: pd.DataFrame, adapter_report: dict) -> str | None:
    if len(frame):
        return None
    if not path.exists():
        return "dataset folder missing"
    if "odds" in key:
        return "odds-only dataset; retained for odds research until pre-fight timestamp quality is confirmed"
    warnings = adapter_report.get("warnings") or []
    import_warnings = adapter_report.get("import_report", {}).get("warnings") or []
    messages = []
    for warning in [*warnings, *import_warnings]:
        if warning not in messages:
            messages.append(warning)
    if messages:
        return "; ".join(messages)
    return "no supported fight rows detected by adapter"


def _database_strength_report(frame: pd.DataFrame, source_reports: dict) -> dict:
    return {
        "rows": int(len(frame)),
        "canonical_fights": _canonical_fights_summary(frame),
        "fighter_profiles": _fighter_profile_summary(frame),
        "fighter_stats": _fighter_stats_summary(frame),
        "odds": _odds_summary(frame),
        "datasets": {
            key: {
                "available": report["available"],
                "rows_normalized": report["rows_normalized"],
                "files_found": len(report["files_found"]),
                "helps_models": _helps_models(report),
                "zero_row_reason": report.get("zero_row_reason"),
                "deduping": report.get("deduping", {}),
            }
            for key, report in source_reports.items()
        },
        "missing_fields": _missing_common_fields(frame),
        "source_priority_decision": "Higher-priority UFCStats-derived result/stat datasets provide fight labels first; odds-only datasets are retained for research until timestamp quality is trusted.",
    }


def _canonical_fights_summary(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"rows": 0, "unique_fight_keys": 0, "date_range": {"min": None, "max": None}}
    return {
        "rows": int(len(frame)),
        "unique_fight_keys": int(frame["fight_key"].nunique()) if "fight_key" in frame.columns else 0,
        "unique_events": int(frame["event_name"].nunique()) if "event_name" in frame.columns else 0,
        "date_range": _date_range(frame),
        "datasets_present": sorted(frame["source_dataset"].dropna().unique().tolist()) if "source_dataset" in frame.columns else [],
    }


def _fighter_profile_summary(frame: pd.DataFrame) -> dict:
    fields = ["fighter_1_height", "fighter_2_height", "fighter_1_reach", "fighter_2_reach", "fighter_1_stance", "fighter_2_stance", "fighter_1_dob", "fighter_2_dob"]
    fighters = set()
    for column in ["fighter_1_name", "fighter_2_name"]:
        if column in frame.columns:
            fighters.update(str(value) for value in frame[column].dropna())
    return {
        "fighters_found": len(fighters),
        "field_coverage": {field: int(frame[field].notna().sum()) if field in frame.columns else 0 for field in fields},
    }


def _fighter_stats_summary(frame: pd.DataFrame) -> dict:
    fields = [
        "fighter_1_sig_strikes_landed",
        "fighter_2_sig_strikes_landed",
        "fighter_1_takedowns_landed",
        "fighter_2_takedowns_landed",
        "fighter_1_control_time_seconds",
        "fighter_2_control_time_seconds",
        "fighter_1_submission_attempts",
        "fighter_2_submission_attempts",
        "fighter_1_knockdowns",
        "fighter_2_knockdowns",
    ]
    contributors = {}
    if not frame.empty and "source_dataset" in frame.columns:
        for dataset, group in frame.groupby("source_dataset"):
            contributors[str(dataset)] = {field: int(group[field].notna().sum()) if field in group.columns else 0 for field in fields}
    return {
        "field_coverage": {field: int(frame[field].notna().sum()) if field in frame.columns else 0 for field in fields},
        "dataset_contributors": contributors,
    }


def _odds_summary(frame: pd.DataFrame) -> dict:
    fields = ["fighter_1_moneyline", "fighter_2_moneyline", "odds_snapshot_date", "odds_is_prefight"]
    trusted = 0
    if "odds_is_prefight" in frame.columns:
        trusted = int(frame["odds_is_prefight"].fillna(False).sum())
    return {
        "field_coverage": {field: int(frame[field].notna().sum()) if field in frame.columns else 0 for field in fields},
        "trusted_prefight_rows": trusted,
        "status": "training_allowed" if trusted >= 500 else "review_needed",
    }


def _missing_common_fields(frame: pd.DataFrame) -> list[str]:
    if frame.empty:
        return all_common_fields()
    return [field for field in all_common_fields() if field not in frame.columns or frame[field].notna().sum() == 0]


def _helps_models(report: dict) -> list[str]:
    labels = report.get("labels_available", {})
    helps = []
    if labels.get("f1_wins_safe", 0) or labels.get("method_class", 0):
        helps.extend(["winner_model", "finish_model", "goes_distance_model", "method_model", "round_phase_model"])
    if labels.get("fighter_1_sig_strikes_landed", 0):
        helps.append("strike_volume_model")
    if labels.get("fighter_1_takedowns_landed", 0):
        helps.append("takedown_control_model")
    if labels.get("fighter_1_moneyline", 0):
        helps.append("odds_calibration_model")
    return sorted(set(helps))


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


def _winner_ready(frame: pd.DataFrame) -> dict:
    labels = _safe_winner_labels(frame)
    rows = int(labels.notna().sum()) if not frame.empty else 0
    has_dates = "event_date" in frame.columns and frame["event_date"].notna().any() if not frame.empty else False
    distribution = labels.dropna().astype(int).astype(str).value_counts().to_dict() if rows else {}
    if rows < 500:
        return {"status": "insufficient_data", "rows": rows, "reason": "Not enough safe winner labels."}
    if not has_dates:
        return {"status": "blocked_missing_dates", "rows": rows, "reason": "Chronological split is not possible without event dates."}
    if len(distribution) < 2:
        return {
            "status": "blocked_orientation_review",
            "rows": rows,
            "class_distribution": {str(key): int(value) for key, value in distribution.items()},
            "reason": "Winner labels are present, but normalized sources appear winner-oriented; runtime fighter_1/fighter_2 orientation must be corrected before winner-model training.",
        }
    return {
        "status": "training_data_ready",
        "rows": rows,
        "class_distribution": {str(key): int(value) for key, value in distribution.items()},
        "reason": "Winner labels use deterministic fighter-name orientation independent of outcome; final model must still beat held-out baseline before production use.",
    }


def _safe_winner_labels(frame: pd.DataFrame) -> pd.Series:
    if frame.empty:
        return pd.Series(dtype="Float64")
    labels = []
    for _, row in frame.iterrows():
        f1 = row.get("fighter_1_name") or row.get("fighter_1")
        f2 = row.get("fighter_2_name") or row.get("fighter_2")
        winner = row.get("winner_name") or row.get("winner")
        if not f1 or not f2:
            labels.append(pd.NA)
            continue
        safe_f1, safe_f2, _orientation = deterministic_fighter_orientation(str(f1), str(f2))
        labels.append(safe_winner_target(safe_f1, safe_f2, str(winner) if pd.notna(winner) else None))
    return pd.Series(labels, dtype="Float64")


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
        if report.get("zero_row_reason"):
            lines.append(f"- Zero-row reason: {report['zero_row_reason']}")
        lines.append(f"- Date range: {report['date_range']}")
        lines.append(f"- Odds quality: {report['odds_timestamp_quality']}")
        lines.append(f"- Uses: {', '.join(report['recommended_uses'])}")
    lines.extend(["", "## Source 7", payload["source_7_note"]])
    return "\n".join(lines).strip() + "\n"


def _database_strength_markdown(report: dict) -> str:
    lines = [
        "# Database Strength Report",
        "",
        "## Plain-English Summary",
        "Imported local Kaggle files were normalized into fight, fighter, stats, and odds coverage summaries. Raw datasets remain local-only under `data/imports/`.",
        "",
        "## Coverage",
        f"- Normalized rows: {report['rows']}",
        f"- Canonical fight keys: {report['canonical_fights']['unique_fight_keys']}",
        f"- Fighters found: {report['fighter_profiles']['fighters_found']}",
        f"- Date range: {report['canonical_fights']['date_range']}",
        f"- Odds status: {report['odds']['status']}",
        "",
        "## Dataset Contributions",
        "| Dataset | Available | Rows | Files | Helps Models | Zero-row Reason |",
        "|---|---|---:|---:|---|---|",
    ]
    for key, item in report["datasets"].items():
        lines.append(f"| {key} | {item['available']} | {item['rows_normalized']} | {item['files_found']} | {', '.join(item['helps_models'])} | {item.get('zero_row_reason') or ''} |")
    lines.extend(["", "## Missing Common Fields"])
    for field in report["missing_fields"][:80]:
        lines.append(f"- `{field}`")
    lines.extend(["", "## Source Priority", report["source_priority_decision"]])
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
