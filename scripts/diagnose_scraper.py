from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.data.scrapers.diagnostics import diagnose_manual_html, diagnose_ufcstats


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose UFCStats fetch and parser health.")
    parser.add_argument("--fetcher", choices=["requests", "playwright"], default="requests")
    parser.add_argument("--save-debug-html", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--manual-html", default="", help="Path to a manually saved UFCStats HTML page.")
    parser.add_argument(
        "--page-type",
        choices=["completed_events", "upcoming_events", "fighters", "event_detail", "fighter_profile"],
        default="completed_events",
    )
    args = parser.parse_args()

    if args.manual_html:
        result = diagnose_manual_html(args.manual_html, args.page_type)
    else:
        result = diagnose_ufcstats(
            fetcher_name=args.fetcher,
            cache_only=args.cache_only,
            save_debug_html=args.save_debug_html,
        )
    print(json.dumps(result, indent=2, default=str))
    return 0 if result["source_health"] in {"healthy", "partially_usable"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
