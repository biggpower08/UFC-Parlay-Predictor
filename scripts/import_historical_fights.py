"""Import local historical fight rows into the production fights table.

This is the safe path to seed Supabase when live UFCStats scraping is blocked.
It only imports source fight/event rows and minimal missing fighter names; Elo and
rankings are generated afterward by the existing update scripts.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
from sqlalchemy import bindparam, create_engine, text
from sqlalchemy.engine import Engine

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.db.schema import init_db
from ufc_predictor.utils.helpers import normalize_name


COLUMN_CANDIDATES = {
    "event": ["event", "event_name", "card"],
    "event_date": ["event_date", "date"],
    "fighter_1": ["fighter_1", "red_fighter", "winner", "fighter_a"],
    "fighter_2": ["fighter_2", "blue_fighter", "loser", "fighter_b"],
    "result": ["result", "outcome"],
    "method": ["method", "finish_method"],
    "round": ["round", "end_round"],
    "time": ["time", "end_time"],
    "weight_class": ["weight_class", "weight", "division"],
    "source_url": ["source_url", "url", "fight_url"],
}


@dataclass
class ImportSummary:
    source_file: str
    source_rows: int
    prepared_rows: int
    duplicate_source_rows: int
    invalid_rows: int
    events_seen: int
    fighters_seen: int
    fights_before: int | None
    fights_after: int | None
    expected_inserts: int
    expected_existing: int
    dry_run: bool


def main() -> int:
    parser = argparse.ArgumentParser(description="Import historical fight CSV rows into Supabase/Postgres.")
    parser.add_argument("--source-file", default=str(settings.FIGHTS_CSV))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--force", action="store_true", help="Update existing fight rows when source_hash already exists.")
    parser.add_argument("--database-url", default=None, help="Optional override; DATABASE_URL is used by default.")
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url
        settings.DATABASE_URL = args.database_url

    try:
        engine = None if args.dry_run and not _database_url() else _engine()
        summary = import_historical_fights(
            Path(args.source_file),
            dry_run=args.dry_run,
            limit=args.limit,
            force=args.force,
            engine=engine,
        )
    except Exception as exc:
        print(f"Historical fight import failed: {exc}")
        return 1

    print_summary(summary)
    return 0


def import_historical_fights(
    source_file: Path,
    dry_run: bool = False,
    limit: int | None = None,
    force: bool = False,
    engine: Engine | None = None,
) -> ImportSummary:
    fights, stats = prepare_fight_rows(source_file, limit=limit)
    events = build_event_rows(fights)
    fighters = build_fighter_rows(fights)

    fights_before = None
    fights_after = None
    expected_existing = 0

    if engine is not None:
        init_db()
        with engine.begin() as conn:
            fights_before = scalar_count(conn, "fights")
            existing_hashes = fetch_existing_hashes(conn, [row["source_hash"] for row in fights])
            expected_existing = len(existing_hashes)
            if not dry_run:
                upsert_events(conn, events)
                upsert_minimal_fighters(conn, fighters)
                upsert_fights(conn, fights, force=force)
                fights_after = scalar_count(conn, "fights")

    return ImportSummary(
        source_file=str(source_file),
        source_rows=stats["source_rows"],
        prepared_rows=len(fights),
        duplicate_source_rows=stats["duplicate_source_rows"],
        invalid_rows=stats["invalid_rows"],
        events_seen=len(events),
        fighters_seen=len(fighters),
        fights_before=fights_before,
        fights_after=fights_after,
        expected_inserts=max(0, len(fights) - expected_existing),
        expected_existing=expected_existing,
        dry_run=dry_run,
    )


def prepare_fight_rows(source_file: Path, limit: int | None = None) -> tuple[list[dict], dict]:
    if not source_file.is_file():
        raise FileNotFoundError(f"Source file not found: {source_file}")

    df = pd.read_csv(source_file)
    if limit:
        df = df.head(limit)
    source_rows = len(df)
    mapping = detect_columns(df.columns)
    required = ["event", "fighter_1", "fighter_2"]
    missing = [name for name in required if name not in mapping]
    if missing:
        raise ValueError(f"Source file is missing required columns: {', '.join(missing)}")

    rows: list[dict] = []
    invalid_rows = 0
    seen_hashes: set[str] = set()
    duplicate_rows = 0
    now = utc_now()

    for _, row in df.iterrows():
        event = clean(row.get(mapping["event"]))
        fighter_1 = clean(row.get(mapping["fighter_1"]))
        fighter_2 = clean(row.get(mapping["fighter_2"]))
        if not event or not fighter_1 or not fighter_2:
            invalid_rows += 1
            continue

        prepared = {
            "event": event,
            "fighter_1": fighter_1,
            "fighter_2": fighter_2,
            "result": normalize_result(clean(row.get(mapping.get("result"))) or "unknown"),
            "method": clean(row.get(mapping.get("method"))),
            "round": clean(row.get(mapping.get("round"))),
            "time": clean(row.get(mapping.get("time"))),
            "event_date": parse_date(clean(row.get(mapping.get("event_date")))),
            "weight_class": clean(row.get(mapping.get("weight_class"))),
            "source": "local_historical_csv",
            "source_url": clean(row.get(mapping.get("source_url"))),
            "scraped_at": now,
            "created_at": now,
        }
        prepared["source_hash"] = source_hash(prepared)
        if prepared["source_hash"] in seen_hashes:
            duplicate_rows += 1
            continue
        seen_hashes.add(prepared["source_hash"])
        rows.append(prepared)

    return rows, {
        "source_rows": source_rows,
        "invalid_rows": invalid_rows,
        "duplicate_source_rows": duplicate_rows,
    }


def detect_columns(columns: Iterable[str]) -> dict[str, str]:
    by_normalized = {normalize_column(col): col for col in columns}
    mapping = {}
    for logical, candidates in COLUMN_CANDIDATES.items():
        for candidate in candidates:
            if normalize_column(candidate) in by_normalized:
                mapping[logical] = by_normalized[normalize_column(candidate)]
                break
    return mapping


def build_event_rows(fights: list[dict]) -> list[dict]:
    rows = {}
    now = utc_now()
    for fight in fights:
        key = normalize_name(fight["event"])
        if not key:
            continue
        rows.setdefault(
            key,
            {
                "name": fight["event"],
                "normalized_name": key,
                "event_date": fight.get("event_date"),
                "location": None,
                "source": "local_historical_csv",
                "source_url": None,
                "source_hash": stable_hash(["local_historical_csv", fight["event"], fight.get("event_date") or ""]),
                "scraped_at": now,
                "updated_at": now,
            },
        )
    return list(rows.values())


def build_fighter_rows(fights: list[dict]) -> list[dict]:
    rows = {}
    now = utc_now()
    for fight in fights:
        for col in ("fighter_1", "fighter_2"):
            name = fight[col]
            key = normalize_name(name)
            if key:
                rows.setdefault(
                    key,
                    {
                        "name": name,
                        "normalized_name": key,
                        "weight_class": None,
                        "elo": settings.ELO_INITIAL,
                        "peak_elo": settings.ELO_INITIAL,
                        "elo_version": settings.ELO_ENGINE_VERSION,
                        "elo_fights_count": 0,
                        "elo_source": "baseline",
                        "updated_at": now,
                    },
                )
    return list(rows.values())


def upsert_events(conn, rows: list[dict]) -> None:
    if not rows:
        return
    conn.execute(
        text(
            """
            insert into events
                (name, normalized_name, event_date, location, source, source_url, source_hash, scraped_at, updated_at)
            values
                (:name, :normalized_name, :event_date, :location, :source, :source_url, :source_hash, :scraped_at, :updated_at)
            on conflict (normalized_name) do update set
                event_date = coalesce(excluded.event_date, events.event_date),
                source_hash = excluded.source_hash,
                updated_at = excluded.updated_at
            """
        ),
        rows,
    )


def upsert_minimal_fighters(conn, rows: list[dict]) -> None:
    if not rows:
        return
    conn.execute(
        text(
            """
            insert into fighters
                (name, normalized_name, weight_class, elo, peak_elo, elo_version, elo_fights_count, elo_source, updated_at)
            values
                (:name, :normalized_name, :weight_class, :elo, :peak_elo, :elo_version, :elo_fights_count, :elo_source, :updated_at)
            on conflict (normalized_name) do nothing
            """
        ),
        rows,
    )


def upsert_fights(conn, rows: list[dict], force: bool = False) -> None:
    if not rows:
        return
    conflict = (
        """
        do update set
            event = excluded.event,
            fighter_1 = excluded.fighter_1,
            fighter_2 = excluded.fighter_2,
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
        if force
        else "do nothing"
    )
    conn.execute(
        text(
            f"""
            insert into fights
                (event, fighter_1, fighter_2, result, method, round, time, source_hash,
                 event_date, weight_class, source, source_url, scraped_at, created_at)
            values
                (:event, :fighter_1, :fighter_2, :result, :method, :round, :time, :source_hash,
                 :event_date, :weight_class, :source, :source_url, :scraped_at, :created_at)
            on conflict (source_hash) {conflict}
            """
        ),
        rows,
    )


