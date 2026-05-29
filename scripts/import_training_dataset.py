from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.importers import import_training_csvs


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize manually downloaded MMA CSV datasets for prop-model training.")
    parser.add_argument("--input-dir", default="data/imports", help="Folder containing downloaded CSV files.")
    parser.add_argument(
        "--output",
        default=str(settings.DATA_PROCESSED_DIR / "training_imports" / "normalized_fights.csv"),
        help="Normalized CSV output path.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Inspect and normalize without writing output.")
    args = parser.parse_args()

    _, report = import_training_csvs(args.input_dir, output=args.output, dry_run=args.dry_run)
    print(json.dumps(report.to_dict(), indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
