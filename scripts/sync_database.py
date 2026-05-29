from __future__ import annotations

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.data.fetchers.errors import (
    FetchError,
    RateLimitError,
    SourceBlockedError,
    SourceUnavailableError,
)
from ufc_predictor.config import settings
from ufc_predictor.data.sync import (
    get_sync_status,
    record_sync_run,
    sync_lock,
    update_source_health,
    upsert_events,
    upsert_fighters_from_fights,
    upsert_fights,
)
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)
BASE_URL = "http://ufcstats.com"
COMPLETED_EVENTS_URL = f"{BASE_URL}/statistics/events/completed?page=all"


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely sync UFCStats data into the app database.")
    parser.add_argument("--dry-run", action="store_true", help="Parse and count records without writing app data.")
    parser.add_argument("--historical", action="store_true", help="Allow a full historical sync. Use with care.")
    parser.add_argument("--recent-days", type=int, default=30, help="For normal syncs, only keep events this recent.")
    parser.add_argument("--limit-events", type=int, default=None, help="Hard cap the number of events fetched/processed.")
    parser.add_argument("--event-url", action="append", default=[], help="Sync a specific UFCStats event URL.")
    parser.add_argument("--event-html", action="append", default=[], help="Parse a manually saved UFCStats event HTML file.")
    parser.add_argument("--fighter-url", action="append", default=[], help="Reserved for targeted fighter profile sync.")
    parser.add_argument("--skip-fighters", action="store_true")
    parser.add_argument("--skip-elo", action="store_true")
    parser.add_argument("--skip-rankings", action="store_true")
    parser.add_argument("--force-refresh", action="store_true")
    parser.add_argument("--cache-only", action="store_true")
    parser.add_argument("--fetcher", default="requests", choices=["requests", "playwright"])
    parser.add_argument("--source", default="ufcstats", choices=["ufcstats"])
    parser.add_argument("--source-health", action="store_true", help="Check source health and exit.")
    parser.add_argument("--status", action="store_true", help="Show latest sync/source status and exit.")
    args = parser.parse_args()

    if args.status:
        print(json.dumps(get_sync_status(args.source), indent=2, default=str))
        return 0

    if args.source_health:
        return check_source_health(args)

    if args.fighter_url:
        print("Targeted fighter profile sync is intentionally not enabled yet.")
        print("Use fight result sync first; profile enrichment should stay limited and manually reviewed.")

    counts = {"events": 0, "fights": 0, "fighters": 0, "rankings": 0, "inserted": 0, "updated": 0, "skipped": 0, "failed": 0}
    status = "succeeded"
    message = ""

    try:
        with sync_lock(dry_run=args.dry_run):
            client = UFCStatsClient(
                fetcher_name=args.fetcher,
                cache_only=args.cache_only,
                force_refresh=args.force_refresh,
            )
            events = _load_events(client, args)
            fights = _load_fights(client, events, args)
            if getattr(args, "_partial_failure", False):
                status = "partial"
                counts["failed"] += int(getattr(args, "_failed_count", 0))
                message = str(getattr(args, "_failure_message", ""))

            counts["events"] = upsert_events(events, dry_run=args.dry_run)
            counts["fights"] = upsert_fights(fights, dry_run=args.dry_run)
            if not args.skip_fighters:
                counts["fighters"] = upsert_fighters_from_fights(fights, dry_run=args.dry_run)
            counts["inserted"] = counts["events"] + counts["fights"] + counts["fighters"]
            counts["skipped"] = max(0, len(events) - counts["events"])

            if not args.dry_run and fights:
                if not args.skip_elo:
                    from ufc_predictor.agents.orchestrator import refresh_all

                    refresh_all(force_refresh=False)
                if not args.skip_rankings:
                    from ufc_predictor.rankings.generator import generate_rankings

                    ranking_result = generate_rankings()
                    counts["rankings"] = int(ranking_result.get("rankings", 0))
            logger.info(
                "sync counts source=%s status=%s events=%s fights=%s fighters=%s inserted=%s skipped=%s failed=%s",
                args.source,
                status,
                counts["events"],
                counts["fights"],
                counts["fighters"],
                counts["inserted"],
                counts["skipped"],
                counts["failed"],
            )

        if not args.dry_run:
            update_source_health(args.source, BASE_URL, "healthy")
            record_sync_run(args.source, status, False, counts, message)
    except SourceBlockedError as exc:
        status = "failed"
        message = str(exc)
        if not args.dry_run:
            update_source_health(args.source, BASE_URL, status, message, challenged=True)
            record_sync_run(args.source, status, False, counts, message)
        print(f"Sync blocked safely: {message}")
        return 2
    except RateLimitError as exc:
        status = "failed"
        message = str(exc)
        if not args.dry_run:
            update_source_health(args.source, BASE_URL, status, message)
            record_sync_run(args.source, status, False, counts, message)
        print(f"Sync rate-limited safely: {message}")
        return 3
    except Exception as exc:
        status = "failed"
        message = str(exc)
        if not args.dry_run:
            update_source_health(args.source, BASE_URL, status, message)
            record_sync_run(args.source, status, False, counts, message)
        raise

    print("Sync complete:")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"  status: {status}")
    if args.dry_run:
        print("  dry_run: true")
        print("  database_writes: false")
    if message:
        print(f"  message: {message[:500]}")
    return 0


