"""Elo rating engine for UFC fight history."""

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def expected_score(elo_a: float, elo_b: float) -> float:
    return 1 / (1 + 10 ** ((elo_b - elo_a) / 400))


def update_elo_win(winner_elo, loser_elo, k_factor=None):
    k = k_factor or settings.ELO_K_FACTOR
    expected_win = expected_score(winner_elo, loser_elo)
    new_winner = winner_elo + k * (1 - expected_win)
    new_loser = loser_elo + k * (0 - (1 - expected_win))
    return round(new_winner, 2), round(new_loser, 2)


def update_elo_draw(elo_a, elo_b, k_factor=None):
    k = k_factor or settings.ELO_K_FACTOR
    exp_a = expected_score(elo_a, elo_b)
    exp_b = expected_score(elo_b, elo_a)
    new_a = elo_a + k * (0.5 - exp_a)
    new_b = elo_b + k * (0.5 - exp_b)
    return round(new_a, 2), round(new_b, 2)


def _normalize_result(result):
    if pd.isna(result):
        return "nc"
    normalized = str(result).lower().strip().split("\n")[0]
    if normalized in {"no contest", "no-contest", "no_contest", "nc"}:
        return "nc"
    if normalized in {"unknown", "nan", ""}:
        return "unknown"
    return normalized


def prepare_fights_chronological(fights_df: pd.DataFrame) -> pd.DataFrame:
    df = fights_df.copy()
    if "event" not in df.columns:
        df = df.reset_index()
    df["_original_order"] = range(len(df))
    df["result"] = df["result"].apply(_normalize_result)
    df["elo_order_source"] = "source_order_inferred"

    if "event_date" in df.columns:
        parsed_dates = pd.to_datetime(df["event_date"], errors="coerce")
        if parsed_dates.notna().any():
            df["_event_date_sort"] = parsed_dates
            sort_columns = ["_event_date_sort"]
            order_column = _first_existing_column(df, ("fight_order", "bout_order", "source_order", "card_order"))
            if order_column:
                df["_fight_order_sort"] = pd.to_numeric(df[order_column], errors="coerce")
                sort_columns.append("_fight_order_sort")
            elif "event" in df.columns:
                sort_columns.append("event")
            sort_columns.append("_original_order")
            df = df.sort_values(sort_columns, kind="mergesort", na_position="last")
            df["elo_order_source"] = "event_date"
        else:
            logger.warning("Elo chronological order inferred from source order because event_date values are missing or invalid")
            df = df.iloc[::-1]
    else:
        logger.warning("Elo chronological order inferred from source order because event_date column is missing")
        df = df.iloc[::-1]

    df = df.drop(columns=[col for col in ("_event_date_sort", "_fight_order_sort") if col in df.columns])
    return df.reset_index(drop=True)


def _first_existing_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    for column in candidates:
        if column in df.columns:
            return column
    return None


