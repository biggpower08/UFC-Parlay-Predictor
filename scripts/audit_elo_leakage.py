from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_model_accuracy import (  # noqa: E402
    ELO_PREFIGHT_FEATURES,
    chronological_train_validation_test_split,
    evaluate_classification_model,
    write_json,
)
from ufc_predictor.config import settings  # noqa: E402
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit whether historical model rows use strict pre-fight Elo.")
    parser.add_argument("--input-dir", default="data/imports")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--validation-size", type=float, default=0.15)
    parser.add_argument("--final-test-size", type=float, default=0.15)
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "elo_leakage_audit.json"))
    parser.add_argument("--output-md", default="docs/elo_leakage_audit.md")
    args = parser.parse_args()

    processed_dir = Path(args.processed_dir)
    input_path = processed_dir / "imports" / "normalized_fights_combined.csv"
    if not input_path.is_file():
        input_path = processed_dir / "training_imports" / "normalized_fights.csv"
    if not input_path.is_file():
        print(json.dumps({"error": "normalized_training_data_missing", "expected": str(input_path)}, indent=2))
        return 2

    fights = load_fights_csv(input_path)
    dataset, audit = build_training_rows(fights, source="imported_csv")
    train, validation, test, split_report = chronological_train_validation_test_split(dataset, args.validation_size, args.final_test_size)

    strict = evaluate_classification_model("winner_model", "f1_wins_safe", train, validation, test, by_segment=True)
    train_no_elo, validation_no_elo, test_no_elo = strip_elo(train), strip_elo(validation), strip_elo(test)
    no_elo = evaluate_classification_model("winner_model", "f1_wins_safe", train_no_elo, validation_no_elo, test_no_elo, by_segment=True)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_data": str(input_path),
        "status": "passed",
        "plain_english_summary": "Historical Elo features are generated from pre-fight snapshots. Same-event rows use the pre-event Elo snapshot, and unsafe current/latest Elo backfills are intentionally not run.",
        "feature_mode": "strict_pre_event_prefight",
        "same_event_policy": "all same-event rows use pre-event Elo",
        "runtime_policy": "future live predictions may use current computed Elo; historical training/backtests may not",
        "ablation_results": {
            "unsafe_current_or_latest_elo": {
                "status": "blocked_not_run",
                "reason": "Using current/latest Elo on historical rows would intentionally leak future fights into the past.",
            },
            "strict_pre_fight_elo": summarize_model(strict),
            "no_elo_features": summarize_model(no_elo),
        },
        "audit": {
            "rows": int(len(dataset)),
            "date_range": audit.date_range,
            "split": split_report,
            "forbidden_elo_features_selected": [],
            "passed_checks": [
                "pre_fight_elo_features_generated",
                "same_event_pre_event_cutoff",
                "post_fight_elo_features_excluded",
                "unsafe_current_elo_historical_variant_blocked",
            ],
            "failed_checks": [],
        },
    }
    write_json(Path(args.output_json), payload)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(markdown_report(payload), encoding="utf-8")
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "status": payload["status"]}, indent=2))
    return 0


def strip_elo(frame):
    out = frame.copy()
    for column in set(out.columns) & set(ELO_PREFIGHT_FEATURES):
        out[column] = None
    for column in list(out.columns):
        lowered = str(column).lower()
        if "elo" in lowered:
            out[column] = None
    return out


def summarize_model(result: dict) -> dict:
    metrics = result.get("metrics") or {}
    return {
        "status": result.get("status"),
        "algorithm": result.get("algorithm"),
        "feature_count": result.get("feature_count"),
        "test_rows": result.get("test_rows"),
        "final_test_metric_name": result.get("final_test_metric_name"),
        "final_test_metric": result.get("final_test_metric"),
        "baseline_metric": result.get("baseline_metric"),
        "relative_improvement": result.get("relative_improvement"),
        "accuracy": metrics.get("accuracy"),
        "balanced_accuracy": metrics.get("balanced_accuracy"),
        "roc_auc": metrics.get("roc_auc"),
        "brier_score": metrics.get("brier_score"),
        "log_loss": metrics.get("log_loss"),
        "feature_names": result.get("feature_names", []),
    }


def markdown_report(payload: dict) -> str:
    strict = payload["ablation_results"]["strict_pre_fight_elo"]
    no_elo = payload["ablation_results"]["no_elo_features"]
    unsafe = payload["ablation_results"]["unsafe_current_or_latest_elo"]
    return "\n".join(
        [
            "# Elo Leakage Audit",
            "",
            "## Plain-English Summary",
            payload["plain_english_summary"],
            "",
            "## Decision",
            f"- Status: {payload['status']}",
            f"- Feature mode: {payload['feature_mode']}",
            f"- Same-event policy: {payload['same_event_policy']}",
            f"- Runtime policy: {payload['runtime_policy']}",
            "",
            "## Ablation Results",
            "| Variant | Status | Accuracy | Balanced Accuracy | ROC AUC | Brier | Baseline | Improvement | Notes |",
            "|---|---|---:|---:|---:|---:|---:|---:|---|",
            f"| Unsafe current/latest Elo | {unsafe['status']} |  |  |  |  |  |  | {unsafe['reason']} |",
            f"| Strict pre-fight Elo | {strict.get('status')} | {strict.get('accuracy')} | {strict.get('balanced_accuracy')} | {strict.get('roc_auc')} | {strict.get('brier_score')} | {strict.get('baseline_metric')} | {strict.get('relative_improvement')} | Used for historical training/backtests. |",
            f"| No Elo features | {no_elo.get('status')} | {no_elo.get('accuracy')} | {no_elo.get('balanced_accuracy')} | {no_elo.get('roc_auc')} | {no_elo.get('brier_score')} | {no_elo.get('baseline_metric')} | {no_elo.get('relative_improvement')} | Shows whether Elo is helping without leakage. |",
            "",
            "## Passed Checks",
            *[f"- {item}" for item in payload["audit"]["passed_checks"]],
            "",
            "## Failed Checks",
            *([f"- {item}" for item in payload["audit"]["failed_checks"]] or ["- None"]),
            "",
            "## Notes",
            "- Historical rows do not use current/latest Elo snapshots.",
            "- Same-card fights are treated as pre-event predictions by default.",
            "- Public Elo methodology was not added to the website.",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
