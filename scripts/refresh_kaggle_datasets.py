from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Refresh configured Kaggle UFC/MMA datasets into local raw imports.")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--dataset-id")
    parser.add_argument("--only-odds", action="store_true")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--manifest", default="config/kaggle_datasets.yaml")
    parser.add_argument("--output-root", default="data/imports/kaggle")
    parser.add_argument("--write-summary", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    datasets = load_dataset_manifest(manifest_path)
    selected = select_datasets(datasets, all_datasets=args.all, dataset_id=args.dataset_id, only_odds=args.only_odds)
    if not selected:
        print(json.dumps({"error": "no_datasets_selected", "hint": "Use --all, --dataset-id ID, or --only-odds."}, indent=2))
        return 1

    output_root = Path(args.output_root)
    plan = [download_plan(item, output_root) for item in selected]
    if args.dry_run:
        print(json.dumps({"dry_run": True, "datasets": plan, "credentials_present": kaggle_credentials_present()}, indent=2))
        return 0

    if not kaggle_credentials_present():
        summary = {
            "generated_at": utc_now(),
            "status": "failed_missing_credentials",
            "error": "Kaggle credentials were not found.",
            "setup": kaggle_setup_help(),
            "results": [{**item, "status": "failed", "error": "missing_kaggle_credentials"} for item in plan],
        }
        write_download_manifest(output_root, summary)
        print(json.dumps(summary, indent=2))
        return 2

    results = []
    changed = False
    for item in selected:
        result = refresh_one_dataset(item, output_root, skip_existing=args.skip_existing, force=args.force, clean=args.clean)
        changed = changed or result.get("status") == "downloaded"
        results.append(result)
    summary = {
        "generated_at": utc_now(),
        "status": "ok" if all(result["status"] in {"downloaded", "skipped_existing"} for result in results) else "partial_failure",
        "changed": changed,
        "results": results,
    }
    write_download_manifest(output_root, summary)
    if args.write_summary:
        print(json.dumps(summary, indent=2))
    else:
        print(json.dumps({"status": summary["status"], "changed": changed, "manifest": str(output_root / "_download_manifest.json")}, indent=2))
    return 0 if summary["status"] == "ok" else 1


def load_dataset_manifest(path: Path) -> list[dict[str, Any]]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    datasets = data.get("datasets") if isinstance(data, dict) else None
    if not isinstance(datasets, list):
        raise ValueError(f"Dataset manifest must contain a datasets list: {path}")
    return [dict(item) for item in datasets]


def select_datasets(datasets: list[dict[str, Any]], all_datasets: bool, dataset_id: str | None, only_odds: bool) -> list[dict[str, Any]]:
    selected = []
    for item in datasets:
        if not item.get("enabled", False):
            continue
        if dataset_id and item.get("id") != dataset_id:
            continue
        if only_odds and not item.get("odds_source", False):
            continue
        if not all_datasets and not dataset_id and not only_odds:
            continue
        selected.append(item)
    return selected


def download_plan(item: dict[str, Any], output_root: Path) -> dict[str, Any]:
    return {
        "dataset_id": item["id"],
        "kaggle_ref": item["kaggle_ref"],
        "category": item.get("category"),
        "train_usage": item.get("train_usage"),
        "output_dir": str(output_root / item["id"]),
    }


def kaggle_credentials_present() -> bool:
    if os.environ.get("KAGGLE_USERNAME") and os.environ.get("KAGGLE_KEY"):
        return True
    candidates = [
        Path.home() / ".kaggle" / "kaggle.json",
        Path(os.environ.get("KAGGLE_CONFIG_DIR", "")) / "kaggle.json" if os.environ.get("KAGGLE_CONFIG_DIR") else None,
    ]
    return any(path and path.is_file() for path in candidates)


def kaggle_setup_help() -> list[str]:
    return [
        "Install or keep kagglehub in the project environment.",
        "Place kaggle.json in your user profile, usually C:\\Users\\<you>\\.kaggle\\kaggle.json.",
        "Do not put kaggle.json inside C:\\dev\\mma-ai and never commit it.",
        "Alternatively set KAGGLE_USERNAME and KAGGLE_KEY in your local environment.",
    ]


def refresh_one_dataset(item: dict[str, Any], output_root: Path, skip_existing: bool, force: bool, clean: bool) -> dict[str, Any]:
    dataset_id = item["id"]
    output_dir = output_root / dataset_id
    try:
        if skip_existing and output_dir.exists() and any(output_dir.rglob("*")) and not force:
            return {**download_plan(item, output_root), "status": "skipped_existing", "downloaded_files": file_manifest(output_dir)}
        if clean and output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        import kagglehub

        downloaded_path = Path(kagglehub.dataset_download(item["kaggle_ref"], force_download=force))
        copy_download(downloaded_path, output_dir)
        return {
            **download_plan(item, output_root),
            "status": "downloaded",
            "downloaded_at": utc_now(),
            "downloaded_files": file_manifest(output_dir),
        }
    except Exception as exc:  # pragma: no cover - exercised through failure-safe integration.
        return {**download_plan(item, output_root), "status": "failed", "error": scrub_error(str(exc))}


def copy_download(source: Path, output_dir: Path) -> None:
    if source.is_file():
        shutil.copy2(source, output_dir / source.name)
        return
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(source)
        target = output_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)


def file_manifest(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    files = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        files.append(
            {
                "path": str(path),
                "size_bytes": path.stat().st_size,
                "sha256": sha256(path),
            }
        )
    return files


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_download_manifest(output_root: Path, summary: dict[str, Any]) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "_download_manifest.json").write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")


def scrub_error(message: str) -> str:
    for key in ("KAGGLE_KEY", "KAGGLE_USERNAME"):
        value = os.environ.get(key)
        if value:
            message = message.replace(value, "[redacted]")
    return message[-1200:]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
