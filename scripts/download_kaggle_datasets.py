from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.training.dataset_sources import CURATED_KAGGLE_DATASETS


DATASET_KEYS = {
    "fight_forecast_gold": "jerzyszocik/ufc-fight-forecast-complete-gold-modeling-dataset",
    "ufc_stats_complete": "leandroiber/ufc-stats-complete-dataset",
    "ufc_1994_2026": "jossilva3110/ufc-dataset-1994-2026",
    "mmastats": "leandroiber/mmastats",
    "fight_stats_2016_2024": "alexmagnus24/ufc-fight-statistics-july-2016-nov-2024",
    "betting_odds_daily": "jerzyszocik/ufc-betting-odds-daily-dataset",
    "betting_odds_2010_2020": "mdabbert/ufc-fights-2010-2020-with-betting-odds",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Download curated Kaggle UFC/MMA datasets into data/imports/kaggle.")
    parser.add_argument("--output-dir", default="data/imports/kaggle")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Pass --force to Kaggle and allow overwriting existing folders.")
    parser.add_argument("--only", choices=sorted(DATASET_KEYS), help="Download only one dataset key.")
    parser.add_argument("--method", choices=["auto", "cli", "kagglehub"], default="auto", help="Downloader backend. auto prefers Kaggle CLI and falls back to kagglehub.")
    args = parser.parse_args()

    datasets = [
        source
        for source in CURATED_KAGGLE_DATASETS
        if not args.only or source.slug == DATASET_KEYS[args.only]
    ]
    output_root = Path(args.output_dir)
    plan = [
        {
            "key": key_for_slug(source.slug),
            "slug": source.slug,
            "target_dir": str(output_root / folder_name(source.slug)),
            "best_use": source.best_use,
        }
        for source in datasets
    ]
    if args.dry_run:
        print(json.dumps({"datasets": plan}, indent=2))
        return 0

    method = args.method
    kaggle_check = run_command([sys.executable, "-m", "kaggle", "--version"], check=False)
    if method == "auto":
        method = "cli" if kaggle_check["returncode"] == 0 else "kagglehub"
    if method == "cli" and kaggle_check["returncode"] != 0:
        print(
            json.dumps(
                {
                    "error": "kaggle_cli_missing",
                    "install": f"{sys.executable} -m pip install kaggle",
                    "auth_help": kaggle_auth_help(),
                },
                indent=2,
            )
        )
        return 2
    kagglehub = None
    if method == "kagglehub":
        try:
            import kagglehub as kagglehub_module
        except ImportError as exc:
            print(json.dumps({"error": "kagglehub_missing", "install": f"{sys.executable} -m pip install kagglehub"}, indent=2))
            return 2
        kagglehub = kagglehub_module

    results = []
    output_root.mkdir(parents=True, exist_ok=True)
    for source in datasets:
        target_dir = output_root / folder_name(source.slug)
        target_dir.mkdir(parents=True, exist_ok=True)
        if any(target_dir.iterdir()) and not args.force:
            results.append(
                {
                    "slug": source.slug,
                    "target_dir": str(target_dir),
                    "status": "skipped_existing",
                    "message": "Folder already contains files. Use --force to refresh.",
                }
            )
            continue
        if method == "cli":
            command = [
                sys.executable,
                "-m",
                "kaggle",
                "datasets",
                "download",
                "-d",
                source.slug,
                "-p",
                str(target_dir),
                "--unzip",
            ]
            if args.force:
                command.append("--force")
            result = run_command(command, check=False)
            results.append(
                {
                    "slug": source.slug,
                    "method": "cli",
                    "target_dir": str(target_dir),
                    "status": "downloaded" if result["returncode"] == 0 else "failed",
                    "returncode": result["returncode"],
                    "stdout": redact(result["stdout"]),
                    "stderr": redact(result["stderr"]),
                    "auth_help": kaggle_auth_help() if result["returncode"] != 0 else None,
                }
            )
            continue
        try:
            cache_path = Path(kagglehub.dataset_download(source.slug))
            copied = copy_tree(cache_path, target_dir)
            results.append(
                {
                    "slug": source.slug,
                    "method": "kagglehub",
                    "target_dir": str(target_dir),
                    "cache_path": str(cache_path),
                    "copied_files": copied,
                    "status": "downloaded",
                }
            )
        except Exception as exc:  # noqa: BLE001 - report downloader/auth failures without secrets.
            results.append(
                {
                    "slug": source.slug,
                    "method": "kagglehub",
                    "target_dir": str(target_dir),
                    "status": "failed",
                    "error": redact(str(exc)),
                    "auth_help": kaggle_auth_help(),
                }
            )

    print(json.dumps({"results": results}, indent=2))
    return 0 if all(item["status"] in {"downloaded", "skipped_existing"} for item in results) else 1


def run_command(command: list[str], check: bool = False) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=check)
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def copy_tree(source: Path, target: Path) -> list[str]:
    copied = []
    for file_path in source.rglob("*"):
        if not file_path.is_file():
            continue
        destination = target / file_path.relative_to(source)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(file_path.read_bytes())
        copied.append(str(destination))
    return copied


def folder_name(slug: str) -> str:
    return slug.replace("/", "__")


def key_for_slug(slug: str) -> str:
    for key, known_slug in DATASET_KEYS.items():
        if slug == known_slug:
            return key
    return folder_name(slug)


def redact(text: str) -> str:
    # Kaggle should not print tokens, but keep output bounded and avoid echoing secrets by accident.
    if not text:
        return ""
    return text[-1200:]


def kaggle_auth_help() -> list[str]:
    return [
        "Go to Kaggle account settings.",
        "Create/download an API token.",
        "Store kaggle.json outside the repo, usually under your user .kaggle folder.",
        "Or run kaggle auth login if your Kaggle CLI supports it.",
        "Never commit kaggle.json or Kaggle credentials.",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
