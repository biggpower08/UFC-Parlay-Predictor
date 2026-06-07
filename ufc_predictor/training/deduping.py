"""Deduping helpers for normalized MMA fight rows."""

from __future__ import annotations

import hashlib
from typing import Any

import pandas as pd

from ufc_predictor.utils.helpers import normalize_name


def stable_fight_key(row: dict[str, Any] | pd.Series) -> str:
    event_date = _clean(row.get("event_date"))
    event = _clean(row.get("event_name") or row.get("event"))
    f1 = normalize_name(row.get("fighter_1_name") or row.get("fighter_1") or row.get("fighter_a") or "")
    f2 = normalize_name(row.get("fighter_2_name") or row.get("fighter_2") or row.get("fighter_b") or "")
    pair = "__vs__".join(sorted([f1, f2]))
    context = _clean(row.get("weight_class") or row.get("scheduled_rounds") or "")
    raw = "|".join([event_date, event, pair, context])
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:24]


def mirrored_pair_key(row: dict[str, Any] | pd.Series) -> str:
    f1 = normalize_name(row.get("fighter_1_name") or row.get("fighter_1") or row.get("fighter_a") or "")
    f2 = normalize_name(row.get("fighter_2_name") or row.get("fighter_2") or row.get("fighter_b") or "")
    return "__vs__".join(sorted([f1, f2]))


def add_deduping_columns(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    out = df.copy()
    out["fight_key"] = out.apply(stable_fight_key, axis=1)
    out["mirrored_pair_key"] = out.apply(mirrored_pair_key, axis=1)
    out["duplicate_fight_key"] = out.duplicated("fight_key", keep=False)
    mirrored_cols = ["event_date", "mirrored_pair_key"]
    if all(column in out.columns for column in mirrored_cols):
        out["mirrored_row_candidate"] = out.duplicated(mirrored_cols, keep=False)
    else:
        out["mirrored_row_candidate"] = False
    return out


def dedupe_summary(df: pd.DataFrame) -> dict[str, int]:
    if df.empty:
        return {"rows": 0, "unique_fight_keys": 0, "duplicate_fight_rows": 0, "mirrored_candidates": 0}
    keyed = add_deduping_columns(df)
    return {
        "rows": int(len(keyed)),
        "unique_fight_keys": int(keyed["fight_key"].nunique()),
        "duplicate_fight_rows": int(keyed["duplicate_fight_key"].sum()),
        "mirrored_candidates": int(keyed["mirrored_row_candidate"].sum()),
    }


def _clean(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().lower()
