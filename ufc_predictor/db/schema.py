"""Database connection and schema helpers.

Local development uses SQLite. Production uses Supabase Postgres when
DATABASE_URL is provided.
"""

import sqlite3
from functools import lru_cache

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from ufc_predictor.config import settings


def using_postgres() -> bool:
    return bool(settings.DATABASE_URL)


def _database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    if using_postgres():
        return create_engine(_database_url(), pool_pre_ping=True)
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{settings.FIGHTERS_DB}", future=True)


def connect(db_path=None) -> sqlite3.Connection:
    if using_postgres():
        raise RuntimeError("Use get_engine() for DATABASE_URL/Postgres connections.")
    path = db_path or settings.FIGHTERS_DB
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def table_exists(table_name: str) -> bool:
    if using_postgres():
        return inspect(get_engine()).has_table(table_name)
    with connect() as conn:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,),
        ).fetchone()
    return row is not None


def init_db(db_path=None) -> None:
    """Create durable tables that sit beside the pandas-managed fighters table."""
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS fighters (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL UNIQUE,
                        nickname TEXT,
                        wins INTEGER,
                        losses INTEGER,
                        draws INTEGER,
                        height_cm DOUBLE PRECISION,
                        weight_in_kg DOUBLE PRECISION,
                        reach_in_cm DOUBLE PRECISION,
                        stance TEXT,
                        date_of_birth DATE,
                        significant_strikes_landed_per_minute DOUBLE PRECISION,
                        significant_striking_accuracy DOUBLE PRECISION,
                        significant_strikes_absorbed_per_minute DOUBLE PRECISION,
                        significant_strike_defence DOUBLE PRECISION,
                        average_takedowns_landed_per_15_minutes DOUBLE PRECISION,
                        takedown_accuracy DOUBLE PRECISION,
                        takedown_defense DOUBLE PRECISION,
                        average_submissions_attempted_per_15_minutes DOUBLE PRECISION,
                        elo DOUBLE PRECISION DEFAULT 1000,
                        peak_elo DOUBLE PRECISION DEFAULT 1000,
                        weight_class TEXT,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_name_trgm ON fighters USING gin (normalized_name gin_trgm_ops)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_nickname ON fighters (nickname)"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS scrape_cache (
                        normalized_name TEXT PRIMARY KEY,
                        source TEXT,
                        url TEXT,
                        raw_json JSONB NOT NULL,
                        confidence DOUBLE PRECISION DEFAULT 0.0,
                        fetched_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS predictions (
                        prediction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        fighter_a TEXT NOT NULL,
                        fighter_b TEXT NOT NULL,
                        winner TEXT,
                        confidence DOUBLE PRECISION,
                        model TEXT,
                        payload_json JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS fights (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        event TEXT,
                        fighter_1 TEXT,
                        fighter_2 TEXT,
                        result TEXT,
                        method TEXT,
                        round TEXT,
                        time TEXT,
                        source_hash TEXT UNIQUE,
                        created_at TIMESTAMPTZ DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS feedback (
                        prediction_id UUID,
                        fighter_a TEXT NOT NULL,
                        fighter_b TEXT NOT NULL,
                        predicted_winner TEXT NOT NULL,
                        actual_winner TEXT,
                        confidence DOUBLE PRECISION,
                        was_correct BOOLEAN NOT NULL,
                        user_notes TEXT,
                        timestamp TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS fighter_elo_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        fighter_name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL,
                        elo DOUBLE PRECISION NOT NULL,
                        peak_elo DOUBLE PRECISION NOT NULL,
                        computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_elo_history_normalized_name ON fighter_elo_history (normalized_name)"))
        return

    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scrape_cache (
                normalized_name TEXT PRIMARY KEY,
                source TEXT,
                url TEXT,
                raw_json TEXT NOT NULL,
                confidence REAL DEFAULT 0.0,
                fetched_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                prediction_id TEXT PRIMARY KEY,
                fighter_a TEXT NOT NULL,
                fighter_b TEXT NOT NULL,
                winner TEXT,
                confidence REAL,
                model TEXT,
                payload_json TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                fighter_1 TEXT,
                fighter_2 TEXT,
                result TEXT,
                method TEXT,
                round TEXT,
                time TEXT
            )
            """
        )
        conn.commit()
