"""Shared helpers: names, safe numeric reads, stat column lookup."""

import pandas as pd


def normalize_name(name) -> str:
    if name is None or (isinstance(name, float) and pd.isna(name)):
        return ""
    return " ".join(str(name).strip().lower().split())


def safe_float(value, default=0.0) -> float:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def normalize_col(name: str) -> str:
    return str(name).lower().replace(" ", "").replace(".", "").replace("_", "")


def get_stat(row, *aliases, default=None):
    alias_norm = [normalize_col(a) for a in aliases]
    for col in row.index:
        col_norm = normalize_col(col)
        for alias in alias_norm:
            if alias in col_norm or col_norm in alias:
                val = row[col]
                if pd.isna(val):
                    return default
                return val
    return default


def find_name_column(df: pd.DataFrame) -> str:
    candidates = ["name", "fighter", "fighter_name", "Name", "Fighter"]
    lower_map = {c.lower(): c for c in df.columns}
    for key in candidates:
        if key.lower() in lower_map:
            return lower_map[key.lower()]
    raise ValueError(f"No name column found. Columns: {list(df.columns)}")
