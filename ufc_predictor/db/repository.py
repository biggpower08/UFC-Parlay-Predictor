"""Repository helpers for fighters, predictions, and scrape cache."""

import json
import sqlite3
import time
import uuid
from datetime import date, datetime, timezone
from difflib import SequenceMatcher

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import text

from ufc_predictor.config import settings
from ufc_predictor.db.schema import connect, get_engine, init_db, table_exists as schema_table_exists, using_postgres
from ufc_predictor.models.elo.history import build_elo_fight_history_rows, summarize_elo_trend
from ufc_predictor.utils.helpers import find_name_column, normalize_name
from ufc_predictor.utils.logger import get_logger
from ufc_predictor.utils.weight_classes import detect_weight_class


FIGHTERS_TABLE = "fighters"
INTEGER_COLUMNS = {"wins", "losses", "draws", "elo_fights_count"}
DATE_COLUMNS = {"date_of_birth"}
FIGHTERS_CACHE_TTL_SECONDS = 60
logger = get_logger(__name__)
_initialized = False
_fighters_cache: tuple[float, pd.DataFrame] | None = None


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_database(force_import: bool = False) -> None:
    global _initialized
    if _initialized and not force_import:
        return
    start = time.perf_counter()
    init_db()
    if force_import or not table_exists(FIGHTERS_TABLE) or not _table_has_rows(FIGHTERS_TABLE):
        import_fighters_csv()
    _initialized = True
    _log_timing("repository.initialize_database", start)


def table_exists(table_name: str) -> bool:
    return schema_table_exists(table_name)


def _table_has_rows(table_name: str) -> bool:
    if not table_exists(table_name):
        return False
    if using_postgres():
        with get_engine().begin() as conn:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar_one()
        return count > 0
    with connect() as conn:
        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    return count > 0


def import_fighters_csv(path=None) -> pd.DataFrame:
    path = path or settings.FIGHTERS_CSV
    if not path.is_file():
        raise FileNotFoundError(f"Fighter CSV not found: {path}")
    df = pd.read_csv(path)
    return save_fighters_df(df, replace=True)


def save_fighters_df(df: pd.DataFrame, replace: bool = True) -> pd.DataFrame:
    _invalidate_fighters_cache()
    out = df.copy()
    name_col = find_name_column(out)
    out["normalized_name"] = out[name_col].astype(str).map(normalize_name)
    out = out.drop_duplicates(subset=["normalized_name"], keep="first")
    out["_search_name"] = out["normalized_name"]
    if "elo" not in out.columns:
        out["elo"] = settings.ELO_INITIAL
    if "peak_elo" not in out.columns:
        out["peak_elo"] = out["elo"]
    if "elo_version" not in out.columns:
        out["elo_version"] = "v1"
    if "elo_computed_at" not in out.columns:
        out["elo_computed_at"] = None
    if "elo_fights_count" not in out.columns:
        out["elo_fights_count"] = 0
    if "elo_source" not in out.columns:
        out["elo_source"] = out.apply(
            lambda row: "computed"
            if safe_int(row.get("elo_fights_count")) > 0 or safe_float(row.get("elo"), settings.ELO_INITIAL) != settings.ELO_INITIAL
            else "baseline",
            axis=1,
        )
    if "weight_class" not in out.columns:
        out["weight_class"] = out.apply(detect_weight_class, axis=1)
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if using_postgres():
        engine = get_engine()
        db_columns = [col["name"] for col in inspect(engine).get_columns(FIGHTERS_TABLE)]
        out_db = out[[col for col in out.columns if col in db_columns and col != "id"]].copy()
        records = [_clean_db_record(record) for record in out_db.to_dict(orient="records")]
        columns = list(records[0].keys()) if records else list(out_db.columns)
        placeholders = ", ".join(f":{col}" for col in columns)
        column_list = ", ".join(columns)
        insert_sql = text(f"INSERT INTO {FIGHTERS_TABLE} ({column_list}) VALUES ({placeholders})")
        with engine.begin() as conn:
            if replace and table_exists(FIGHTERS_TABLE):
                conn.execute(text(f"DELETE FROM {FIGHTERS_TABLE}"))
            if records:
                for start in range(0, len(records), 500):
                    conn.execute(insert_sql, records[start : start + 500])
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_fighters_normalized_name ON fighters(normalized_name)"))
        return out

    with connect() as conn:
        out.to_sql(FIGHTERS_TABLE, conn, if_exists="replace" if replace else "append", index=False)
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_fighters_normalized_name ON fighters(normalized_name)"
        )
        conn.commit()
    return out


