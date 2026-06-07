from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.training.dataset_manifest import DATASET_MANIFEST


KAGGLE_DATASETS = {
    key: entry
    for key, entry in DATASET_MANIFEST.items()
    if entry.source_type == "kaggle"
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Download supported Kaggle UFC/MMA datasets into data/imports/kaggle.")
    parser.add_argument("--all", action="store_true", help="Download every configured Kaggle dataset.")
    parser.add_argument("--only", choices=sorted(KAGGLE_DATASETS), help="Download only one dataset key.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--output-root", default="data/imports/kaggle")
    args = parser.parse_args()

    if args.list:
        print(json.dumps({"datasets": [_dataset_plan(key, Path(args.output_root)) for key in sorted(KAGGLE_DATASETS)]}, indent=2))
        return 0
    if not args.all and not args.only:
        print(json.dumps({"error": "choose --all, --only KEY, or --list"}, indent=2))
        return 1

    keys = [args.only] if args.only else sorted(KAGGLE_DATASETS)
    plan = [_dataset_plan(key, Path(args.output_root)) for key in keys]
    if args.dry_run:
        print(json.dumps({"dry_run": True, "datasets": plan}, indent=2))
        return 0

    check = _run([sys.executable, "-m", "kaggle", "--version"])
    if check["returncode"] != 0:
        print(json.dumps({"error": "kaggle_cli_missing_or_not_authenticated", "install": f"{sys.executable} -m pip install kaggle", "auth_help": _auth_help()}, indent=2))
        return 2

    results = []
    for item in plan:
        target = Path(item["target_dir"])
        target.mkdir(parents=True, exist_ok=True)
        if args.skip_existing and any(target.iterdir()):
            results.append({**item, "status": "skipped_existing"})
            continue
        command = [
            sys.executable,
            "-m",
            "kaggle",
            "datasets",
            "download",
            "-d",
            item["slug"],
            "-p",
            str(target),
            "--unzip",
        ]
        if args.force:
            command.append("--force")
        result = _run(command)
        results.append(
            {
                **item,
                "status": "downloaded" if result["returncode"] == 0 else "failed",
                "returncode": result["returncode"],
                "stdout": _redact(result["stdout"]),
                "stderr": _redact(result["stderr"]),
                "auth_help": None if result["returncode"] == 0 else _auth_help(),
            }
        )
    print(json.dumps({"results": results}, indent=2))
    return 0 if all(item["status"] in {"downloaded", "skipped_existing"} for item in results) else 1


def _dataset_plan(key: str, output_root: Path) -> dict:
    entry = KAGGLE_DATASETS[key]
    target = output_root / Path(entry.local_path).name
    return {
        "key": key,
        "slug": entry.source_slug_or_repo,
        "target_dir": str(target),
        "intended_uses": entry.intended_uses,
    }


def _run(command: list[str]) -> dict:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _redact(text: str) -> str:
    return (text or "")[-1200:]


def _auth_help() -> list[str]:
    return [
        "Install/configure Kaggle CLI outside the repo.",
        "Keep kaggle.json under your user profile, not C:\\dev\\mma-ai.",
        "Never commit kaggle.json or any API key.",
    ]


if __name__ == "__main__":
    raise SystemExit(main())
