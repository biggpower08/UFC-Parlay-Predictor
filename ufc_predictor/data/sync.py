"""Database sync helpers for scraped event, fight, and ranking data."""

from __future__ import annotations

import socket
import uuid
import json
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone

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


def utc_now_dt() -> datetime:
    return datetime.now(timezone.utc)


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
        "inserted_count": counts.get("inserted", 0),
        "updated_count": counts.get("updated", 0),
        "skipped_count": counts.get("skipped", 0),
        "failed_count": counts.get("failed", 0),
        "message": message[:2000],
    }
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    insert into sync_runs
                        (source, status, started_at, finished_at, dry_run, events_seen, fights_seen, fighters_seen,
                         inserted_count, updated_count, skipped_count, failed_count, message)
                    values
                        (:source, :status, :started_at, :finished_at, :dry_run, :events_seen, :fights_seen, :fighters_seen,
                         :inserted_count, :updated_count, :skipped_count, :failed_count, :message)
                    """
                ),
                payload,
            )
        return
    with connect() as conn:
        conn.execute(
            """
            insert into sync_runs
                (source, status, started_at, finished_at, dry_run, events_seen, fights_seen, fighters_seen,
                 inserted_count, updated_count, skipped_count, failed_count, message)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                payload["inserted_count"],
                payload["updated_count"],
                payload["skipped_count"],
                payload["failed_count"],
                payload["message"],
            ),
        )
        conn.commit()


def update_source_health(
    source: str,
    base_url: str,
    status: str,
    error: str = "",
    challenged: bool = False,
    status_code: int | None = None,
    fetch_ms: float | None = None,
) -> None:
    init_db()
    now = utc_now()
    success = status == "healthy"
    payload = {
        "source": source,
        "base_url": base_url,
        "enabled": True,
        "last_success_at": now if success else None,
        "last_failed_at": None if success else now,
        "last_error": None if success else error[:2000],
        "challenge_detected": challenged,
        "last_status_code": status_code,
        "average_fetch_ms": fetch_ms,
        "updated_at": now,
    }
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    insert into scraper_sources
                        (source, base_url, enabled, last_success_at, last_failed_at, last_error,
                         challenge_detected, consecutive_failures, last_status_code, average_fetch_ms, updated_at)
                    values
                        (:source, :base_url, :enabled, :last_success_at, :last_failed_at, :last_error,
                         :challenge_detected, case when :last_failed_at is null then 0 else 1 end,
                         :last_status_code, :average_fetch_ms, :updated_at)
                    on conflict (source) do update set
                        base_url = excluded.base_url,
                        last_success_at = coalesce(excluded.last_success_at, scraper_sources.last_success_at),
                        last_failed_at = coalesce(excluded.last_failed_at, scraper_sources.last_failed_at),
                        last_error = excluded.last_error,
                        challenge_detected = excluded.challenge_detected,
                        consecutive_failures = case
                            when excluded.last_failed_at is null then 0
                            else scraper_sources.consecutive_failures + 1
                        end,
                        last_status_code = excluded.last_status_code,
                        average_fetch_ms = excluded.average_fetch_ms,
                        updated_at = excluded.updated_at
                    """
                ),
                payload,
            )
        return
    with connect() as conn:
        existing = conn.execute("select consecutive_failures from scraper_sources where source = ?", (source,)).fetchone()
        failures = 0 if success else ((existing["consecutive_failures"] if existing else 0) + 1)
        conn.execute(
            """
            insert or replace into scraper_sources
                (source, base_url, enabled, last_success_at, last_failed_at, last_error,
                 challenge_detected, consecutive_failures, last_status_code, average_fetch_ms, updated_at)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                base_url,
                1,
                payload["last_success_at"] if success else (None if not existing else conn.execute("select last_success_at from scraper_sources where source = ?", (source,)).fetchone()["last_success_at"]),
                payload["last_failed_at"],
                payload["last_error"],
                1 if challenged else 0,
                failures,
                status_code,
                fetch_ms,
                now,
            ),
        )
        conn.commit()


