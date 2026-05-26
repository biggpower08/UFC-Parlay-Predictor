"""Generate Elo rankings and weight-class summaries."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from ufc_predictor.config import settings
from ufc_predictor.data.sync import load_fights_table, replace_weight_class_history
from ufc_predictor.db import repository
from ufc_predictor.db.schema import connect, get_engine, init_db, using_postgres
from ufc_predictor.utils.helpers import find_name_column, normalize_name
from ufc_predictor.utils.weight_classes import detect_weight_class


def generate_rankings(export_csv: bool = False, output_dir: Path | None = None, dry_run: bool = False) -> dict:
    init_db()
    fighters = repository.get_fighters_df()
    if fighters.empty:
        return {"rankings": 0, "weight_class_history": 0}

    name_col = find_name_column(fighters)
    fighters = fighters.copy()
    fighters["fighter_name"] = fighters[name_col]
    fighters["normalized_name"] = fighters["fighter_name"].astype(str).map(normalize_name)
    fighters["weight_class"] = fighters.apply(detect_weight_class, axis=1)
    fighters["elo"] = pd.to_numeric(fighters.get("elo", settings.ELO_INITIAL), errors="coerce").fillna(settings.ELO_INITIAL)
    fighters["peak_elo"] = pd.to_numeric(fighters.get("peak_elo", fighters["elo"]), errors="coerce").fillna(fighters["elo"])
    fighters["elo_fights_count"] = pd.to_numeric(fighters.get("elo_fights_count", 0), errors="coerce").fillna(0).astype(int)
    fighters["wins"] = pd.to_numeric(fighters.get("wins", 0), errors="coerce").fillna(0).astype(int)
    fighters["losses"] = pd.to_numeric(fighters.get("losses", 0), errors="coerce").fillna(0).astype(int)

    eligible = fighters[fighters["elo_fights_count"] > 0].copy()
    ranking_rows = []
    ranking_rows.extend(_ranking_rows(eligible, "overall_current_elo", "elo"))
    ranking_rows.extend(_ranking_rows(eligible, "overall_peak_elo", "peak_elo"))
    for weight_class, group in eligible.groupby("weight_class"):
        if not weight_class or str(weight_class).lower() == "unknown":
            continue
        ranking_rows.extend(_ranking_rows(group, "weight_class_current_elo", "elo", weight_class=str(weight_class)))

    weight_history = build_weight_class_history(load_fights_table())
    if not dry_run:
        replace_rankings(ranking_rows)
        replace_weight_class_history(weight_history)

    if export_csv:
        export_rankings_csv(ranking_rows, output_dir)
    return {"rankings": len(ranking_rows), "weight_class_history": len(weight_history)}


def build_weight_class_history(fights: pd.DataFrame) -> list[dict]:
    if fights.empty or "weight_class" not in fights.columns:
        return []
    rows = []
    records = {}
    for _, fight in fights.iterrows():
        weight_class = fight.get("weight_class")
        if not weight_class or str(weight_class).lower() == "unknown":
            continue
        event_date = fight.get("event_date")
        for col in ("fighter_1", "fighter_2"):
            fighter = fight.get(col)
            key = (normalize_name(fighter), str(weight_class))
            if not key[0]:
                continue
            item = records.setdefault(
                key,
                {
                    "fighter_name": fighter,
                    "normalized_name": key[0],
                    "weight_class": str(weight_class),
                    "fights_count": 0,
                    "first_seen": event_date,
                    "last_seen": event_date,
                    "inferred_from_fights": True,
                    "confidence": 0.0,
                },
            )
            item["fights_count"] += 1
            item["first_seen"] = _min_date(item["first_seen"], event_date)
            item["last_seen"] = _max_date(item["last_seen"], event_date)
    for item in records.values():
        item["confidence"] = min(1.0, 0.5 + item["fights_count"] * 0.1)
        rows.append(item)
    return rows


def replace_rankings(rows: list[dict]) -> int:
    init_db()
    generated_at = datetime.now(timezone.utc).isoformat()
    for row in rows:
        row["generated_at"] = generated_at
    if using_postgres():
        with get_engine().begin() as conn:
            conn.execute(text("delete from fighter_rankings"))
            if rows:
                conn.execute(
                    text(
                        """
                        insert into fighter_rankings
                            (fighter_name, normalized_name, ranking_type, weight_class, rank, elo, peak_elo,
                             fights_count, wins, losses, generated_at, source)
                        values
                            (:fighter_name, :normalized_name, :ranking_type, :weight_class, :rank, :elo, :peak_elo,
                             :fights_count, :wins, :losses, :generated_at, :source)
                        """
                    ),
                    rows,
                )
        return len(rows)
    with connect() as conn:
        conn.execute("delete from fighter_rankings")
        conn.executemany(
            """
            insert into fighter_rankings
                (fighter_name, normalized_name, ranking_type, weight_class, rank, elo, peak_elo,
                 fights_count, wins, losses, generated_at, source)
            values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    row["fighter_name"],
                    row["normalized_name"],
                    row["ranking_type"],
                    row["weight_class"],
                    row["rank"],
                    row["elo"],
                    row["peak_elo"],
                    row["fights_count"],
                    row["wins"],
                    row["losses"],
                    row["generated_at"],
                    row["source"],
                )
                for row in rows
            ],
        )
        conn.commit()
    return len(rows)


