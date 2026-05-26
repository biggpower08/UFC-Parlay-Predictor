"""Database sync helpers for scraped event, fight, and ranking data."""

from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import text

from ufc_predictor.db import repository
from ufc_predictor.db.schema import connect, get_engine, init_db, using_postgres
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger
from ufc_predictor.utils.weight_classes import detect_weight_class

logger = get_logger(__name__)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def upsert_events(events, dry_run: bool = False) -> int:
    init_db()
    rows = [
        {
            "name": event.name,
            "normalized_name": event.normalized_name,
            "event_date": event.event_date,
            "location": event.location,
            "source": event.source,
            "source_url": event.url,
            "source_hash": event.source_hash,
            "scraped_at": utc_now(),
            "updated_at": utc_now(),
        }
        for event in events
    ]
    if dry_run or not rows:
        return len(rows)
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    insert into events
                        (name, normalized_name, event_date, location, source, source_url, source_hash, scraped_at, updated_at)
                    values
                        (:name, :normalized_name, :event_date, :location, :source, :source_url, :source_hash, :scraped_at, :updated_at)
                    on conflict (normalized_name) do update set
                        event_date = excluded.event_date,
                        location = excluded.location,
                        source_url = excluded.source_url,
                        source_hash = excluded.source_hash,
                        scraped_at = excluded.scraped_at,
                        updated_at = excluded.updated_at
                    """
                ),
                rows,
            )
        return len(rows)
    with connect() as conn:
        conn.executemany(
            """
            insert or replace into events
                (name, normalized_name, event_date, location, source, source_url, source_hash, scraped_at, updated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["name"],
                    row["normalized_name"],
                    row["event_date"],
                    row["location"],
                    row["source"],
                    row["source_url"],
                    row["source_hash"],
                    row["scraped_at"],
                    row["updated_at"],
                )
                for row in rows
            ],
        )
        conn.commit()
    return len(rows)


def upsert_fights(fights, dry_run: bool = False) -> int:
    init_db()
    rows = [
        {
            "event": fight.event,
            "fighter_1": fight.fighter_1,
            "fighter_2": fight.fighter_2,
            "result": fight.result,
            "method": fight.method,
            "round": fight.round,
            "time": fight.time,
            "source_hash": fight.source_hash,
            "event_date": fight.event_date,
            "weight_class": fight.weight_class,
            "source": fight.source,
            "source_url": fight.source_url,
            "scraped_at": utc_now(),
        }
        for fight in fights
    ]
    if dry_run or not rows:
        return len(rows)
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    insert into fights
                        (event, fighter_1, fighter_2, result, method, round, time, source_hash,
                         event_date, weight_class, source, source_url, scraped_at)
                    values
                        (:event, :fighter_1, :fighter_2, :result, :method, :round, :time, :source_hash,
                         :event_date, :weight_class, :source, :source_url, :scraped_at)
                    on conflict (source_hash) do update set
                        result = excluded.result,
                        method = excluded.method,
                        round = excluded.round,
                        time = excluded.time,
                        event_date = excluded.event_date,
                        weight_class = excluded.weight_class,
                        source = excluded.source,
                        source_url = excluded.source_url,
                        scraped_at = excluded.scraped_at
                    """
                ),
                rows,
            )
        return len(rows)
    with connect() as conn:
        conn.executemany(
            """
            insert or ignore into fights
                (event, fighter_1, fighter_2, result, method, round, time, source_hash,
                 event_date, weight_class, source, source_url, scraped_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["event"],
                    row["fighter_1"],
                    row["fighter_2"],
                    row["result"],
                    row["method"],
                    row["round"],
                    row["time"],
                    row["source_hash"],
                    row["event_date"],
                    row["weight_class"],
                    row["source"],
                    row["source_url"],
                    row["scraped_at"],
                )
                for row in rows
            ],
        )
        conn.commit()
    return len(rows)


