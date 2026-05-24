"""Repository helpers for fighters, predictions, and scrape cache."""

import json
import sqlite3
import uuid
from datetime import date, datetime, timezone
from difflib import SequenceMatcher

import pandas as pd
from sqlalchemy import inspect
from sqlalchemy import text

from ufc_predictor.config import settings
from ufc_predictor.db.schema import connect, get_engine, init_db, table_exists as schema_table_exists, using_postgres
from ufc_predictor.utils.helpers import find_name_column, normalize_name
from ufc_predictor.utils.weight_classes import detect_weight_class


FIGHTERS_TABLE = "fighters"
INTEGER_COLUMNS = {"wins", "losses", "draws"}
DATE_COLUMNS = {"date_of_birth"}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def initialize_database(force_import: bool = False) -> None:
    init_db()
    if force_import or not table_exists(FIGHTERS_TABLE) or not _table_has_rows(FIGHTERS_TABLE):
        import_fighters_csv()


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
    out = df.copy()
    name_col = find_name_column(out)
    out["normalized_name"] = out[name_col].astype(str).map(normalize_name)
    out = out.drop_duplicates(subset=["normalized_name"], keep="first")
    out["_search_name"] = out["normalized_name"]
    if "elo" not in out.columns:
        out["elo"] = settings.ELO_INITIAL
    if "peak_elo" not in out.columns:
        out["peak_elo"] = out["elo"]
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
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(f"SELECT * FROM {FIGHTERS_TABLE}")).mappings().all()
        return pd.DataFrame([dict(row) for row in rows])
    with connect() as conn:
        return pd.read_sql_query(f"SELECT * FROM {FIGHTERS_TABLE}", conn)


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
    initialize_database()
    normalized = normalize_name(query)
    if not normalized:
        return []
    df = get_fighters_df()
    for col in ("nickname", "wins", "losses", "draws", "stance", "weight_in_kg", "reach_in_cm", "elo"):
        if col not in df.columns:
            df[col] = None
    name_col = find_name_column(df)
    rows = []
    for _, row in df.iterrows():
        name = str(row.get(name_col) or "")
        nickname = str(row.get("nickname") or "")
        name_key = normalize_name(name)
        nick_key = normalize_name(nickname)
        score, match_type = _match_score(normalized, name_key, nick_key)
        if score <= 0:
            continue
        item = row.to_dict()
        item["weight_class"] = detect_weight_class(row)
        item["_score"] = score
        item["_match_type"] = match_type
        rows.append(item)
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
        "_score",
        "_match_type",
    ]
    return matches[columns].to_dict(orient="records")


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
        return 0.92 - min(0.2, (len(name_key) - len(query)) / 100), "partial_name"
    if nick_key and query in nick_key:
        return 0.90 - min(0.2, (len(nick_key) - len(query)) / 100), "partial_nickname"

    name_score = SequenceMatcher(None, query, name_key).ratio()
    nick_score = SequenceMatcher(None, query, nick_key).ratio() if nick_key else 0
    if max(name_score, nick_score) < 0.58:
        return 0.0, "none"
    if nick_score > name_score:
        return nick_score * 0.86, "fuzzy_nickname"
    return name_score * 0.86, "fuzzy_name"


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


def update_elo_columns(elo_by_search: dict, peak_elo: dict | None = None) -> None:
    initialize_database()
    df = get_fighters_df()
    name_col = find_name_column(df)
    peak_elo = peak_elo or {}
    df["elo"] = df["normalized_name"].map(elo_by_search).fillna(settings.ELO_INITIAL)
    df["peak_elo"] = df[name_col].map(
        lambda n: peak_elo.get(n, elo_by_search.get(normalize_name(n), settings.ELO_INITIAL))
    )
    save_fighters_df(df, replace=True)


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
