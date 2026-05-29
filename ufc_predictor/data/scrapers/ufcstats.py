"""Original UFCStats scraper and parser.

The parser functions are pure and unit-testable with saved HTML fixtures. The
client adds polite timeouts, retries, user-agent headers, and optional file cache
so sync jobs do not hammer UFCStats during repeated local tests.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from ufc_predictor.config import settings
from ufc_predictor.data.fetchers.errors import ParseError
from ufc_predictor.utils.helpers import normalize_name

BASE_URL = "http://ufcstats.com"
COMPLETED_EVENTS_URL = f"{BASE_URL}/statistics/events/completed?page=all"
UPCOMING_EVENTS_URL = f"{BASE_URL}/statistics/events/upcoming"
FIGHTERS_URL = f"{BASE_URL}/statistics/fighters?char=a&page=all"
KNOWN_FIGHTER_PROFILE_URL = f"{BASE_URL}/fighter-details/07f72a2a7591b409"
USER_AGENT = settings.SCRAPER_USER_AGENT


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


@dataclass(frozen=True)
class ScrapedFighterListing:
    first_name: str
    last_name: str
    nickname: str | None = None
    height: str | None = None
    weight: str | None = None
    reach: str | None = None
    stance: str | None = None
    record: str | None = None
    url: str | None = None

    @property
    def name(self) -> str:
        return _clean_text(f"{self.first_name} {self.last_name}")


class UFCStatsClient:
    def __init__(
        self,
        fetcher=None,
        fetcher_name: str | None = None,
        cache_only: bool = False,
        force_refresh: bool = False,
    ) -> None:
        self.fetcher = fetcher or build_fetcher(fetcher_name or settings.SCRAPER_FETCHER, cache_only=cache_only, force_refresh=force_refresh)

    def fetch(self, url: str) -> str:
        return self.fetcher.fetch(url).text

    def fetch_completed_events(self, limit: int | None = None) -> list[ScrapedEvent]:
        events = parse_completed_events(self.fetch(COMPLETED_EVENTS_URL))
        return events[:limit] if limit else events

    def fetch_upcoming_events(self, limit: int | None = None) -> list[ScrapedEvent]:
        events = parse_completed_events(self.fetch(UPCOMING_EVENTS_URL))
        return events[:limit] if limit else events

    def fetch_event_fights(self, event: ScrapedEvent) -> list[ScrapedFight]:
        return parse_event_fights(self.fetch(event.url), event)


def build_fetcher(name: str, cache_only: bool = False, force_refresh: bool = False):
    if name == "requests":
        from ufc_predictor.data.fetchers.requests_fetcher import RequestsFetcher

        return RequestsFetcher(cache_only=cache_only, force_refresh=force_refresh)
    if name == "playwright":
        from ufc_predictor.data.fetchers.playwright_fetcher import PlaywrightFetcher

        return PlaywrightFetcher(cache_only=cache_only, force_refresh=force_refresh)
    raise ValueError(f"Unknown fetcher: {name}")


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
    if not events:
        raise ParseError("No UFCStats events found in response")
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
    if not fights:
        raise ParseError(f"No fights found for event {event.name}")
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


def parse_fighter_listing(html: str) -> list[ScrapedFighterListing]:
    soup = BeautifulSoup(html, "html.parser")
    fighters: list[ScrapedFighterListing] = []
    for row in soup.select("tr.b-statistics__table-row"):
        cells = [_clean_text(cell.get_text(" ", strip=True)) for cell in row.select("td")]
        links = row.select("a[href*='/fighter-details/']")
        if len(cells) < 2 or not links:
            continue
        first_name = cells[0]
        last_name = cells[1] if len(cells) > 1 else ""
        if not first_name or first_name.lower() == "first":
            continue
        wins = cells[7] if len(cells) > 7 else None
        losses = cells[8] if len(cells) > 8 else None
        draws = cells[9] if len(cells) > 9 else None
        record = None
        if wins is not None and losses is not None and draws is not None:
            record = f"{wins}-{losses}-{draws}"
        fighters.append(
            ScrapedFighterListing(
                first_name=first_name,
                last_name=last_name,
                nickname=cells[2] if len(cells) > 2 else None,
                height=cells[3] if len(cells) > 3 else None,
                weight=cells[4] if len(cells) > 4 else None,
                reach=cells[5] if len(cells) > 5 else None,
                stance=cells[6] if len(cells) > 6 else None,
                record=record,
                url=links[0].get("href"),
            )
        )
    if not fighters:
        raise ParseError("No UFCStats fighters found in response")
    return fighters


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


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
