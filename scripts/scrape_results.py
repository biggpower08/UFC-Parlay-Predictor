from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.data.fetchers.errors import FetchError
from ufc_predictor.data.scrapers.ufcstats import UFCStatsClient


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-events", type=int, default=1)
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--fetcher", default="requests", choices=["requests", "playwright"])
    args = parser.parse_args()
    client = UFCStatsClient(
        fetcher_name=args.fetcher,
        cache_only=args.cache_only,
        force_refresh=args.force_refresh,
    )
    try:
        events = client.fetch_completed_events(limit=args.limit_events)
    except FetchError as exc:
        print(f"UFCStats result scrape failed safely: {exc}")
        return 1
    fights = []
    for event in events:
        try:
            event_fights = client.fetch_event_fights(event)
        except FetchError as exc:
            print(f"{event.name}: failed safely: {exc}")
            continue
        fights.extend(event_fights)
        print(f"{event.name}: {len(event_fights)} fights")
    print(f"total fights: {len(fights)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