def compute_elo_ratings(
    fights_df: pd.DataFrame,
    initial_elo=None,
    k_factor=None,
):
    initial = initial_elo or settings.ELO_INITIAL
    k = k_factor or settings.ELO_K_FACTOR
    ufcfights = prepare_fights_chronological(fights_df)
    elo_ratings = {}
    peak_elo_ratings = {}
    elo_by_search = {}

    for col in (
        "fighter_1_elo_start",
        "fighter_2_elo_start",
        "fighter_1_elo_end",
        "fighter_2_elo_end",
        "fighter_1_elo_change",
        "fighter_2_elo_change",
        "elo_expected_fighter_1",
        "elo_expected_fighter_2",
    ):
        ufcfights[col] = 0.0
    ufcfights["elo_result_type"] = "unknown"

    for index, row in ufcfights.iterrows():
        f1, f2 = row["fighter_1"], row["fighter_2"]
        elo_ratings.setdefault(f1, initial)
        elo_ratings.setdefault(f2, initial)
        s1, s2 = elo_ratings[f1], elo_ratings[f2]
        expected_f1 = expected_score(s1, s2)
        expected_f2 = expected_score(s2, s1)
        ufcfights.at[index, "fighter_1_elo_start"] = s1
        ufcfights.at[index, "fighter_2_elo_start"] = s2
        ufcfights.at[index, "elo_expected_fighter_1"] = round(expected_f1, 6)
        ufcfights.at[index, "elo_expected_fighter_2"] = round(expected_f2, 6)

        result = row["result"]
        outcome = _fight_outcome(row, f1, f2)
        if outcome == "fighter_1_win":
            n1, n2 = update_elo_win(s1, s2, k)
            result_type = "win"
        elif outcome == "fighter_2_win":
            n2, n1 = update_elo_win(s2, s1, k)
            result_type = "win"
        elif outcome == "draw":
            n1, n2 = update_elo_draw(s1, s2, k)
            result_type = "draw"
        else:
            n1, n2 = s1, s2
            result_type = "no_change"

        for fighter, new_elo in ((f1, n1), (f2, n2)):
            peak_elo_ratings[fighter] = max(
                peak_elo_ratings.get(fighter, initial), new_elo
            )

        ufcfights.at[index, "fighter_1_elo_end"] = n1
        ufcfights.at[index, "fighter_2_elo_end"] = n2
        ufcfights.at[index, "fighter_1_elo_change"] = round(n1 - s1, 2)
        ufcfights.at[index, "fighter_2_elo_change"] = round(n2 - s2, 2)
        ufcfights.at[index, "elo_result_type"] = result_type
        elo_ratings[f1], elo_ratings[f2] = n1, n2

    ufcfights = ufcfights.reset_index(drop=True)
    for fighter, elo in elo_ratings.items():
        elo_by_search[normalize_name(fighter)] = elo

    logger.info("Computed Elo for %s fighters", len(elo_ratings))
    return ufcfights, elo_ratings, peak_elo_ratings, elo_by_search


def _fight_outcome(row: pd.Series, fighter_1: str, fighter_2: str) -> str:
    """Return the Elo outcome using explicit winner fields when they match fighters.

    Historical CSV rows use result == "win" to mean fighter_1 beat fighter_2.
    If imported data includes an explicit winner name matching either fighter,
    that explicit result is safer and takes precedence.
    """
    winner = _first_non_empty_value(row, ("winner_name", "winner", "winning_fighter"))
    loser = _first_non_empty_value(row, ("loser_name", "loser", "losing_fighter"))
    f1_key = normalize_name(fighter_1)
    f2_key = normalize_name(fighter_2)
    winner_key = normalize_name(winner)
    loser_key = normalize_name(loser)
    if winner_key == f1_key or (loser_key == f2_key and bool(loser_key)):
        return "fighter_1_win"
    if winner_key == f2_key or (loser_key == f1_key and bool(loser_key)):
        return "fighter_2_win"

    result = str(row.get("result", "")).lower().strip().split("\n")[0]
    if result == "win":
        return "fighter_1_win"
    if result == "draw":
        return "draw"
    return "no_change"


def _first_non_empty_value(row: pd.Series, candidates: tuple[str, ...]):
    for column in candidates:
        if column in row.index and not pd.isna(row.get(column)) and str(row.get(column)).strip():
            return row.get(column)
    return None


def build_elo_fight_counts(fights_elo: pd.DataFrame) -> dict[str, int]:
    """Count completed Elo-tracked fights per normalized fighter name."""
    counts: dict[str, int] = {}
    if fights_elo is None or fights_elo.empty:
        return counts
    for _, row in fights_elo.iterrows():
        result = str(row.get("result", "")).lower().strip().split("\n")[0]
        if result not in {"win", "draw"}:
            continue
        for col in ("fighter_1", "fighter_2"):
            name = row.get(col)
            key = normalize_name(name)
            if key:
                counts[key] = counts.get(key, 0) + 1
    return counts


def get_fighter_elo(fighter_name, elo_by_search, default=None):
    default = default or settings.ELO_INITIAL
    return elo_by_search.get(normalize_name(fighter_name), default)


def export_elo_leaderboard(elo_ratings, path=None):
    from pathlib import Path

    path = Path(path or settings.ELO_LEADERBOARD_CSV)
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = sorted(elo_ratings.items(), key=lambda x: x[1], reverse=True)
    pd.DataFrame(rows, columns=["Fighter", "Elo Rating"]).to_csv(path, index=False)
    logger.info("Exported Elo leaderboard to %s", path)
