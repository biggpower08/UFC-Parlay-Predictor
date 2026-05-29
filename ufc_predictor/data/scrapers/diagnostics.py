"""UFCStats fetch and parser diagnostics.

Diagnostics separate network success from parser success and never classify a
challenge page as healthy.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

from ufc_predictor.config import settings
from ufc_predictor.data.fetchers.errors import FetchError, SourceBlockedError, SourceUnavailableError
from ufc_predictor.data.scrapers.ufcstats import (
    COMPLETED_EVENTS_URL,
    FIGHTERS_URL,
    KNOWN_FIGHTER_PROFILE_URL,
    UPCOMING_EVENTS_URL,
    ScrapedEvent,
    build_fetcher,
    parse_completed_events,
    parse_event_fights,
    parse_fighter_listing,
    parse_fighter_profile,
)

EXPECTED_MARKERS = (
    "Events & Fights",
    "Fighters",
    "b-statistics__table",
    "b-link b-link_style_black",
    "fighter-details",
    "event-details",
)
CHALLENGE_MARKERS = (
    "challenge",
    "captcha",
    "enable javascript",
    "requires javascript",
    "checking your browser",
    "access denied",
    "cloudflare",
    "cf-chl",
)


@dataclass
class PageDiagnostic:
    page_type: str
    url: str
    fetcher: str
    status_code: int | None = None
    final_url: str | None = None
    content_type: str | None = None
    bytes_read: int = 0
    title: str | None = None
    expected_markers: list[str] | None = None
    challenge_markers: list[str] | None = None
    body_preview: str = ""
    events_parsed: int = 0
    fights_parsed: int = 0
    fighters_parsed: int = 0
    fighter_profiles_parsed: int = 0
    cache_hit: bool = False
    cache_age_seconds: float | None = None
    elapsed_ms: float | None = None
    source_health_status: str = "not_checked"
    error: str | None = None
    debug_html_path: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT_PAGES = [
    ("completed_events", COMPLETED_EVENTS_URL),
    ("upcoming_events", UPCOMING_EVENTS_URL),
    ("fighters", FIGHTERS_URL),
    ("fighter_profile", KNOWN_FIGHTER_PROFILE_URL),
]


def diagnose_ufcstats(
    fetcher_name: str = "requests",
    cache_only: bool = False,
    save_debug_html: bool = False,
) -> dict:
    pages = [diagnose_url(page_type, url, fetcher_name, cache_only=cache_only, save_debug_html=save_debug_html) for page_type, url in DEFAULT_PAGES]
    return {
        "fetcher": fetcher_name,
        "source_health": classify_source_health(pages),
        "pages": [page.to_dict() for page in pages],
    }


def diagnose_manual_html(path: str | Path, page_type: str) -> dict:
    html_path = Path(path)
    html = html_path.read_text(encoding="utf-8")
    diagnostic = analyze_html(page_type, str(html_path), html, fetcher="manual_html")
    diagnostic.cache_hit = False
    return {
        "fetcher": "manual_html",
        "source_health": diagnostic.source_health_status,
        "pages": [diagnostic.to_dict()],
    }


def diagnose_url(
    page_type: str,
    url: str,
    fetcher_name: str,
    cache_only: bool = False,
    save_debug_html: bool = False,
) -> PageDiagnostic:
    try:
        fetcher = build_fetcher(fetcher_name, cache_only=cache_only)
        result = fetcher.fetch(url)
        diagnostic = analyze_html(page_type, url, result.text, fetcher=fetcher_name)
        diagnostic.status_code = result.status_code
        diagnostic.final_url = result.final_url or result.url
        diagnostic.content_type = result.content_type
        diagnostic.bytes_read = result.bytes_read
        diagnostic.cache_hit = result.from_cache
        diagnostic.cache_age_seconds = getattr(fetcher, "last_cache_age_seconds", None)
        diagnostic.elapsed_ms = result.elapsed_ms
        if save_debug_html:
            diagnostic.debug_html_path = str(_save_debug_html(page_type, result.text))
        return diagnostic
    except SourceBlockedError as exc:
        return PageDiagnostic(page_type, url, fetcher_name, source_health_status="blocked", error=str(exc))
    except SourceUnavailableError as exc:
        return PageDiagnostic(page_type, url, fetcher_name, source_health_status="failed", error=str(exc))
    except FetchError as exc:
        return PageDiagnostic(page_type, url, fetcher_name, source_health_status="failed", error=str(exc))
    except ImportError as exc:
        return PageDiagnostic(page_type, url, fetcher_name, source_health_status="failed", error=_dependency_message(fetcher_name, exc))
    except Exception as exc:
        return PageDiagnostic(page_type, url, fetcher_name, source_health_status="failed", error=str(exc))


def analyze_html(page_type: str, url: str, html: str, fetcher: str) -> PageDiagnostic:
    expected = expected_markers(html)
    challenges = challenge_markers(html)
    diagnostic = PageDiagnostic(
        page_type=page_type,
        url=url,
        fetcher=fetcher,
        bytes_read=len(html.encode("utf-8")),
        title=page_title(html),
        expected_markers=expected,
        challenge_markers=challenges,
        body_preview=sanitize_preview(html),
    )
    if challenges:
        diagnostic.source_health_status = "blocked"
        return diagnostic

    try:
        if page_type in {"completed_events", "upcoming_events"}:
            diagnostic.events_parsed = len(parse_completed_events(html))
        elif page_type == "event_detail":
            event = ScrapedEvent(name=Path(url).stem or "manual_event", url=url)
            diagnostic.fights_parsed = len(parse_event_fights(html, event))
        elif page_type == "fighters":
            diagnostic.fighters_parsed = len(parse_fighter_listing(html))
        elif page_type == "fighter_profile":
            diagnostic.fighter_profiles_parsed = 1 if parse_fighter_profile(html, url) else 0
        else:
            diagnostic.error = f"Unknown page type: {page_type}"
            diagnostic.source_health_status = "failed"
            return diagnostic
    except Exception as exc:
        diagnostic.error = str(exc)
        diagnostic.source_health_status = "failed"
        return diagnostic

    if _page_parse_succeeded(diagnostic):
        diagnostic.source_health_status = "healthy"
    else:
        diagnostic.source_health_status = "failed"
    return diagnostic


def classify_source_health(pages: list[PageDiagnostic]) -> str:
    statuses = [page.source_health_status for page in pages]
    if any(status == "blocked" for status in statuses):
        return "blocked"
    if all(status == "healthy" for status in statuses):
        return "healthy"
    if any(status in {"healthy", "partially_usable"} for status in statuses):
        return "partially_usable"
    if any(status == "failed" for status in statuses):
        return "failed"
    return "unreliable"


def _page_parse_succeeded(diagnostic: PageDiagnostic) -> bool:
    if diagnostic.page_type in {"completed_events", "upcoming_events"}:
        return diagnostic.events_parsed > 0
    if diagnostic.page_type == "event_detail":
        return diagnostic.fights_parsed > 0
    if diagnostic.page_type == "fighters":
        return diagnostic.fighters_parsed > 0
    if diagnostic.page_type == "fighter_profile":
        return diagnostic.fighter_profiles_parsed > 0
    return False


def expected_markers(html: str) -> list[str]:
    return [marker for marker in EXPECTED_MARKERS if marker.lower() in (html or "").lower()]


def challenge_markers(html: str) -> list[str]:
    return [marker for marker in CHALLENGE_MARKERS if marker in (html or "").lower()]


def page_title(html: str) -> str | None:
    soup = BeautifulSoup(html or "", "html.parser")
    title = soup.find("title")
    return " ".join(title.get_text(" ", strip=True).split()) if title else None


def sanitize_preview(html: str, limit: int = 300) -> str:
    text = BeautifulSoup(html or "", "html.parser").get_text(" ", strip=True)
    text = re.sub(r"\s+", " ", text)
    return text[:limit]


def _save_debug_html(page_type: str, html: str) -> Path:
    path = settings.DATA_PROCESSED_DIR / "scrape_debug" / f"{page_type}.html"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")
    return path


def _dependency_message(fetcher: str, exc: ImportError) -> str:
    if fetcher == "playwright":
        return (
            f"Playwright is unavailable: {exc}. Install with: "
            "& $env:MMA_AI_PYTHON -m pip install playwright; "
            "& $env:MMA_AI_PYTHON -m playwright install chromium"
        )
    return f"Fetcher dependency is unavailable: {exc}"
