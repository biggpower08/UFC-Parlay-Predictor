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
                        elo_version TEXT DEFAULT 'v1',
                        elo_computed_at TIMESTAMPTZ,
                        elo_fights_count INTEGER DEFAULT 0,
                        elo_source TEXT DEFAULT 'baseline',
                        weight_class TEXT,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_name_trgm ON fighters USING gin (normalized_name gin_trgm_ops)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_nickname ON fighters (nickname)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_normalized_name ON fighters (normalized_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_name_lower ON fighters (lower(name))"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_nickname_lower ON fighters (lower(nickname))"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_nickname_trgm ON fighters USING gin (nickname gin_trgm_ops)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_weight_class ON fighters (weight_class)"))
            conn.execute(text("ALTER TABLE fighters ADD COLUMN IF NOT EXISTS elo_version TEXT DEFAULT 'v1'"))
            conn.execute(text("ALTER TABLE fighters ADD COLUMN IF NOT EXISTS elo_computed_at TIMESTAMPTZ"))
            conn.execute(text("ALTER TABLE fighters ADD COLUMN IF NOT EXISTS elo_fights_count INTEGER DEFAULT 0"))
            conn.execute(text("ALTER TABLE fighters ADD COLUMN IF NOT EXISTS elo_source TEXT DEFAULT 'baseline'"))
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
                        event_date DATE,
                        weight_class TEXT,
                        source TEXT DEFAULT 'local_csv',
                        source_url TEXT,
                        scraped_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("ALTER TABLE fights ADD COLUMN IF NOT EXISTS event_date DATE"))
            conn.execute(text("ALTER TABLE fights ADD COLUMN IF NOT EXISTS weight_class TEXT"))
            conn.execute(text("ALTER TABLE fights ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'local_csv'"))
            conn.execute(text("ALTER TABLE fights ADD COLUMN IF NOT EXISTS source_url TEXT"))
            conn.execute(text("ALTER TABLE fights ADD COLUMN IF NOT EXISTS scraped_at TIMESTAMPTZ"))
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
                        elo_version TEXT NOT NULL DEFAULT 'v1',
                        computed_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_elo_history_normalized_name ON fighter_elo_history (normalized_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_elo_history_name_computed_at ON fighter_elo_history (normalized_name, computed_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_elo_history_fighter_name ON fighter_elo_history (fighter_name)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_elo_source ON fighters (elo_source)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fights_fighter_1_event ON fights (fighter_1, event)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fights_fighter_2_event ON fights (fighter_2, event)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fights_event_created_at ON fights (event, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fights_created_at ON fights (created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fights_weight_class ON fights (weight_class)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_predictions_fighter_a_created_at ON predictions (fighter_a, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_predictions_fighter_b_created_at ON predictions (fighter_b, created_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_predictions_created_at ON predictions (created_at)"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL UNIQUE,
                        event_date DATE,
                        location TEXT,
                        source TEXT NOT NULL DEFAULT 'ufcstats',
                        source_url TEXT,
                        source_hash TEXT UNIQUE,
                        scraped_at TIMESTAMPTZ,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_events_event_date ON events (event_date)"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS fighter_rankings (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        fighter_name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL,
                        ranking_type TEXT NOT NULL,
                        weight_class TEXT,
                        rank INTEGER NOT NULL,
                        elo DOUBLE PRECISION NOT NULL,
                        peak_elo DOUBLE PRECISION,
                        fights_count INTEGER DEFAULT 0,
                        wins INTEGER DEFAULT 0,
                        losses INTEGER DEFAULT 0,
                        generated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        source TEXT NOT NULL DEFAULT 'elo_v1'
                    )
                    """
                )
            )
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rankings_type_rank ON fighter_rankings (ranking_type, rank)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_rankings_weight_class ON fighter_rankings (weight_class)"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS fighter_weight_class_history (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        fighter_name TEXT NOT NULL,
                        normalized_name TEXT NOT NULL,
                        weight_class TEXT NOT NULL,
                        fights_count INTEGER DEFAULT 0,
                        first_seen DATE,
                        last_seen DATE,
                        inferred_from_fights BOOLEAN NOT NULL DEFAULT true,
                        confidence DOUBLE PRECISION DEFAULT 0,
                        generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS sync_runs (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        source TEXT NOT NULL,
                        status TEXT NOT NULL,
                        started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        finished_at TIMESTAMPTZ,
                        dry_run BOOLEAN NOT NULL DEFAULT false,
                        events_seen INTEGER DEFAULT 0,
                        fights_seen INTEGER DEFAULT 0,
                        fighters_seen INTEGER DEFAULT 0,
                        message TEXT
                    )
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS scraper_sources (
                        source TEXT PRIMARY KEY,
                        base_url TEXT NOT NULL,
                        enabled BOOLEAN NOT NULL DEFAULT true,
                        last_success_at TIMESTAMPTZ,
                        last_failed_at TIMESTAMPTZ,
                        last_error TEXT,
                        challenge_detected BOOLEAN NOT NULL DEFAULT false,
                        consecutive_failures INTEGER NOT NULL DEFAULT 0,
                        last_status_code INTEGER,
                        average_fetch_ms DOUBLE PRECISION,
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
            conn.execute(text("ALTER TABLE scraper_sources ADD COLUMN IF NOT EXISTS last_failed_at TIMESTAMPTZ"))
            conn.execute(text("ALTER TABLE scraper_sources ADD COLUMN IF NOT EXISTS challenge_detected BOOLEAN NOT NULL DEFAULT false"))
            conn.execute(text("ALTER TABLE scraper_sources ADD COLUMN IF NOT EXISTS consecutive_failures INTEGER NOT NULL DEFAULT 0"))
            conn.execute(text("ALTER TABLE scraper_sources ADD COLUMN IF NOT EXISTS last_status_code INTEGER"))
            conn.execute(text("ALTER TABLE scraper_sources ADD COLUMN IF NOT EXISTS average_fetch_ms DOUBLE PRECISION"))
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS sync_locks (
                        lock_name TEXT PRIMARY KEY,
                        owner TEXT NOT NULL,
                        started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                        expires_at TIMESTAMPTZ NOT NULL
                    )
                    """
                )
            )
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
                time TEXT,
                source_hash TEXT UNIQUE,
                event_date TEXT,
                weight_class TEXT,
                source TEXT DEFAULT 'local_csv',
                source_url TEXT,
                scraped_at TEXT
            )
            """
        )
        for stmt in (
            "ALTER TABLE fights ADD COLUMN source_hash TEXT",
            "ALTER TABLE fights ADD COLUMN event_date TEXT",
            "ALTER TABLE fights ADD COLUMN weight_class TEXT",
            "ALTER TABLE fights ADD COLUMN source TEXT DEFAULT 'local_csv'",
            "ALTER TABLE fights ADD COLUMN source_url TEXT",
            "ALTER TABLE fights ADD COLUMN scraped_at TEXT",
        ):
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fighter_elo_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                elo REAL NOT NULL,
                peak_elo REAL NOT NULL,
                elo_version TEXT NOT NULL DEFAULT 'v1',
                computed_at TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_elo_history_normalized_name ON fighter_elo_history (normalized_name)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_elo_history_name_computed_at ON fighter_elo_history (normalized_name, computed_at)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                normalized_name TEXT NOT NULL UNIQUE,
                event_date TEXT,
                location TEXT,
                source TEXT NOT NULL DEFAULT 'ufcstats',
                source_url TEXT,
                source_hash TEXT UNIQUE,
                scraped_at TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_events_event_date ON events (event_date)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fighter_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                ranking_type TEXT NOT NULL,
                weight_class TEXT,
                rank INTEGER NOT NULL,
                elo REAL NOT NULL,
                peak_elo REAL,
                fights_count INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                generated_at TEXT,
                source TEXT NOT NULL DEFAULT 'elo_v1'
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_rankings_type_rank ON fighter_rankings (ranking_type, rank)")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fighter_weight_class_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fighter_name TEXT NOT NULL,
                normalized_name TEXT NOT NULL,
                weight_class TEXT NOT NULL,
                fights_count INTEGER DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT,
                inferred_from_fights INTEGER NOT NULL DEFAULT 1,
                confidence REAL DEFAULT 0,
                generated_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT,
                dry_run INTEGER NOT NULL DEFAULT 0,
                events_seen INTEGER DEFAULT 0,
                fights_seen INTEGER DEFAULT 0,
                fighters_seen INTEGER DEFAULT 0,
                message TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scraper_sources (
                source TEXT PRIMARY KEY,
                base_url TEXT NOT NULL,
                enabled INTEGER NOT NULL DEFAULT 1,
                last_success_at TEXT,
                last_failed_at TEXT,
                last_error TEXT,
                challenge_detected INTEGER NOT NULL DEFAULT 0,
                consecutive_failures INTEGER NOT NULL DEFAULT 0,
                last_status_code INTEGER,
                average_fetch_ms REAL,
                updated_at TEXT
            )
            """
        )
        for stmt in (
            "ALTER TABLE scraper_sources ADD COLUMN last_failed_at TEXT",
            "ALTER TABLE scraper_sources ADD COLUMN challenge_detected INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE scraper_sources ADD COLUMN consecutive_failures INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE scraper_sources ADD COLUMN last_status_code INTEGER",
            "ALTER TABLE scraper_sources ADD COLUMN average_fetch_ms REAL",
        ):
            try:
                conn.execute(stmt)
            except sqlite3.OperationalError:
                pass
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sync_locks (
                lock_name TEXT PRIMARY KEY,
                owner TEXT NOT NULL,
                started_at TEXT NOT NULL,
                expires_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
