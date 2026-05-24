"""UFC fight history loader (Kaggle every-ufc-fight-ever)."""

import os

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def load_fights(force_refresh: bool = False) -> pd.DataFrame:
    path = settings.FIGHTS_CSV
    if path.is_file() and not force_refresh:
        logger.info("Loading fights from %s", path)
        return pd.read_csv(path)

    try:
        import kagglehub
    except ImportError as exc:
        raise RuntimeError(
            "kagglehub is required to refresh fights. Install requirements or use the cached CSV."
        ) from exc

    logger.info("Downloading fight history from Kaggle...")
    kaggle_path = kagglehub.dataset_download(settings.KAGGLE_FIGHTS_DATASET)
    csv_path = os.path.join(kaggle_path, settings.KAGGLE_FIGHTS_FILENAME)
    if not os.path.isfile(csv_path):
        candidates = [f for f in os.listdir(kaggle_path) if f.endswith(".csv")]
        if not candidates:
            raise FileNotFoundError(f"No CSV in {kaggle_path}")
        csv_path = os.path.join(kaggle_path, candidates[0])

    df = pd.read_csv(csv_path, index_col=0).reset_index()
    settings.DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    logger.info("Cached %s fights to %s", len(df), path)
    return df
