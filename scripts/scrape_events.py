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
    parser.add_argument("--limit-events", type=int, default=None)
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--fetcher", default="requests", choices=["requests", "playwright"])
    args = parser.parse_args()
    try:
        events = UFCStatsClient(
            fetcher_name=args.fetcher,
            cache_only=args.cache_only,
            force_refresh=args.force_refresh,
        ).fetch_completed_events(limit=args.limit_events)
    except FetchError as exc:
        print(f"UFCStats event scrape failed safely: {exc}")
        return 1
    print(f"events: {len(events)}")
    for event in events[:10]:
        print(f"{event.event_date or 'unknown'} | {event.name} | {event.url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