def get_fighters_df() -> pd.DataFrame:
    initialize_database()
    global _fighters_cache
    if _fighters_cache and time.monotonic() - _fighters_cache[0] < FIGHTERS_CACHE_TTL_SECONDS:
        return _fighters_cache[1].copy()
    start = time.perf_counter()
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(f"SELECT * FROM {FIGHTERS_TABLE}")).mappings().all()
        df = pd.DataFrame([dict(row) for row in rows])
        _fighters_cache = (time.monotonic(), df)
        _log_timing("repository.get_fighters_df", start, rows=len(df))
        return df.copy()
    with connect() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {FIGHTERS_TABLE}", conn)
    _fighters_cache = (time.monotonic(), df)
    _log_timing("repository.get_fighters_df", start, rows=len(df))
    return df.copy()


def _clean_db_record(record: dict) -> dict:
    clean = {}
    for key, value in record.items():
        if pd.isna(value):
            clean[key] = None
            continue
        if key in INTEGER_COLUMNS:
            clean[key] = int(value)
            continue
        if key in DATE_COLUMNS:
            if isinstance(value, date):
                clean[key] = value
            else:
                clean[key] = str(value)[:10] if str(value).strip() else None
            continue
        clean[key] = value
    return clean


def search_fighters(query: str, limit: int = 12) -> list[dict]:
    return find_fighter_candidates(query, limit=limit)


def find_fighter_candidates(query: str, limit: int = 8) -> list[dict]:
    start = time.perf_counter()
    initialize_database()
    normalized = normalize_name(query)
    if not normalized:
        return []
    df = get_fighters_df()
    for col in (
        "nickname",
        "wins",
        "losses",
        "draws",
        "stance",
        "weight_in_kg",
        "reach_in_cm",
        "elo",
        "elo_fights_count",
        "elo_source",
        "elo_computed_at",
    ):
        if col not in df.columns:
            df[col] = None
    name_col = find_name_column(df)
    search_df = df.copy()
    search_df["_name_key"] = search_df.get("normalized_name", search_df[name_col]).fillna("").astype(str)
    if "normalized_name" not in search_df.columns:
        search_df["_name_key"] = search_df[name_col].fillna("").astype(str).map(normalize_name)
    search_df["_nick_key"] = search_df["nickname"].fillna("").astype(str).map(normalize_name)

    rows = []
    seen = set()

    def add_row(row, score: float, match_type: str) -> None:
        key = row.get("normalized_name") or row.get("_name_key") or normalize_name(row.get(name_col))
        if not key or key in seen:
            return
        seen.add(key)
        item = row.to_dict()
        item["weight_class"] = detect_weight_class(row)
        item["_score"] = score
        item["_match_type"] = match_type
        rows.append(item)

    exact_name = search_df["_name_key"] == normalized
    exact_nick = search_df["_nick_key"] == normalized
    for _, row in search_df.loc[exact_name].iterrows():
        add_row(row, 1.0, "exact_name")
    for _, row in search_df.loc[exact_nick].iterrows():
        add_row(row, 0.98, "exact_nickname")

    partial_name = search_df["_name_key"].str.contains(normalized, regex=False, na=False)
    partial_nick = search_df["_nick_key"].str.contains(normalized, regex=False, na=False)
    for _, row in search_df.loc[partial_name].iterrows():
        score = _partial_score(normalized, str(row["_name_key"]), 0.96, 0.86)
        add_row(row, score, "partial_name")
    for _, row in search_df.loc[partial_nick].iterrows():
        score = _partial_score(normalized, str(row["_nick_key"]), 0.94, 0.84)
        add_row(row, score, "partial_nickname")

    if len(rows) < limit and len(normalized) >= 3:
        for _, row in search_df.iterrows():
            key = row.get("normalized_name") or row.get("_name_key")
            if key in seen:
                continue
            score, match_type = _match_score(normalized, str(row["_name_key"]), str(row["_nick_key"]))
            if score > 0:
                add_row(row, score, match_type)
    if not rows:
        return []
    matches = pd.DataFrame(rows).sort_values(
        ["_score", "normalized_name"],
        ascending=[False, True],
    ).head(limit)
    matches = matches.rename(columns={name_col: "name"})
    columns = [
        "name",
        "nickname",
        "wins",
        "losses",
        "draws",
        "stance",
        "weight_in_kg",
        "weight_class",
        "reach_in_cm",
        "elo",
        "elo_fights_count",
        "elo_source",
        "elo_computed_at",
        "_score",
        "_match_type",
    ]
    result = matches[columns].to_dict(orient="records")
    _log_timing("repository.find_fighter_candidates", start, query=query, matches=len(result))
    return result


