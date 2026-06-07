from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.training.leakage import scan_dataframe
from ufc_predictor.training.splits import chronological_split_df, event_grouped_split, random_stratified_split
from ufc_predictor.training.targets import build_bettor_targets


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit or train a leakage-aware winner model from Silver-style data.")
    parser.add_argument("--source", default="silver", choices=["silver", "csv"])
    parser.add_argument("--input", default="")
    parser.add_argument("--split", default="chronological", choices=["chronological", "event_grouped", "random_stratified"])
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else _default_silver_path()
    if not input_path or not input_path.is_file():
        print(json.dumps({"status": "blocked", "reason": "Silver CSV not found.", "expected_input": str(input_path or "")}, indent=2))
        return 2
    frame = pd.read_csv(input_path)
    targeted, target_report = build_bettor_targets(frame)
    valid = targeted[targeted["f1_wins"].notna()].copy()
    leakage = scan_dataframe(valid)
    train, test, split_report = _split(valid, args.split)
    payload = {
        "status": "audit_only" if args.dry_run else "blocked",
        "input": str(input_path),
        "source": args.source,
        "rows": int(len(frame)),
        "valid_winner_rows": int(len(valid)),
        "target_report": target_report.to_dict(),
        "split": split_report,
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "leakage_summary": leakage["summary"],
        "runtime_compatible": False,
        "decision": (
            "offline_benchmark_until_runtime_feature_builder_and_chronological_metrics_are implemented"
            if args.dry_run
            else "refusing_to_train_in_this_pass"
        ),
        "reason": "Mentor Silver features are valuable, but production winner training needs safe f1/f2 orientation, chronological validation, and runtime-compatible feature creation.",
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0 if args.dry_run else 2


def _default_silver_path() -> Path | None:
    candidates = [
        Path("data/imports/kaggle/jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset/UFC_full_data_silver.csv"),
        Path("ufc_predictor/data/imports/kaggle/jerzyszocik__ufc-fight-forecast-complete-gold-modeling-dataset/UFC_full_data_silver.csv"),
        Path("data/mentor_silver_run/UFC_full_data_silver.csv"),
    ]
    return next((path for path in candidates if path.is_file()), candidates[0])


def _split(df: pd.DataFrame, split_type: str):
    if split_type == "chronological":
        return chronological_split_df(df, date_col="event_date")
    if split_type == "event_grouped":
        return event_grouped_split(df, event_col="event_name", date_col="event_date")
    return random_stratified_split(df, target_col="f1_wins")


if __name__ == "__main__":
    raise SystemExit(main())