def fetch_existing_hashes(conn, hashes: list[str]) -> set[str]:
    if not hashes:
        return set()
    found: set[str] = set()
    stmt = text("select source_hash from fights where source_hash in :hashes").bindparams(bindparam("hashes", expanding=True))
    for chunk in chunks(hashes, 1000):
        found.update(row[0] for row in conn.execute(stmt, {"hashes": chunk}).fetchall())
    return found


def scalar_count(conn, table: str) -> int:
    return int(conn.execute(text(f"select count(*) from {table}")).scalar() or 0)


def chunks(values: list[str], size: int):
    for index in range(0, len(values), size):
        yield values[index : index + size]


def normalize_column(value: str) -> str:
    return str(value or "").strip().lower().replace(" ", "_").replace("-", "_")


def clean(value) -> str | None:
    if value is None or pd.isna(value):
        return None
    text_value = " ".join(str(value).replace("\xa0", " ").split())
    return text_value or None


def normalize_result(value: str | None) -> str:
    raw = clean(value)
    if not raw:
        return "unknown"
    lowered = raw.lower()
    if lowered.startswith("w") or lowered in {"win", "winner"}:
        return "win"
    if "draw" in lowered:
        return "draw"
    if "no contest" in lowered or lowered in {"nc", "n/c"}:
        return "nc"
    return lowered


