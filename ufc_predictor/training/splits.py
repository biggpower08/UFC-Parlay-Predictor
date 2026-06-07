"""Split strategies for leakage-aware fight model evaluation."""

from __future__ import annotations

import pandas as pd


def chronological_split_df(df: pd.DataFrame, date_col: str = "event_date", test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    _validate_test_size(test_size)
    rows = df.copy()
    rows["_split_date"] = pd.to_datetime(rows.get(date_col), errors="coerce")
    if rows["_split_date"].isna().all():
        return rows.iloc[0:0].copy(), rows.copy(), {
            "split_type": "chronological",
            "status": "missing_dates",
            "model_status_modifier": "experimental",
            "warning": "Chronological split unavailable because event dates are missing.",
        }
    rows = rows.sort_values(["_split_date"], kind="mergesort").reset_index(drop=True)
    split_at = max(1, int(len(rows) * (1 - test_size)))
    return _drop_helper(rows.iloc[:split_at]), _drop_helper(rows.iloc[split_at:]), {
        "split_type": "chronological",
        "status": "ok",
        "train_rows": int(split_at),
        "test_rows": int(len(rows) - split_at),
        "model_status_modifier": "none",
    }


def event_grouped_split(df: pd.DataFrame, event_col: str = "event_name", date_col: str = "event_date", test_size: float = 0.2) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    _validate_test_size(test_size)
    if event_col not in df.columns:
        train, test, report = chronological_split_df(df, date_col=date_col, test_size=test_size)
        report["warning"] = f"Event grouped split fell back to chronological because {event_col} is missing."
        return train, test, report
    events = (
        df[[event_col, date_col]].copy()
        if date_col in df.columns
        else df[[event_col]].assign(**{date_col: pd.NaT})
    )
    events["_event_date"] = pd.to_datetime(events[date_col], errors="coerce")
    unique_events = events.drop_duplicates(event_col).sort_values(["_event_date", event_col], kind="mergesort")
    split_at = max(1, int(len(unique_events) * (1 - test_size)))
    train_events = set(unique_events.iloc[:split_at][event_col])
    test_events = set(unique_events.iloc[split_at:][event_col])
    train = df[df[event_col].isin(train_events)].copy()
    test = df[df[event_col].isin(test_events)].copy()
    return train, test, {
        "split_type": "event_grouped",
        "status": "ok",
        "train_events": len(train_events),
        "test_events": len(test_events),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "event_overlap": sorted(train_events & test_events),
    }


def random_stratified_split(df: pd.DataFrame, target_col: str, test_size: float = 0.2, random_state: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    _validate_test_size(test_size)
    if target_col not in df.columns:
        raise ValueError(f"{target_col} is required for stratified split.")
    sampled = df.sample(frac=1.0, random_state=random_state)
    train_parts = []
    test_parts = []
    for _label, group in sampled.groupby(target_col, dropna=False):
        split_at = max(1, int(len(group) * (1 - test_size)))
        train_parts.append(group.iloc[:split_at])
        test_parts.append(group.iloc[split_at:])
    train = pd.concat(train_parts).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    test = pd.concat(test_parts).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
    return train, test, {
        "split_type": "random_stratified",
        "status": "comparison_only",
        "warning": "Random split is useful for comparison only; it is not the headline future-fight metric.",
    }


def mirrored_group_key(row: pd.Series, fighter_a: str = "fighter_1", fighter_b: str = "fighter_2", event_col: str = "event_name") -> str:
    fighters = sorted([str(row.get(fighter_a) or ""), str(row.get(fighter_b) or "")])
    return "|".join([str(row.get(event_col) or ""), *fighters])


def _drop_helper(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop(columns=[column for column in ("_split_date",) if column in df.columns]).copy()


def _validate_test_size(test_size: float) -> None:
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")
