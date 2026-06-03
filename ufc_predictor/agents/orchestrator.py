"""Data orchestration: local DB first, web fill-in when needed."""

from ufc_predictor.agents.web_agent import fetch_and_normalize_fighter
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.db import repository
from ufc_predictor.config import settings
from ufc_predictor.models.elo.elo_engine import build_elo_fight_counts, compute_elo_ratings, export_elo_leaderboard
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


class FighterResolutionError(LookupError):
    def __init__(self, payload: dict):
        self.payload = payload
        super().__init__(payload.get("message", "Fighter could not be resolved"))


def ensure_database(force_import: bool = False) -> None:
    repository.initialize_database(force_import=force_import)


def resolve_fighter(name: str, allow_scrape: bool = True, confirmed: bool = False):
    ensure_database()
    resolution = repository.resolve_name(name)
    if resolution["status"] == "resolved" or (confirmed and resolution.get("resolved_name")):
        row = repository.get_fighter_by_name(resolution["resolved_name"])
        if row is not None:
            return row

    row = repository.get_fighter_by_name(name)
    if row is not None:
        return row
    if resolution["status"] == "needs_confirmation":
        raise FighterResolutionError(resolution)
    if resolution["status"] == "needs_full_name" and len(name.split()) < 2:
        raise FighterResolutionError(resolution)
    if not allow_scrape:
        raise LookupError(f"Fighter not found: {name}")

    logger.info("Fighter %s missing locally; attempting web fill-in", name)
    record = fetch_and_normalize_fighter(name)
    if normalize_name(record["name"]) != normalize_name(name):
        record["name"] = name
        record["normalized_name"] = normalize_name(name)
        record["_search_name"] = record["normalized_name"]
    return repository.upsert_fighter(record)


def refresh_all(force_refresh: bool = False) -> dict:
    ensure_database()
    fights = load_fights(force_refresh=force_refresh)
    fights_elo, elo_ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
    fight_counts = build_elo_fight_counts(fights_elo)
    repository.update_elo_columns(
        elo_by_search,
        peak_elo,
        elo_version=settings.ELO_ENGINE_VERSION,
        fight_counts=fight_counts,
    )
    history_rows = repository.replace_elo_history(
        elo_ratings,
        peak_elo,
        elo_version=settings.ELO_ENGINE_VERSION,
    )
    fight_history_rows = repository.replace_elo_fight_history(
        fights_elo,
        elo_version=settings.ELO_ENGINE_VERSION,
    )
    export_elo_leaderboard(elo_ratings)
    return {
        "fighters": len(repository.get_fighters_df()),
        "fights": len(fights),
        "elo_fighters": len(elo_ratings),
        "elo_history_rows": history_rows,
        "elo_fight_history_rows": fight_history_rows,
    }
