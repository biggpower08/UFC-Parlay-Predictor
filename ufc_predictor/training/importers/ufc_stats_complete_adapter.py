from __future__ import annotations

from pathlib import Path

from ufc_predictor.training.importers.kaggle_adapter import adapt_kaggle_dataset


def adapt(folder: str | Path, dry_run: bool = True):
    return adapt_kaggle_dataset("ufc_stats_complete", folder, dry_run=dry_run)
