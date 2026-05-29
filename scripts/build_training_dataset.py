from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv


def main() -> int:
    parser = argparse.ArgumentParser(description="Build or audit leakage-aware training rows.")
    parser.add_argument("--dry-run", action="store_true", help="Print audit only and do not write a dataset.")
    parser.add_argument("--output", default="", help="Optional CSV output path. Not used with --dry-run.")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--min-date", default="")
    parser.add_argument("--max-date", default="")
    parser.add_argument("--source", default="csv", choices=["csv", "imported_csv", "ufcstats_cache", "manual_html"])
    parser.add_argument("--input", default=str(settings.FIGHTS_CSV), help="Input fights CSV path.")
    parser.add_argument("--missingness-report", action="store_true")
    args = parser.parse_args()

    default_import = settings.DATA_PROCESSED_DIR / "training_imports" / "normalized_fights.csv"
    input_path = args.input
    if args.source == "imported_csv" and args.input == str(settings.FIGHTS_CSV) and default_import.is_file():
        input_path = str(default_import)
    fights = load_fights_csv(input_path)
    if args.min_date and "event_date" in fights.columns:
        fights = fights[fights["event_date"] >= args.min_date]
    if args.max_date and "event_date" in fights.columns:
        fights = fights[fights["event_date"] <= args.max_date]
    if args.limit:
        fights = fights.head(args.limit)

    dataset, audit = build_training_rows(fights, source=args.source)
    payload = audit.to_dict()
    if not args.missingness_report:
        payload.pop("missingness_report", None)
    print(json.dumps(payload, indent=2, default=str))

    if args.dry_run:
        return 0
    if not audit.training_data_ready:
        print("Refusing to write training dataset because audit did not pass readiness checks.")
        return 2
    if not args.output:
        print("--output is required when not using --dry-run.")
        return 1
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(output, index=False)
    print(f"Wrote training dataset: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
