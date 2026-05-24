"""Centralized configuration — all paths via pathlib."""

import os
from pathlib import Path

# Package root (ufc_predictor/)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Data layout
DATA_DIR = Path(os.getenv("UFC_PREDICTOR_DATA_DIR", PACKAGE_ROOT / "data"))
DATA_RAW_DIR = DATA_DIR / "raw"
DATA_PROCESSED_DIR = DATA_DIR / "processed"
DATA_FEEDBACK_DIR = DATA_DIR / "feedback"

FIGHTERS_CSV = DATA_RAW_DIR / "fighters.csv"
FIGHTS_CSV = DATA_RAW_DIR / "fights.csv"
ELO_LEADERBOARD_CSV = DATA_PROCESSED_DIR / "current_fighters_elo.csv"
MODEL_METRICS_JSON = DATA_PROCESSED_DIR / "model_metrics.json"
MODEL_WEIGHTS_JSON = DATA_PROCESSED_DIR / "model_weights.json"
FIGHTERS_DB = DATA_PROCESSED_DIR / "fighters.db"
SCRAPE_CACHE_DIR = DATA_PROCESSED_DIR / "scrape_cache"

FEEDBACK_LOG_CSV = DATA_FEEDBACK_DIR / "feedback_log.csv"

# Production services
DATABASE_URL = os.getenv("DATABASE_URL", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")
FRONTEND_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS",
        "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

# Models
MODELS_DIR = PACKAGE_ROOT / "models"
LATEST_MODEL_PKL = MODELS_DIR / "latest_model.pkl"
SKLEARN_MODEL_DIR = MODELS_DIR / "sklearn"

# Config files
NOTE_TAGS_YAML = PACKAGE_ROOT / "config" / "note_tags.yaml"

# Logs
LOGS_DIR = PACKAGE_ROOT / "logs"
APP_LOG_FILE = LOGS_DIR / "app.log"

# Kaggle
KAGGLE_FIGHTS_DATASET = "trixster23/every-ufc-fight-ever"
KAGGLE_FIGHTS_FILENAME = "ufcfights10_26_24.csv"
KAGGLE_STATS_DATASET = "asaniczka/ufc-fighters-statistics"

# Data source priority for web fill-in
SOURCE_PRIORITY = ["ufcstats", "tapology", "sherdog", "wikipedia"]

# Elo
ELO_INITIAL = 1000
ELO_K_FACTOR = 40

# Retrain
RETRAIN_FEEDBACK_THRESHOLD = 10
RETRAIN_TEST_SIZE = 0.2
RETRAIN_RANDOM_STATE = 42

# Prediction
CLOSE_CALL_PROB_THRESHOLD = 0.08
CLOSE_CALL_ELO_THRESHOLD = 0.06
ENSEMBLE_WEIGHTS = {"sklearn": 0.55, "elo": 0.20, "llm": 0.25}
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Feature toggles
USE_SKLEARN_MODEL = True
USE_ELO_FALLBACK = True
USE_RANKINGS = True
USE_FEEDBACK_IN_TRAINING = True
EXPORT_ELO_ON_TRAIN = True