def get_sync_status(source: str = "ufcstats") -> dict:
    init_db()
    if using_postgres():
        with get_engine().begin() as conn:
            source_row = conn.execute(text("select * from scraper_sources where source = :source"), {"source": source}).mappings().fetchone()
            last_run = conn.execute(text("select * from sync_runs order by started_at desc limit 1")).mappings().fetchone()
            last_success = conn.execute(text("select * from sync_runs where status in ('success', 'succeeded') order by started_at desc limit 1")).mappings().fetchone()
            rankings = conn.execute(text("select max(generated_at) as generated_at from fighter_rankings")).mappings().fetchone()
            elo = conn.execute(text("select max(computed_at) as computed_at from fighter_elo_history")).mappings().fetchone()
            active_lock = conn.execute(text("select * from sync_locks where expires_at > now() order by started_at desc limit 1")).mappings().fetchone()
        return _status_payload(source_row, last_run, last_success, rankings, elo, active_lock)
    with connect() as conn:
        source_row = conn.execute("select * from scraper_sources where source = ?", (source,)).fetchone()
        last_run = conn.execute("select * from sync_runs order by started_at desc limit 1").fetchone()
        last_success = conn.execute("select * from sync_runs where status in ('success', 'succeeded') order by started_at desc limit 1").fetchone()
        rankings = conn.execute("select max(generated_at) as generated_at from fighter_rankings").fetchone()
        elo = conn.execute("select max(computed_at) as computed_at from fighter_elo_history").fetchone()
        active_lock = conn.execute("select * from sync_locks where expires_at > ? order by started_at desc limit 1", (utc_now(),)).fetchone()
    return _status_payload(source_row, last_run, last_success, rankings, elo, active_lock)


@contextmanager
def sync_lock(lock_name: str = "ufcstats_sync", ttl_minutes: int = 30, dry_run: bool = False):
    if dry_run:
        yield {"locked": False, "owner": "dry-run"}
        return
    owner = f"{socket.gethostname()}-{uuid.uuid4()}"
    if not acquire_sync_lock(lock_name, owner, ttl_minutes):
        raise RuntimeError(f"Sync lock is already held: {lock_name}")
    try:
        yield {"locked": True, "owner": owner}
    finally:
        release_sync_lock(lock_name, owner)


def acquire_sync_lock(lock_name: str, owner: str, ttl_minutes: int = 30) -> bool:
    init_db()
    now = utc_now_dt()
    expires = now + timedelta(minutes=ttl_minutes)
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(text("delete from sync_locks where expires_at < now()"))
            try:
                conn.execute(
                    text("insert into sync_locks (lock_name, owner, started_at, expires_at, metadata) values (:lock_name, :owner, :started_at, :expires_at, :metadata)"),
                    {"lock_name": lock_name, "owner": owner, "started_at": now, "expires_at": expires, "metadata": {"kind": "scheduled_sync"}},
                )
                return True
            except Exception:
                return False
    with connect() as conn:
        conn.execute("delete from sync_locks where expires_at < ?", (now.isoformat(),))
        try:
            conn.execute(
                "insert into sync_locks (lock_name, owner, started_at, expires_at, metadata) values (?, ?, ?, ?, ?)",
                (lock_name, owner, now.isoformat(), expires.isoformat(), json.dumps({"kind": "scheduled_sync"})),
            )
            conn.commit()
            return True
        except Exception:
            return False


def release_sync_lock(lock_name: str, owner: str) -> None:
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(text("delete from sync_locks where lock_name = :lock_name and owner = :owner"), {"lock_name": lock_name, "owner": owner})
        return
    with connect() as conn:
        conn.execute("delete from sync_locks where lock_name = ? and owner = ?", (lock_name, owner))
        conn.commit()


def load_fights_table() -> pd.DataFrame:
    init_db()
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text("select * from fights")).mappings().all()
        return pd.DataFrame([dict(row) for row in rows])
    with connect() as conn:
        return pd.read_sql_query("select * from fights", conn)


def _status_payload(source_row, last_run, last_success, rankings, elo, active_lock=None) -> dict:
    def as_dict(row):
        return dict(row) if row is not None else None

    source = as_dict(source_row)
    if source and source.get("challenge_detected"):
        source["status"] = "challenged"
    elif source and source.get("last_success_at"):
        source["status"] = "healthy"
    elif source and source.get("last_failed_at"):
        source["status"] = "unavailable"
    else:
        source = source or {"status": "unknown"}
    return {
        "source": source,
        "last_sync_run": as_dict(last_run),
        "last_successful_sync": as_dict(last_success),
        "last_rankings_generated_at": (dict(rankings).get("generated_at") if rankings else None),
        "last_elo_computed_at": (dict(elo).get("computed_at") if elo else None),
        "active_lock": as_dict(active_lock),
    }