def query_rankings(ranking_type: str = "overall_current_elo", weight_class: str | None = None, limit: int = 50) -> list[dict]:
    init_db()
    limit = min(max(int(limit), 1), 200)
    params = {"ranking_type": ranking_type, "limit": limit}
    where = "ranking_type = :ranking_type"
    if weight_class:
        where += " and weight_class = :weight_class"
        params["weight_class"] = weight_class
    sql = f"""
        select fighter_name, normalized_name, ranking_type, weight_class, rank, elo, peak_elo,
               fights_count, wins, losses, generated_at, source
        from fighter_rankings
        where {where}
        order by rank asc
        limit :limit
    """
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def query_elo_history(normalized_name: str, limit: int = 100) -> list[dict]:
    init_db()
    params = {"normalized_name": normalized_name, "limit": min(max(int(limit), 1), 500)}
    sql = """
        select fighter_name, normalized_name, elo, peak_elo, elo_version, computed_at
        from fighter_elo_history
        where normalized_name = :normalized_name
        order by computed_at desc
        limit :limit
    """
    if using_postgres():
        with get_engine().begin() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
        return [dict(row) for row in rows]
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(row) for row in rows]


def export_rankings_csv(rows: list[dict], output_dir: Path | None = None) -> None:
    output_dir = Path(output_dir or settings.DATA_PROCESSED_DIR / "exports")
    output_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows)
    if not df.empty:
        for ranking_type, group in df.groupby("ranking_type"):
            group.to_csv(output_dir / f"{ranking_type}.csv", index=False)


def _ranking_rows(df: pd.DataFrame, ranking_type: str, sort_col: str, weight_class: str | None = None) -> list[dict]:
    out = []
    ranked = df.sort_values([sort_col, "fighter_name"], ascending=[False, True]).reset_index(drop=True)
    for idx, row in ranked.iterrows():
        out.append(
            {
                "fighter_name": row["fighter_name"],
                "normalized_name": row["normalized_name"],
                "ranking_type": ranking_type,
                "weight_class": weight_class,
                "rank": int(idx + 1),
                "elo": float(row["elo"]),
                "peak_elo": float(row["peak_elo"]),
                "fights_count": int(row["elo_fights_count"]),
                "wins": int(row["wins"]),
                "losses": int(row["losses"]),
                "source": settings.ELO_ENGINE_VERSION,
            }
        )
    return out


def _min_date(a, b):
    if not a:
        return b
    if not b:
        return a
    return min(str(a), str(b))


def _max_date(a, b):
    if not a:
        return b
    if not b:
        return a
    return max(str(a), str(b))
