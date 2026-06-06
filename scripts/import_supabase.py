"""Import local UFC Predictor CSV data into Supabase Postgres.

Required environment variable:

    DATABASE_URL=postgresql://postgres:<password>@<host>:5432/postgres

Typical first run:

    python scripts/import_supabase.py --apply-schema

This script imports source data only. It does not upload SQLite caches or model
artifacts such as .pkl, model_weights.json, or model_metrics.json.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.models.elo.elo_engine import build_elo_fight_counts, compute_elo_ratings
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.weight_classes import detect_weight_class


FIGHTER_COLUMNS = [
    "name",
    "normalized_name",
    "nickname",
    "wins",
    "losses",
    "draws",
    "height_cm",
    "weight_in_kg",
    "reach_in_cm",
    "stance",
    "date_of_birth",
    "significant_strikes_landed_per_minute",
    "significant_striking_accuracy",
    "significant_strikes_absorbed_per_minute",
    "significant_strike_defence",
    "average_takedowns_landed_per_15_minutes",
    "takedown_accuracy",
    "takedown_defense",
    "average_submissions_attempted_per_15_minutes",
    "elo",
    "peak_elo",
    "elo_version",
    "elo_computed_at",
    "elo_fights_count",
    "elo_source",
    "weight_class",
    "updated_at",
]

FIGHT_COLUMNS = [
    "event",
    "fighter_1",
    "fighter_2",
    "result",
    "method",
    "round",
    "time",
    "source_hash",
    "created_at",
]

FEEDBACK_COLUMNS = [
    "prediction_id",
    "fighter_a",
    "fighter_b",
    "predicted_winner",
    "actual_winner",
    "confidence",
    "was_correct",
    "user_notes",
    "timestamp",
]


def connect():
    try:
        import psycopg
    except ImportError as exc:
        raise RuntimeError(
            "Install psycopg first: & $env:MMA_AI_PYTHON -m pip install -r requirements.txt"
        ) from exc

    db_url = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return psycopg.connect(db_url)


def apply_schema(conn) -> None:
    schema_path = ROOT / "supabase" / "schema.sql"
    with open(schema_path, encoding="utf-8") as f:
        conn.execute(f.read())
    conn.commit()


def import_all(apply_schema_first: bool = False) -> dict:
    with connect() as conn:
        if apply_schema_first:
            apply_schema(conn)

        fights = prepare_fights()
        fighters, elo_history = prepare_fighters_and_elo(fights)
        feedback = prepare_feedback()

        import_fighters(conn, fighters)
        import_fights(conn, fights)
        import_elo_history(conn, elo_history)
        import_feedback(conn, feedback)
        conn.commit()

    return {
        "fighters": len(fighters),
        "fights": len(fights),
        "fighter_elo_history": len(elo_history),
        "feedback": len(feedback),
    }


def prepare_fighters_and_elo(fights: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    fighters = pd.read_csv(settings.FIGHTERS_CSV)
    fighters["normalized_name"] = fighters["name"].map(normalize_name)

    _fights_elo, elo_ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
    fight_counts = build_elo_fight_counts(_fights_elo)
    fighters["elo"] = fighters["normalized_name"].map(elo_by_search).fillna(settings.ELO_INITIAL)
    fighters["peak_elo"] = fighters["name"].map(
        lambda name: peak_elo.get(name, elo_by_search.get(normalize_name(name), settings.ELO_INITIAL))
    )
    fighters["weight_class"] = fighters.apply(detect_weight_class, axis=1)
    fighters["elo_fights_count"] = fighters["normalized_name"].map(fight_counts).fillna(0).astype(int)
    fighters["elo_source"] = fighters["elo_fights_count"].map(lambda count: "computed" if int(count) > 0 else "baseline")
    fighters["elo_version"] = settings.ELO_ENGINE_VERSION
    computed_at = utc_now()
    fighters["elo_computed_at"] = fighters["elo_source"].map(lambda source: computed_at if source == "computed" else None)
    fighters["updated_at"] = computed_at

    for col in FIGHTER_COLUMNS:
        if col not in fighters.columns:
            fighters[col] = None

    elo_rows = []
    for fighter_name, elo in elo_ratings.items():
        elo_rows.append(
            {
                "fighter_name": fighter_name,
                "normalized_name": normalize_name(fighter_name),
                "elo": elo,
                "peak_elo": peak_elo.get(fighter_name, elo),
                "elo_version": settings.ELO_ENGINE_VERSION,
                "computed_at": computed_at,
            }
        )
    return fighters[FIGHTER_COLUMNS], pd.DataFrame(elo_rows)


def prepare_fights() -> pd.DataFrame:
    fights = pd.read_csv(settings.FIGHTS_CSV)
    dedupe_cols = [col for col in ["event", "fighter_1", "fighter_2", "result", "method", "round", "time"] if col in fights.columns]
    fights = fights.drop_duplicates(subset=dedupe_cols, keep="first") if dedupe_cols else fights.drop_duplicates()
    fights["source_hash"] = fights.apply(source_hash, axis=1)
    fights["created_at"] = utc_now()
    for col in FIGHT_COLUMNS:
        if col not in fights.columns:
            fights[col] = None
    return fights[FIGHT_COLUMNS]


def prepare_feedback() -> pd.DataFrame:
    if not settings.FEEDBACK_LOG_CSV.is_file():
        return pd.DataFrame(columns=FEEDBACK_COLUMNS)
    feedback = pd.read_csv(settings.FEEDBACK_LOG_CSV)
    for col in FEEDBACK_COLUMNS:
        if col not in feedback.columns:
            feedback[col] = None
    feedback["was_correct"] = feedback["was_correct"].map(parse_bool)
    return feedback[FEEDBACK_COLUMNS]


def import_fighters(conn, df: pd.DataFrame) -> None:
    columns = FIGHTER_COLUMNS
    update_cols = [col for col in columns if col != "normalized_name"]
    sql = f"""
        insert into fighters ({','.join(columns)})
        values ({','.join(['%s'] * len(columns))})
        on conflict (normalized_name) do update set
        {','.join([f"{col}=excluded.{col}" for col in update_cols])}
    """
    conn.cursor().executemany(sql, rows(df, columns))


def import_fights(conn, df: pd.DataFrame) -> None:
    columns = FIGHT_COLUMNS
    update_cols = [col for col in columns if col != "source_hash"]
    sql = f"""
        insert into fights ({','.join(columns)})
        values ({','.join(['%s'] * len(columns))})
        on conflict (source_hash) do update set
        {','.join([f"{col}=excluded.{col}" for col in update_cols])}
    """
    conn.cursor().executemany(sql, rows(df, columns))


def import_elo_history(conn, df: pd.DataFrame) -> None:
    if df.empty:
        return
    conn.execute("delete from fighter_elo_history where elo_version = %s", (settings.ELO_ENGINE_VERSION,))
    columns = ["fighter_name", "normalized_name", "elo", "peak_elo", "elo_version", "computed_at"]
    sql = f"insert into fighter_elo_history ({','.join(columns)}) values ({','.join(['%s'] * len(columns))})"
    conn.cursor().executemany(sql, rows(df, columns))


def import_feedback(conn, df: pd.DataFrame) -> None:
    if df.empty:
        return
    columns = FEEDBACK_COLUMNS
    sql = f"""
        insert into feedback ({','.join(columns)})
        values ({','.join(['%s'] * len(columns))})
    """
    conn.cursor().executemany(sql, rows(df, columns))


def rows(df: pd.DataFrame, columns: list[str]) -> list[tuple[Any, ...]]:
    return [tuple(clean_value(row[col]) for col in columns) for _, row in df.iterrows()]


def clean_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def source_hash(row: pd.Series) -> str:
    parts = [str(row.get(col, "") or "").strip().lower() for col in ["event", "fighter_1", "fighter_2", "result", "method", "round", "time"]]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def parse_bool(value):
    if pd.isna(value):
        return None
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-schema", action="store_true", help="Run supabase/schema.sql before import.")
    args = parser.parse_args()

    result = import_all(apply_schema_first=args.apply_schema)
    print("Supabase import complete:")
    for table, count in result.items():
        print(f"  {table}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