def resolve_name(query: str) -> dict:
    normalized = normalize_name(query)
    candidates = find_fighter_candidates(query, limit=5)
    if not candidates:
        return {
            "status": "needs_full_name",
            "query": query,
            "resolved_name": None,
            "candidates": [],
            "message": "I could not recognize that fighter. Please enter the full fighter name.",
        }

    best = candidates[0]
    exact = best["_match_type"] in {"exact_name", "exact_nickname"}
    clear_single = len(candidates) == 1 and best["_score"] >= 0.82
    clear_lead = len(candidates) > 1 and best["_score"] >= 0.88 and best["_score"] - candidates[1]["_score"] >= 0.12
    if exact or clear_single or clear_lead:
        return {
            "status": "resolved",
            "query": query,
            "resolved_name": best["name"],
            "candidates": candidates,
            "message": f"Resolved {query} to {best['name']}.",
        }

    return {
        "status": "needs_confirmation",
        "query": query,
        "resolved_name": best["name"],
        "candidates": candidates,
        "message": f"Did you mean {best['name']}?",
    }


def _match_score(query: str, name_key: str, nick_key: str) -> tuple[float, str]:
    if query == name_key:
        return 1.0, "exact_name"
    if nick_key and query == nick_key:
        return 0.98, "exact_nickname"
    if query in name_key:
        return _partial_score(query, name_key, 0.96, 0.86), "partial_name"
    if nick_key and query in nick_key:
        return _partial_score(query, nick_key, 0.94, 0.84), "partial_nickname"

    name_score = SequenceMatcher(None, query, name_key).ratio()
    nick_score = SequenceMatcher(None, query, nick_key).ratio() if nick_key else 0
    if max(name_score, nick_score) < 0.58:
        return 0.0, "none"
    if nick_score > name_score:
        return nick_score * 0.86, "fuzzy_nickname"
    return name_score * 0.86, "fuzzy_name"


def _partial_score(query: str, value: str, prefix_base: float, contains_base: float) -> float:
    if value.startswith(query) or any(part.startswith(query) for part in value.split()):
        return prefix_base - min(0.12, (len(value) - len(query)) / 160)
    return contains_base - min(0.16, (len(value) - len(query)) / 120)


def get_fighter_by_name(name: str) -> pd.Series | None:
    initialize_database()
    normalized = normalize_name(name)
    if using_postgres():
        with get_engine().begin() as conn:
            row = conn.execute(
                text("SELECT * FROM fighters WHERE normalized_name = :normalized LIMIT 1"),
                {"normalized": normalized},
            ).mappings().fetchone()
        return pd.Series(dict(row)) if row else None

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM fighters WHERE normalized_name = ? LIMIT 1",
            (normalized,),
        ).fetchone()
    return pd.Series(dict(row)) if row else None


def upsert_fighter(record: dict) -> pd.Series:
    initialize_database()
    df = get_fighters_df()
    name = record.get("name") or record.get("Name") or record.get("fighter")
    if not name:
        raise ValueError("Cannot upsert fighter without a name")
    normalized = normalize_name(name)
    record = {**record, "name": name, "normalized_name": normalized, "_search_name": normalized}
    for col in df.columns:
        record.setdefault(col, None)
    new_row = pd.DataFrame([{col: record.get(col) for col in df.columns}])
    df = df[df["normalized_name"] != normalized]
    df = pd.concat([df, new_row], ignore_index=True)
    save_fighters_df(df, replace=True)
    return new_row.iloc[0]


