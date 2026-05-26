from __future__ import annotations

import argparse


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--fighter-url", action="append", default=[])
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--fetcher", default="requests", choices=["requests", "playwright"])
    parser.parse_args()
    print("Fighter profile scraping is parser-ready but not run as a bulk crawl yet.")
    print("Use fight result sync first; profile enrichment should be limited to selected fighter URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
