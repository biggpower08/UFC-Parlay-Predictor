from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.data.scrapers.ufcstats import UFCStatsClient


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit-events", type=int, default=1)
    parser.add_argument("--force-refresh", action="store_true")
    args = parser.parse_args()
    client = UFCStatsClient(force_refresh=args.force_refresh)
    events = client.fetch_completed_events(limit=args.limit_events)
    fights = []
    for event in events:
        event_fights = client.fetch_event_fights(event)
        fights.extend(event_fights)
        print(f"{event.name}: {len(event_fights)} fights")
    print(f"total fights: {len(fights)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