def update_elo_columns(
    elo_by_search: dict,
    peak_elo: dict | None = None,
    elo_version: str = "v1",
    fight_counts: dict | None = None,
    computed_at: str | None = None,
) -> None:
    initialize_database()
    df = get_fighters_df()
    name_col = find_name_column(df)
    peak_elo = peak_elo or {}
    fight_counts = fight_counts or {}
    computed_at = computed_at or _utc_now()
    df["elo"] = df["normalized_name"].map(elo_by_search).fillna(settings.ELO_INITIAL)
    df["peak_elo"] = df[name_col].map(
        lambda n: peak_elo.get(n, elo_by_search.get(normalize_name(n), settings.ELO_INITIAL))
    )
    df["elo_fights_count"] = df["normalized_name"].map(fight_counts).fillna(0).astype(int)
    df["elo_source"] = df["elo_fights_count"].map(lambda count: "computed" if int(count) > 0 else "baseline")
    df["elo_version"] = elo_version
    df["elo_computed_at"] = df["elo_source"].map(lambda source: computed_at if source == "computed" else None)
    save_fighters_df(df, replace=True)
    logger.info(
        "Updated latest Elo columns fighters=%s computed=%s baseline=%s version=%s",
        len(df),
        int((df["elo_source"] == "computed").sum()),
        int((df["elo_source"] == "baseline").sum()),
        elo_version,
    )


