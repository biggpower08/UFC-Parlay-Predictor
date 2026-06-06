from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.training.dataset_sources import CURATED_KAGGLE_DATASETS, curated_training_sources


def main() -> int:
    parser = argparse.ArgumentParser(description="Download curated Kaggle UFC/MMA datasets into local import storage.")
    parser.add_argument("--output-dir", default="data/imports", help="Local folder for downloaded CSV files. Do not commit this folder.")
    parser.add_argument("--dry-run", action="store_true", help="Print the dataset catalog without downloading.")
    parser.add_argument("--copy", action="store_true", help="Copy downloaded files into --output-dir. Otherwise report Kaggle cache paths.")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    payload = {"sources": curated_training_sources(), "downloads": []}
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        return 0

    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError("Install kagglehub first: & $env:MMA_AI_PYTHON -m pip install kagglehub") from exc

    if args.copy:
        output_dir.mkdir(parents=True, exist_ok=True)

    for source in CURATED_KAGGLE_DATASETS:
        download_path = Path(kagglehub.dataset_download(source.slug))
        copied_files = []
        if args.copy:
            destination = output_dir / source.slug.replace("/", "__")
            destination.mkdir(parents=True, exist_ok=True)
            for file_path in download_path.rglob("*"):
                if file_path.is_file():
                    target = destination / file_path.relative_to(download_path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, target)
                    copied_files.append(str(target))
        payload["downloads"].append(
            {
                "slug": source.slug,
                "cache_path": str(download_path),
                "copied_files": copied_files,
            }
        )

    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
