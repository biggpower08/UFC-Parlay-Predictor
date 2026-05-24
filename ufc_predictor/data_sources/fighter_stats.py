"""Per-fighter career stats (Kaggle asaniczka dataset)."""

import os

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import find_name_column
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def load_ufc_fighters() -> pd.DataFrame:
    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError(
            "kagglehub is required to refresh fighter stats. Install requirements or use the cached CSV."
        ) from exc

    path = kagglehub.dataset_download(settings.KAGGLE_STATS_DATASET)
    csv_file = [f for f in os.listdir(path) if f.endswith(".csv")][0]
    return pd.read_csv(os.path.join(path, csv_file))


def load_fighters_cached() -> pd.DataFrame:
    path = settings.FIGHTERS_CSV
    if path.is_file():
        return pd.read_csv(path)
    df = load_ufc_fighters()
    settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Cached fighters to %s", path)
    return df
