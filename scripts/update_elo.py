"""Refresh fight history and recompute MMA Elo ratings.

Run manually:

    python scripts/update_elo.py

Cron/Task Scheduler can call the same command. The script is retry-safe and
deduplicates fight rows before recomputing ratings.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.db.repository import update_elo_columns
from ufc_predictor.models.elo.elo_engine import compute_elo_ratings, export_elo_leaderboard


LOG_PATH = settings.LOGS_DIR / "elo_update.log"


def configure_logging() -> None:
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=settings.LOG_FORMAT,
        handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
    )


def update_elo(force_refresh: bool = True) -> dict:
    logging.info("Elo update started force_refresh=%s", force_refresh)
    fights = load_fights(force_refresh=force_refresh)
    before = len(fights)
    dedupe_cols = [col for col in ["event", "fighter_1", "fighter_2", "result", "method", "round", "time"] if col in fights.columns]
    fights = fights.drop_duplicates(subset=dedupe_cols, keep="first") if dedupe_cols else fights.drop_duplicates()
    removed = before - len(fights)

    fights_elo, elo_ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
    update_elo_columns(elo_by_search, peak_elo)
    export_elo_leaderboard(elo_ratings)

    logging.info(
        "Elo update complete fights=%s duplicates_removed=%s rated_fighters=%s",
        len(fights_elo),
        removed,
        len(elo_ratings),
    )
    return {
        "fights": len(fights_elo),
        "duplicates_removed": removed,
        "rated_fighters": len(elo_ratings),
        "leaderboard": str(settings.ELO_LEADERBOARD_CSV),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-refresh", action="store_true", help="Use cached fights.csv instead of downloading.")
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    configure_logging()
    last_error = None
    for attempt in range(1, args.retries + 2):
        try:
            result = update_elo(force_refresh=not args.no_refresh)
            logging.info("Result: %s", result)
            return 0
        except Exception as exc:
            last_error = exc
            logging.exception("Elo update attempt %s failed", attempt)
            if attempt <= args.retries:
                time.sleep(min(30, attempt * 5))

    logging.error("Elo update failed permanently: %s", last_error)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