def check_source_health(args) -> int:
    counts = {"events": 0, "fights": 0, "fighters": 0, "rankings": 0, "inserted": 0, "updated": 0, "skipped": 0, "failed": 0}
    try:
        UFCStatsClient, _parse_event_fights, _scraped_event = _ufcstats_imports()
        client = UFCStatsClient(
            fetcher_name=args.fetcher,
            cache_only=args.cache_only,
            force_refresh=args.force_refresh,
        )
        html = client.fetch(COMPLETED_EVENTS_URL)
        status = "healthy" if "event-details" in html else "unavailable"
        message = "" if status == "healthy" else "Events page did not contain event links"
        update_source_health(args.source, BASE_URL, status, message)
        record_sync_run(args.source, f"source_health_{status}", True, counts, message)
        print(json.dumps(_source_health_payload(args.source, "healthy" if status == "healthy" else "unreliable"), indent=2, default=str))
        return 0 if status == "healthy" else 1
    except SourceBlockedError as exc:
        message = str(exc)
        update_source_health(args.source, BASE_URL, "failed", message, challenged=True)
        record_sync_run(args.source, "source_health_challenged", True, counts, message)
        print(json.dumps(_source_health_payload(args.source, "blocked"), indent=2, default=str))
        return 2
    except (RateLimitError, SourceUnavailableError, FetchError) as exc:
        message = str(exc)
        update_source_health(args.source, BASE_URL, "failed", message)
        record_sync_run(args.source, "source_health_failed", True, counts, message)
        print(json.dumps(_source_health_payload(args.source, "unreliable"), indent=2, default=str))
        return 1
    except ImportError as exc:
        message = _dependency_message(args.fetcher, exc)
        update_source_health(args.source, BASE_URL, "failed", message)
        record_sync_run(args.source, "source_health_failed", True, counts, message)
        print(json.dumps(_source_health_payload(args.source, "unreliable", message), indent=2, default=str))
        return 1


def _source_health_payload(source: str, ufcstats_live_status: str, live_message: str | None = None) -> dict:
    csv_exists = settings.FIGHTS_CSV.is_file()
    manual_html_available = True
    cached_html_available = _has_cached_html()
    structured_api_configured = bool(getattr(settings, "SPORTSDATAIO_API_KEY", "") or getattr(settings, "BALLDONTLIE_API_KEY", ""))
    return {
        "sources": {
            "ufcstats_live": {
                "status": ufcstats_live_status,
                "message": live_message or "Use only after source-health is healthy. Do not bypass challenge/block pages.",
            },
            "csv_import": {
                "status": "available" if csv_exists else "unavailable",
                "path": str(settings.FIGHTS_CSV),
                "message": "Primary current fallback for historical import and data audits.",
            },
            "manual_html_import": {
                "status": "available" if manual_html_available else "unavailable",
                "command": "scripts\\sync_database.py --dry-run --event-html <saved_ufcstats_event.html>",
            },
            "cached_html": {
                "status": "available" if cached_html_available else "unavailable",
                "path": str(settings.SCRAPER_CACHE_DIR),
            },
            "structured_api": {
                "status": "configured" if structured_api_configured else "not_configured",
                "providers": ["future_sportsdataio", "future_balldontlie"],
            },
            "odds_source": {
                "status": "configured" if settings.ENABLE_ODDS else "not_configured",
                "provider": settings.ODDS_PROVIDER,
            },
        },
        "sync_status": get_sync_status(source),
    }


