"""Refresh fight history and recompute MMA Elo ratings.

Run manually:

    python scripts/update_elo.py --no-refresh

Cron/Task Scheduler can call the same command. The script is retry-safe and
deduplicates fight rows through the shared orchestrator before persisting Elo.
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

from ufc_predictor.agents.orchestrator import refresh_all
from ufc_predictor.config import settings


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
    result = refresh_all(force_refresh=force_refresh)
    logging.info("Elo update complete: %s", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-refresh", action="store_true", help="Use cached fights.csv instead of downloading.")
    parser.add_argument("--force-refresh", action="store_true", help="Download fresh fight data before Elo recompute.")
    parser.add_argument("--retries", type=int, default=2)
    args = parser.parse_args()

    configure_logging()
    force_refresh = args.force_refresh or not args.no_refresh
    last_error = None
    for attempt in range(1, args.retries + 2):
        try:
            result = update_elo(force_refresh=force_refresh)
            print("Elo update complete:")
            for key, value in result.items():
                print(f"  {key}: {value}")
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