def upsert_fighters_from_fights(fights, dry_run: bool = False) -> int:
    names = []
    weight_by_name = {}
    for fight in fights:
        for name in (fight.fighter_1, fight.fighter_2):
            key = normalize_name(name)
            if not key:
                continue
            names.append(name)
            if fight.weight_class:
                weight_by_name.setdefault(key, fight.weight_class)
    unique = {normalize_name(name): name for name in names}
    if dry_run:
        return len(unique)

    df = repository.get_fighters_df()
    if "normalized_name" not in df.columns:
        name_col = "name" if "name" in df.columns else "Name"
        df["normalized_name"] = df[name_col].astype(str).map(normalize_name)
    existing = set(df["normalized_name"].dropna().astype(str))
    new_rows = []
    for key, name in unique.items():
        if key in existing:
            continue
        new_rows.append(
            {
                "name": name,
                "normalized_name": key,
                "_search_name": key,
                "weight_class": weight_by_name.get(key) or "Unknown",
                "elo": 1000,
                "peak_elo": 1000,
                "elo_fights_count": 0,
                "elo_source": "baseline",
            }
        )
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        repository.save_fighters_df(df, replace=True)
    return len(unique)


def replace_weight_class_history(rows: list[dict], dry_run: bool = False) -> int:
    init_db()
    if dry_run:
        return len(rows)
    generated_at = utc_now()
    for row in rows:
        row["generated_at"] = generated_at
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(text("delete from fighter_weight_class_history"))
            if rows:
                conn.execute(
                    text(
                        """
                        insert into fighter_weight_class_history
                            (fighter_name, normalized_name, weight_class, fights_count, first_seen, last_seen,
                             inferred_from_fights, confidence, generated_at)
                        values
                            (:fighter_name, :normalized_name, :weight_class, :fights_count, :first_seen, :last_seen,
                             :inferred_from_fights, :confidence, :generated_at)
                        """
                    ),
                    rows,
                )
        return len(rows)
    with connect() as conn:
        conn.execute("delete from fighter_weight_class_history")
        conn.executemany(
            """
            insert into fighter_weight_class_history
                (fighter_name, normalized_name, weight_class, fights_count, first_seen, last_seen,
                 inferred_from_fights, confidence, generated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["fighter_name"],
                    row["normalized_name"],
                    row["weight_class"],
                    row["fights_count"],
                    row["first_seen"],
                    row["last_seen"],
                    1 if row["inferred_from_fights"] else 0,
                    row["confidence"],
                    row["generated_at"],
                )
                for row in rows
            ],
        )
        conn.commit()
    return len(rows)


def record_sync_run(source: str, status: str, dry_run: bool, counts: dict, message: str = "") -> None:
    init_db()
    payload = {
        "source": source,
        "status": status,
        "started_at": utc_now(),
        "finished_at": utc_now(),
        "dry_run": dry_run,
        "events_seen": counts.get("events", 0),
        "fights_seen": counts.get("fights", 0),
        "fighters_seen": counts.get("fighters", 0),
        "message": message[:2000],
    }
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    insert into sync_runs
                        (source, status, started_at, finished_at, dry_run, events_seen, fights_seen, fighters_seen, message)
                    values
                        (:source, :status, :started_at, :finished_at, :dry_run, :events_seen, :fights_seen, :fighters_seen, :message)
                    """
                ),
                payload,
            )
        return
    with connect() as conn:
        conn.execute(
            """
            insert into sync_runs
                (source, status, started_at, finished_at, dry_run, events_seen, fights_seen, fighters_seen, message)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["source"],
                payload["status"],
                payload["started_at"],
                payload["finished_at"],
                1 if payload["dry_run"] else 0,
                payload["events_seen"],
                payload["fights_seen"],
                payload["fighters_seen"],
                payload["message"],
            ),
        )
        conn.commit()


def load_fights_table() -> pd.DataFrame:
    init_db()
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text("select * from fights")).mappings().all()
        return pd.DataFrame([dict(row) for row in rows])
    with connect() as conn:
        return pd.read_sql_query("select * from fights", conn)
