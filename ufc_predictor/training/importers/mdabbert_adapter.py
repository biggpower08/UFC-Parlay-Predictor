from __future__ import annotations

from pathlib import Path

from ufc_predictor.training.importers.kaggle_adapter import adapt_kaggle_dataset


def adapt_ultimate(folder: str | Path, dry_run: bool = True):
    return adapt_kaggle_dataset("mdabbert_ultimate", folder, dry_run=dry_run)


def adapt_2010_2020_odds(folder: str | Path, dry_run: bool = True):
    return adapt_kaggle_dataset("mdabbert_2010_2020_odds", folder, dry_run=dry_run)
