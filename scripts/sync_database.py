from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.agents.orchestrator import refresh_all
from ufc_predictor.data.scrapers.ufcstats import UFCStatsClient
from ufc_predictor.data.sync import record_sync_run, upsert_events, upsert_fighters_from_fights, upsert_fights
from ufc_predictor.rankings.generator import generate_rankings


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit-events", type=int, default=1)
    parser.add_argument("--skip-fighters", action="store_true")
    parser.add_argument("--skip-elo", action="store_true")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--source", default="ufcstats", choices=["ufcstats"])
    args = parser.parse_args()

    counts = {"events": 0, "fights": 0, "fighters": 0}
    try:
        client = UFCStatsClient(force_refresh=args.force_refresh)
        events = client.fetch_completed_events(limit=args.limit_events)
        fights = []
        for event in events:
            fights.extend(client.fetch_event_fights(event))

        counts["events"] = upsert_events(events, dry_run=args.dry_run)
        counts["fights"] = upsert_fights(fights, dry_run=args.dry_run)
        if not args.skip_fighters:
            counts["fighters"] = upsert_fighters_from_fights(fights, dry_run=args.dry_run)

        if not args.dry_run and not args.skip_elo:
            refresh_all(force_refresh=False)
            generate_rankings()

        record_sync_run(args.source, "success", args.dry_run, counts)
    except Exception as exc:
        record_sync_run(args.source, "failed", args.dry_run, counts, str(exc))
        raise

    print("Sync complete:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    if args.dry_run:
        print("  dry_run: true")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
