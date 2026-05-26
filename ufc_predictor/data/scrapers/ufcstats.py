"""Original UFCStats scraper and parser.

The parser functions are pure and unit-testable with saved HTML fixtures. The
client adds polite timeouts, retries, user-agent headers, and optional file cache
so sync jobs do not hammer UFCStats during repeated local tests.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import normalize_name
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)

BASE_URL = "http://ufcstats.com"
COMPLETED_EVENTS_URL = f"{BASE_URL}/statistics/events/completed?page=all"
USER_AGENT = "UFC-Predictor/2.0 (+https://github.com/biggpower08/UFC-Parlay-Predictor)"


@dataclass(frozen=True)
class ScrapedEvent:
    name: str
    url: str
    event_date: str | None = None
    location: str | None = None
    source: str = "ufcstats"

    @property
    def normalized_name(self) -> str:
        return normalize_name(self.name)

    @property
    def source_hash(self) -> str:
        return stable_hash([self.source, self.name, self.event_date or "", self.url])


@dataclass(frozen=True)
class ScrapedFight:
    event: str
    fighter_1: str
    fighter_2: str
    result: str
    method: str | None = None
    round: str | None = None
    time: str | None = None
    weight_class: str | None = None
    event_date: str | None = None
    source_url: str | None = None
    source: str = "ufcstats"

    @property
    def source_hash(self) -> str:
        return stable_hash(
            [
                self.source,
                self.event,
                self.fighter_1,
                self.fighter_2,
                self.result,
                self.method or "",
                self.round or "",
                self.time or "",
            ]
        )


@dataclass(frozen=True)
class ScrapedFighterProfile:
    name: str
    nickname: str | None = None
    height: str | None = None
    weight: str | None = None
    reach: str | None = None
    stance: str | None = None
    date_of_birth: str | None = None
    source_url: str | None = None

    @property
    def normalized_name(self) -> str:
        return normalize_name(self.name)


class UFCStatsClient:
    def __init__(
        self,
        timeout: float = 15.0,
        retries: int = 2,
        sleep_seconds: float = 0.75,
        cache_dir: Path | None = None,
        force_refresh: bool = False,
    ) -> None:
        self.timeout = timeout
        self.retries = retries
        self.sleep_seconds = sleep_seconds
        self.cache_dir = cache_dir or settings.SCRAPE_CACHE_DIR / "http" / "ufcstats"
        self.force_refresh = force_refresh
        self.headers = {"User-Agent": USER_AGENT}

    def fetch(self, url: str) -> str:
        cache_path = self._cache_path(url)
        if cache_path.is_file() and not self.force_refresh:
            text = cache_path.read_text(encoding="utf-8")
            if not _looks_like_browser_challenge(text):
                return text

        last_error: Exception | None = None
        for attempt in range(1, self.retries + 2):
            try:
                with httpx.Client(timeout=self.timeout, headers=self.headers, follow_redirects=True) as client:
                    response = client.get(url)
                    response.raise_for_status()
                text = response.text
                if _looks_like_browser_challenge(text):
                    raise RuntimeError("UFCStats returned a browser JavaScript challenge instead of scrapeable HTML")
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                cache_path.write_text(text, encoding="utf-8")
                time.sleep(self.sleep_seconds)
                return text
            except Exception as exc:  # pragma: no cover - network failures vary
                last_error = exc
                logger.warning("UFCStats fetch failed url=%s attempt=%s error=%s", url, attempt, exc)
                time.sleep(min(5.0, self.sleep_seconds * attempt))
        raise RuntimeError(f"Could not fetch UFCStats page {url}: {last_error}")

    def fetch_completed_events(self, limit: int | None = None) -> list[ScrapedEvent]:
        events = parse_completed_events(self.fetch(COMPLETED_EVENTS_URL))
        return events[:limit] if limit else events

    def fetch_event_fights(self, event: ScrapedEvent) -> list[ScrapedFight]:
        return parse_event_fights(self.fetch(event.url), event)

    def _cache_path(self, url: str) -> Path:
        parsed = urlparse(url)
        slug = hashlib.sha256(url.encode("utf-8")).hexdigest()
        suffix = Path(parsed.path).name or "index"
        return self.cache_dir / f"{suffix}-{slug}.html"


def parse_completed_events(html: str) -> list[ScrapedEvent]:
    soup = BeautifulSoup(html, "html.parser")
    events: list[ScrapedEvent] = []
    for row in soup.select("tr.b-statistics__table-row"):
        link = row.select_one("a[href*='/event-details/']")
        if not link:
            continue
        cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in row.select("td")]
        date_text = cells[0] if cells else None
        location = cells[1] if len(cells) > 1 else None
        events.append(
            ScrapedEvent(
                name=_clean_text(link.get_text(" ", strip=True)),
                url=link.get("href", "").strip(),
                event_date=_parse_date(date_text),
                location=location,
            )
        )
    if events:
        return events

    # Fallback for older/simple UFCStats markup.
    for link in soup.select("a.b-link.b-link_style_black[href*='/event-details/']"):
        events.append(ScrapedEvent(name=_clean_text(link.get_text(" ", strip=True)), url=link["href"].strip()))
    return events


def parse_event_fights(html: str, event: ScrapedEvent) -> list[ScrapedFight]:
    soup = BeautifulSoup(html, "html.parser")
    fights: list[ScrapedFight] = []
    for row in soup.select("tr.b-fight-details__table-row, tbody tr"):
        fighter_links = row.select("a[href*='/fighter-details/']")
        fighter_names = [_clean_text(link.get_text(" ", strip=True)) for link in fighter_links if link.get_text(strip=True)]
        if len(fighter_names) < 2:
            cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in row.select("td")]
            fighter_names = _extract_fighter_names_from_cells(cells)
        if len(fighter_names) < 2:
            continue

        cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in row.select("td")]
        result = _normalize_result(cells[0] if cells else "")
        method = cells[7] if len(cells) > 7 else None
        round_value = cells[8] if len(cells) > 8 else None
        time_value = cells[9] if len(cells) > 9 else None
        weight_class = cells[6] if len(cells) > 6 else None
        fights.append(
            ScrapedFight(
                event=event.name,
                fighter_1=fighter_names[0],
                fighter_2=fighter_names[1],
                result=result,
                method=method,
                round=round_value,
                time=time_value,
                weight_class=weight_class,
                event_date=event.event_date,
                source_url=row.get("data-link") or event.url,
            )
        )
    return fights


def parse_fighter_profile(html: str, source_url: str | None = None) -> ScrapedFighterProfile | None:
    soup = BeautifulSoup(html, "html.parser")
    name_el = soup.select_one(".b-content__title-highlight")
    if not name_el:
        return None
    details = {}
    for item in soup.select(".b-list__box-list-item"):
        text = _clean_text(item.get_text(" ", strip=True))
        if ":" not in text:
            continue
        key, value = [part.strip() for part in text.split(":", 1)]
        details[key.lower()] = value or None
    nickname_el = soup.select_one(".b-content__Nickname")
    return ScrapedFighterProfile(
        name=_clean_text(name_el.get_text(" ", strip=True)),
        nickname=_clean_text(nickname_el.get_text(" ", strip=True)) if nickname_el else None,
        height=details.get("height"),
        weight=details.get("weight"),
        reach=details.get("reach"),
        stance=details.get("stance"),
        date_of_birth=_parse_date(details.get("dob")),
        source_url=source_url,
    )


def stable_hash(parts: list[str]) -> str:
    normalized = "|".join(str(part or "").strip().lower() for part in parts)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _extract_fighter_names_from_cells(cells: list[str]) -> list[str]:
    if len(cells) < 2:
        return []
    parts = [part.strip() for part in cells[1].split("  ") if part.strip()]
    if len(parts) >= 2:
        return parts[:2]
    lines = [part.strip() for part in cells[1].splitlines() if part.strip()]
    return lines[:2]


def _normalize_result(result: str) -> str:
    value = _clean_text(result).lower()
    if value.startswith("w"):
        return "win"
    if "draw" in value:
        return "draw"
    if "nc" in value or "no contest" in value:
        return "nc"
    return value or "unknown"


def _parse_date(value: str | None) -> str | None:
    if not value:
        return None
    value = _clean_text(value)
    for fmt in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).date().isoformat()
        except ValueError:
            continue
    return value


def _clean_text(value: str | None) -> str:
    return " ".join(str(value or "").replace("\xa0", " ").split())


def _looks_like_browser_challenge(html: str) -> bool:
    text = html.lower()
    return "checking your browser" in text or "requires javascript" in text


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