def replace_elo_history(
    elo_ratings: dict,
    peak_elo: dict | None = None,
    elo_version: str = "v1",
    computed_at: str | None = None,
) -> int:
    """Replace the latest Elo snapshot for one engine version.

    The table stores a rerunnable snapshot per Elo version, so refreshing the same
    version deletes stale rows before inserting the newly computed ratings.
    """
    init_db()
    peak_elo = peak_elo or {}
    computed_at = computed_at or _utc_now()
    rows = [
        {
            "fighter_name": fighter_name,
            "normalized_name": normalize_name(fighter_name),
            "elo": float(elo),
            "peak_elo": float(peak_elo.get(fighter_name, elo)),
            "elo_version": elo_version,
            "computed_at": computed_at,
        }
        for fighter_name, elo in elo_ratings.items()
    ]
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text("DELETE FROM fighter_elo_history WHERE elo_version = :elo_version"),
                {"elo_version": elo_version},
            )
            if rows:
                conn.execute(
                    text(
                        """
                        INSERT INTO fighter_elo_history
                            (fighter_name, normalized_name, elo, peak_elo, elo_version, computed_at)
                        VALUES
                            (:fighter_name, :normalized_name, :elo, :peak_elo, :elo_version, :computed_at)
                        """
                    ),
                    rows,
                )
        logger.info("Replaced Elo history rows=%s version=%s", len(rows), elo_version)
        return len(rows)

    with connect() as conn:
        conn.execute("DELETE FROM fighter_elo_history WHERE elo_version = ?", (elo_version,))
        conn.executemany(
            """
            INSERT INTO fighter_elo_history
                (fighter_name, normalized_name, elo, peak_elo, elo_version, computed_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["fighter_name"],
                    row["normalized_name"],
                    row["elo"],
                    row["peak_elo"],
                    row["elo_version"],
                    row["computed_at"],
                )
                for row in rows
            ],
        )
        conn.commit()
    logger.info("Replaced Elo history rows=%s version=%s", len(rows), elo_version)
    return len(rows)


def replace_elo_fight_history(
    fights_elo: pd.DataFrame,
    elo_version: str = "v1",
    computed_at: str | None = None,
) -> int:
    """Replace true fight-by-fight Elo history for one engine version."""
    init_db()
    computed_at = computed_at or _utc_now()
    rows = build_elo_fight_history_rows(fights_elo, elo_version=elo_version, computed_at=computed_at)
    columns = [
        "fighter_name",
        "normalized_name",
        "opponent_name",
        "opponent_normalized_name",
        "event",
        "event_date",
        "fight_id",
        "source_hash",
        "weight_class",
        "result",
        "method",
        "round",
        "elo_before",
        "elo_after",
        "elo_change",
        "opponent_elo_before",
        "expected_score",
        "elo_version",
        "order_source",
        "computed_at",
    ]
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text("DELETE FROM fighter_elo_fight_history WHERE elo_version = :elo_version"),
                {"elo_version": elo_version},
            )
            if rows:
                conn.execute(
                    text(
                        f"""
                        INSERT INTO fighter_elo_fight_history
                            ({", ".join(columns)})
                        VALUES
                            ({", ".join(f":{column}" for column in columns)})
                        """
                    ),
                    rows,
                )
        logger.info("Replaced fight-by-fight Elo history rows=%s version=%s", len(rows), elo_version)
        return len(rows)

    with connect() as conn:
        conn.execute("DELETE FROM fighter_elo_fight_history WHERE elo_version = ?", (elo_version,))
        if rows:
            conn.executemany(
                f"""
                INSERT INTO fighter_elo_fight_history
                    ({", ".join(columns)})
                VALUES
                    ({", ".join(["?"] * len(columns))})
                """,
                [tuple(row.get(column) for column in columns) for row in rows],
            )
        conn.commit()
    logger.info("Replaced fight-by-fight Elo history rows=%s version=%s", len(rows), elo_version)
    return len(rows)


def query_elo_fight_history(normalized_name: str, limit: int = 10, elo_version: str = "v1") -> list[dict]:
    """Return recent true fight-by-fight Elo history rows for one fighter."""
    init_db()
    limit = min(max(int(limit), 1), 50)
    params = {"normalized_name": normalized_name, "elo_version": elo_version, "limit": limit}
    sql = """
        SELECT fighter_name, normalized_name, opponent_name, opponent_normalized_name,
               event, event_date, fight_id, source_hash, weight_class, result, method, round,
               elo_before, elo_after, elo_change, opponent_elo_before, expected_score,
               elo_version, order_source, computed_at
        FROM fighter_elo_fight_history
        WHERE normalized_name = :normalized_name AND elo_version = :elo_version
        ORDER BY event_date DESC NULLS LAST, id DESC
        LIMIT :limit
    """
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]

    sqlite_sql = sql.replace(" DESC NULLS LAST", " IS NULL ASC, event_date DESC")
    with connect() as conn:
        rows = conn.execute(sqlite_sql, params).fetchall()
    return [dict(row) for row in rows]


def query_elo_trend_summary(normalized_name: str, elo_version: str = "v1") -> dict:
    """Return a lightweight Elo trend summary backed by fight-by-fight history."""
    init_db()
    snapshot = _query_fighter_elo_snapshot(normalized_name)
    params = {"normalized_name": normalized_name, "elo_version": elo_version}
    sql = """
        SELECT id, fighter_name, normalized_name, opponent_name, event, event_date,
               result, elo_after, elo_change, elo_version
        FROM fighter_elo_fight_history
        WHERE normalized_name = :normalized_name AND elo_version = :elo_version
        ORDER BY event_date ASC NULLS LAST, id ASC
    """
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        history = [dict(row) for row in rows]
    else:
        sqlite_sql = sql.replace(" ASC NULLS LAST", " IS NULL ASC, event_date ASC")
        with connect() as conn:
            rows = conn.execute(sqlite_sql, params).fetchall()
        history = [dict(row) for row in rows]

    return summarize_elo_trend(
        history,
        current_elo=snapshot.get("elo"),
        peak_elo=snapshot.get("peak_elo"),
        elo_fights_count=snapshot.get("elo_fights_count"),
        elo_version=snapshot.get("elo_version") or elo_version,
    )


def _query_fighter_elo_snapshot(normalized_name: str) -> dict:
    if using_postgres():
        with get_engine().begin() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT elo, peak_elo, elo_fights_count, elo_version
                    FROM fighters
                    WHERE normalized_name = :normalized_name
                    LIMIT 1
                    """
                ),
                {"normalized_name": normalized_name},
            ).mappings().fetchone()
        return dict(row) if row else {"elo_fights_count": 0}

    with connect() as conn:
        row = conn.execute(
            """
            SELECT elo, peak_elo, elo_fights_count, elo_version
            FROM fighters
            WHERE normalized_name = ?
            LIMIT 1
            """,
            (normalized_name,),
        ).fetchone()
    return dict(row) if row else {"elo_fights_count": 0}


