"""GitHub/manual local dataset adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ufc_predictor.training.importers.kaggle_adapter import normalize_common_columns


def inventory_github_folder(folder: str | Path) -> dict[str, Any]:
    root = Path(folder)
    interesting = []
    if root.exists():
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix.lower() in {".csv", ".json", ".jsonl"}:
                interesting.append(str(path))
    return {"folder": str(root), "files": interesting, "available": bool(interesting)}


def adapt_github_dataset(dataset_key: str, folder: str | Path, dry_run: bool = True) -> tuple[pd.DataFrame, dict[str, Any]]:
    root = Path(folder)
    frames = []
    warnings = []
    for path in sorted(root.rglob("*.csv")) if root.exists() else []:
        lowered = str(path).lower()
        if not any(part in lowered for part in ["data", "stats", "scorecard", "merged", "processed", "clean"]):
            continue
        try:
            raw = pd.read_csv(path, nrows=None if not dry_run else 5000, low_memory=False)
        except Exception as exc:  # noqa: BLE001
            warnings.append(f"{path}: {exc}")
            continue
        raw["source_file"] = str(path)
        raw["source_dataset"] = dataset_key
        frames.append(normalize_common_columns(raw, dataset_key))
    frame = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
    return frame, {"dataset_key": dataset_key, "adapter": "github_local", "inventory": inventory_github_folder(root), "warnings": warnings}
