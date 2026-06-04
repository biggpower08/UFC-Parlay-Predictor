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
PROP_MODELS_DIR = MODELS_DIR / "props" / "artifacts"
PROP_MODEL_METRICS_JSON = DATA_PROCESSED_DIR / "prop_model_metrics.json"

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
ELO_ENGINE_VERSION = "v1"

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
USE_LLM_ANALYST = os.getenv("USE_LLM_ANALYST", "false").lower() in {"1", "true", "yes", "on"}
ENABLE_AI_SUMMARY = os.getenv("ENABLE_AI_SUMMARY", "false").lower() in {"1", "true", "yes", "on"}
AI_SUMMARY_PROVIDER = os.getenv("AI_SUMMARY_PROVIDER", "none")
AI_SUMMARY_MODEL = os.getenv("AI_SUMMARY_MODEL", "")
AI_SUMMARY_TIMEOUT_SECONDS = float(os.getenv("AI_SUMMARY_TIMEOUT_SECONDS", "10"))

# Odds / betting-read infrastructure. Disabled by default; no API key is required
# for public predictions or normal app startup.
ENABLE_ODDS = os.getenv("ENABLE_ODDS", "false").lower() in {"1", "true", "yes", "on"}
ODDS_PROVIDER = os.getenv("ODDS_PROVIDER", "none")
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "")
ODDS_CACHE_TTL_SECONDS = int(os.getenv("ODDS_CACHE_TTL_SECONDS", "300"))

# Prediction-credit/paywall scaffolding. Disabled by default so current public
# prediction behavior is unchanged until payments/auth are intentionally added.
ENABLE_CREDIT_GATE = os.getenv("ENABLE_CREDIT_GATE", "false").lower() in {"1", "true", "yes", "on"}
FREE_PREDICTION_LIMIT = int(os.getenv("FREE_PREDICTION_LIMIT", "3"))
CREDIT_PACK_OPTIONS = [
    int(option.strip())
    for option in os.getenv("CREDIT_PACK_OPTIONS", "5,10,15,20").split(",")
    if option.strip().isdigit()
]

# Future Stripe placeholders only; real checkout/webhooks are not active yet.
ENABLE_STRIPE = os.getenv("ENABLE_STRIPE", "false").lower() in {"1", "true", "yes", "on"}
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")
STRIPE_PRICE_PACK_5 = os.getenv("STRIPE_PRICE_PACK_5", "")
STRIPE_PRICE_PACK_10 = os.getenv("STRIPE_PRICE_PACK_10", "")
STRIPE_PRICE_PACK_15 = os.getenv("STRIPE_PRICE_PACK_15", "")
STRIPE_PRICE_PACK_20 = os.getenv("STRIPE_PRICE_PACK_20", "")

# Scraper / sync
ENABLE_LIVE_SYNC = os.getenv("ENABLE_LIVE_SYNC", "false").lower() in {"1", "true", "yes", "on"}
SYNC_SECRET = os.getenv("SYNC_SECRET", "")
SCRAPER_FETCHER = os.getenv("SCRAPER_FETCHER", "requests")
SCRAPER_RATE_LIMIT_SECONDS = float(os.getenv("SCRAPER_RATE_LIMIT_SECONDS", "0.75"))
SCRAPER_CACHE_DIR = Path(os.getenv("SCRAPER_CACHE_DIR", SCRAPE_CACHE_DIR / "http"))
SCRAPER_USER_AGENT = os.getenv(
    "SCRAPER_USER_AGENT",
    "UFC-Predictor/2.0 (+https://github.com/biggpower08/UFC-Parlay-Predictor)",
)
SCRAPER_MAX_RESPONSE_BYTES = int(os.getenv("SCRAPER_MAX_RESPONSE_BYTES", "3000000"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

# Feature toggles
USE_SKLEARN_MODEL = True
USE_ELO_FALLBACK = True
USE_RANKINGS = True
USE_FEEDBACK_IN_TRAINING = True
EXPORT_ELO_ON_TRAIN = True