def safe_int(value, default: int = 0) -> int:
    try:
        if pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _invalidate_fighters_cache() -> None:
    global _fighters_cache
    _fighters_cache = None


def _log_timing(label: str, start: float, **fields) -> None:
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    extra = " ".join(f"{key}={value}" for key, value in fields.items() if value is not None)
    logger.info("timing %s elapsed_ms=%s%s", label, elapsed_ms, f" {extra}" if extra else "")


def save_scrape_cache(normalized_name: str, source: str, url: str, raw: dict, confidence: float) -> None:
    init_db()
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO scrape_cache
                        (normalized_name, source, url, raw_json, confidence, fetched_at)
                    VALUES (:normalized_name, :source, :url, CAST(:raw_json AS jsonb), :confidence, :fetched_at)
                    ON CONFLICT (normalized_name) DO UPDATE SET
                        source = EXCLUDED.source,
                        url = EXCLUDED.url,
                        raw_json = EXCLUDED.raw_json,
                        confidence = EXCLUDED.confidence,
                        fetched_at = EXCLUDED.fetched_at
                    """
                ),
                {
                    "normalized_name": normalized_name,
                    "source": source,
                    "url": url,
                    "raw_json": json.dumps(raw),
                    "confidence": confidence,
                    "fetched_at": _utc_now(),
                },
            )
        return

    with connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO scrape_cache
                (normalized_name, source, url, raw_json, confidence, fetched_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (normalized_name, source, url, json.dumps(raw), confidence, _utc_now()),
        )
        conn.commit()


def get_scrape_cache(normalized_name: str) -> dict | None:
    init_db()
    if using_postgres():
        with get_engine().begin() as conn:
            row = conn.execute(
                text("SELECT * FROM scrape_cache WHERE normalized_name = :normalized_name"),
                {"normalized_name": normalized_name},
            ).mappings().fetchone()
        if not row:
            return None
        out = dict(row)
        raw = out.pop("raw_json")
        out["raw"] = raw if isinstance(raw, dict) else json.loads(raw)
        return out

    with connect() as conn:
        row = conn.execute(
            "SELECT * FROM scrape_cache WHERE normalized_name = ?",
            (normalized_name,),
        ).fetchone()
    if not row:
        return None
    out = dict(row)
    out["raw"] = json.loads(out.pop("raw_json"))
    return out


def save_prediction(fighter_a: str, fighter_b: str, prediction: dict, payload: dict) -> str:
    init_db()
    prediction_id = prediction.get("prediction_id") or str(uuid.uuid4())
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO predictions
                        (prediction_id, fighter_a, fighter_b, winner, confidence, model, payload_json, created_at)
                    VALUES
                        (:prediction_id, :fighter_a, :fighter_b, :winner, :confidence, :model,
                         CAST(:payload_json AS jsonb), :created_at)
                    ON CONFLICT (prediction_id) DO UPDATE SET
                        fighter_a = EXCLUDED.fighter_a,
                        fighter_b = EXCLUDED.fighter_b,
                        winner = EXCLUDED.winner,
                        confidence = EXCLUDED.confidence,
                        model = EXCLUDED.model,
                        payload_json = EXCLUDED.payload_json,
                        created_at = EXCLUDED.created_at
                    """
                ),
                {
                    "prediction_id": prediction_id,
                    "fighter_a": fighter_a,
                    "fighter_b": fighter_b,
                    "winner": prediction.get("winner"),
                    "confidence": prediction.get("confidence"),
                    "model": prediction.get("model"),
                    "payload_json": json.dumps(payload, default=str),
                    "created_at": _utc_now(),
                },
            )
        return prediction_id

    with connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO predictions
                (prediction_id, fighter_a, fighter_b, winner, confidence, model, payload_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prediction_id,
                fighter_a,
                fighter_b,
                prediction.get("winner"),
                prediction.get("confidence"),
                prediction.get("model"),
                json.dumps(payload, default=str),
                _utc_now(),
            ),
        )
        conn.commit()
    return prediction_id