def _load_events(client: UFCStatsClient, args) -> list[ScrapedEvent]:
    UFCStatsClient, parse_event_fights, ScrapedEvent = _ufcstats_imports()
    if args.event_html:
        return [
            ScrapedEvent(
                name=Path(path).stem,
                url=str(Path(path).resolve()),
                source=args.source,
            )
            for path in args.event_html
        ]
    if args.event_url:
        return [
            ScrapedEvent(
                name=f"Manual UFCStats event {index + 1}",
                url=url,
                source=args.source,
            )
            for index, url in enumerate(args.event_url)
        ]

    events = client.fetch_completed_events(limit=args.limit_events)
    if args.historical:
        return events

    recent = _filter_recent(events, args.recent_days)
    if recent:
        return recent[: args.limit_events] if args.limit_events else recent
    # If UFCStats dates are missing or unparsable, keep the normal sync bounded.
    safe_limit = args.limit_events or 5
    return events[:safe_limit]


def _load_fights(client: UFCStatsClient, events: list[ScrapedEvent], args) -> list:
    UFCStatsClient, parse_event_fights, ScrapedEvent = _ufcstats_imports()
    if args.event_html:
        fights = []
        for event in events:
            html_path = Path(event.url)
            try:
                event_fights = parse_event_fights(html_path.read_text(encoding="utf-8"), event)
                fights.extend(event_fights)
                logger.info("sync parsed manual_html=%s fights=%s", html_path, len(event_fights))
            except Exception as exc:
                args._partial_failure = True
                args._failed_count = int(getattr(args, "_failed_count", 0)) + 1
                args._failure_message = f"{getattr(args, '_failure_message', '')} Manual HTML failed: {html_path}: {exc}".strip()
                logger.warning("sync manual_html_failed path=%s error=%s", html_path, exc)
        return fights

    fights = []
    for event in events:
        try:
            event_fights = client.fetch_event_fights(event)
            fights.extend(event_fights)
            logger.info("sync parsed event=%s fights=%s", event.name, len(event_fights))
        except FetchError as exc:
            args._partial_failure = True
            args._failed_count = int(getattr(args, "_failed_count", 0)) + 1
            args._failure_message = f"{getattr(args, '_failure_message', '')} Event failed: {event.name}: {exc}".strip()
            logger.warning("sync event_failed event=%s error=%s", event.name, exc)
    return fights


def _ufcstats_imports():
    from ufc_predictor.data.scrapers.ufcstats import ScrapedEvent, UFCStatsClient, parse_event_fights

    return UFCStatsClient, parse_event_fights, ScrapedEvent


def _dependency_message(fetcher: str, exc: ImportError) -> str:
    base = f"Missing dependency for source-health check: {exc}"
    if fetcher == "playwright":
        return (
            f"{base}. Install optional Playwright support with: "
            "& $env:MMA_AI_PYTHON -m pip install playwright; "
            "& $env:MMA_AI_PYTHON -m playwright install chromium"
        )
    return base


def _has_cached_html() -> bool:
    cache_dir = settings.SCRAPER_CACHE_DIR
    return cache_dir.is_dir() and any(cache_dir.rglob("*"))


def _filter_recent(events: list[ScrapedEvent], recent_days: int) -> list[ScrapedEvent]:
    cutoff = date.today() - timedelta(days=max(1, recent_days))
    recent = []
    for event in events:
        if not event.event_date:
            continue
        try:
            if date.fromisoformat(event.event_date) >= cutoff:
                recent.append(event)
        except ValueError:
            continue
    return recent


if __name__ == "__main__":
    raise SystemExit(main())
