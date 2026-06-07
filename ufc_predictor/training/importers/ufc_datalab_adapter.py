from __future__ import annotations

from pathlib import Path

from ufc_predictor.training.importers.github_adapter import adapt_github_dataset


def adapt(folder: str | Path, dry_run: bool = True):
    return adapt_github_dataset("ufc_datalab", folder, dry_run=dry_run)