def parse_date(value: str | None) -> str | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def source_hash(row: dict) -> str:
    return stable_hash([row.get(col) or "" for col in ["event", "fighter_1", "fighter_2", "result", "method", "round", "time"]])


def stable_hash(parts: list[str]) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _database_url() -> str:
    return os.environ.get("DATABASE_URL") or os.environ.get("SUPABASE_DB_URL") or settings.DATABASE_URL


def _engine() -> Engine:
    url = _database_url()
    if not url:
        raise RuntimeError("DATABASE_URL is not set. Set it before running a real import.")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    return create_engine(url, pool_pre_ping=True, connect_args={"prepare_threshold": None})


def print_summary(summary: ImportSummary) -> None:
    print("Historical fight import summary:")
    print(f"  source_file: {summary.source_file}")
    print(f"  source_rows: {summary.source_rows}")
    print(f"  prepared_fights: {summary.prepared_rows}")
    print(f"  duplicate_source_rows: {summary.duplicate_source_rows}")
    print(f"  invalid_rows: {summary.invalid_rows}")
    print(f"  events_seen: {summary.events_seen}")
    print(f"  fighters_seen: {summary.fighters_seen}")
    print(f"  fights_before: {summary.fights_before if summary.fights_before is not None else 'not checked'}")
    print(f"  expected_existing: {summary.expected_existing}")
    print(f"  expected_inserts: {summary.expected_inserts}")
    print(f"  fights_after: {summary.fights_after if summary.fights_after is not None else 'not written'}")
    print(f"  dry_run: {str(summary.dry_run).lower()}")


if __name__ == "__main__":
    raise SystemExit(main())
