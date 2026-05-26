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
    return str(result).lower().strip().split("\n")[0]


def prepare_fights_chronological(fights_df: pd.DataFrame) -> pd.DataFrame:
    df = fights_df.copy()
    if "event" not in df.columns:
        df = df.reset_index()
    df = df.iloc[::-1].reset_index(drop=True)
    df["result"] = df["result"].apply(_normalize_result)
    return df


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
    ):
        ufcfights[col] = 0.0

    for index, row in ufcfights.iterrows():
        f1, f2 = row["fighter_1"], row["fighter_2"]
        elo_ratings.setdefault(f1, initial)
        elo_ratings.setdefault(f2, initial)
        s1, s2 = elo_ratings[f1], elo_ratings[f2]
        ufcfights.at[index, "fighter_1_elo_start"] = s1
        ufcfights.at[index, "fighter_2_elo_start"] = s2

        result = row["result"]
        if result == "win":
            n1, n2 = update_elo_win(s1, s2, k)
        elif result == "draw":
            n1, n2 = update_elo_draw(s1, s2, k)
        else:
            n1, n2 = s1, s2

        for fighter, new_elo in ((f1, n1), (f2, n2)):
            peak_elo_ratings[fighter] = max(
                peak_elo_ratings.get(fighter, initial), new_elo
            )

        ufcfights.at[index, "fighter_1_elo_end"] = n1
        ufcfights.at[index, "fighter_2_elo_end"] = n2
        elo_ratings[f1], elo_ratings[f2] = n1, n2

    for fighter, elo in elo_ratings.items():
        elo_by_search[normalize_name(fighter)] = elo

    logger.info("Computed Elo for %s fighters", len(elo_ratings))
    return ufcfights, elo_ratings, peak_elo_ratings, elo_by_search


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
