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
    parser.add_argument("--input-dir", default="", help="Folder containing downloaded CSV files. Defaults to data/imports, then ufc_predictor/data/imports.")
    parser.add_argument(
        "--output",
        default=str(settings.DATA_PROCESSED_DIR / "training_imports" / "normalized_fights.csv"),
        help="Normalized CSV output path.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Inspect and normalize without writing output.")
    args = parser.parse_args()

    input_dirs = [Path(args.input_dir)] if args.input_dir else [Path("data/imports"), settings.DATA_DIR / "imports"]
    reports = []
    wrote_rows = False
    for input_dir in input_dirs:
        output = args.output
        if len(input_dirs) > 1 and input_dir != input_dirs[0]:
            output_path = Path(args.output)
            output = str(output_path.with_name(f"{output_path.stem}_{input_dir.name}{output_path.suffix}"))
        normalized, report = import_training_csvs(input_dir, output=output, dry_run=args.dry_run)
        reports.append(report.to_dict())
        wrote_rows = wrote_rows or not normalized.empty
        if normalized.empty and not args.input_dir:
            continue
        if args.input_dir:
            break

    payload = {
        "reports": reports,
        "combined_rows_normalized": sum(report.get("rows_normalized", 0) for report in reports),
        "wrote_normalized_data": bool(wrote_rows and not args.dry_run),
    }
    print(json.dumps(payload, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
