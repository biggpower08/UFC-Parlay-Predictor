from pathlib import Path

import pytest

from ufc_predictor.data.fetchers.errors import SourceBlockedError
from ufc_predictor.data.fetchers.requests_fetcher import RequestsFetcher, looks_like_browser_challenge
from ufc_predictor.data.scrapers.diagnostics import (
    analyze_html,
    classify_source_health,
    diagnose_manual_html,
    expected_markers,
)
from ufc_predictor.data.scrapers.ufcstats import parse_completed_events, parse_fighter_listing


FIXTURES = Path(__file__).parent / "fixtures"


def test_expected_marker_detection():
    html = (FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8")

    assert "b-link b-link_style_black" in expected_markers(html)


def test_200_challenge_page_is_classified_blocked():
    html = "<html><title>Checking your browser</title><body>Cloudflare challenge captcha</body></html>"
    diagnostic = analyze_html("completed_events", "http://example.test", html, "requests")

    assert looks_like_browser_challenge(html)
    assert diagnostic.source_health_status == "blocked"
    assert diagnostic.challenge_markers


def test_completed_events_fixture_parses_and_is_healthy():
    html = (FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8")
    events = parse_completed_events(html)
    diagnostic = analyze_html("completed_events", "fixture", html, "manual_html")

    assert len(events) == 1
    assert diagnostic.events_parsed == 1
    assert diagnostic.source_health_status == "healthy"


def test_upcoming_events_fixture_uses_same_event_parser():
    html = (FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8")
    diagnostic = analyze_html("upcoming_events", "fixture", html, "manual_html")

    assert diagnostic.events_parsed == 1
    assert diagnostic.source_health_status == "healthy"


def test_fighters_fixture_parses():
    html = (FIXTURES / "ufcstats_fighters.html").read_text(encoding="utf-8")
    fighters = parse_fighter_listing(html)
    diagnostic = analyze_html("fighters", "fixture", html, "manual_html")

    assert fighters[0].first_name == "Alpha"
    assert fighters[0].record == "10-1-0"
    assert diagnostic.fighters_parsed == 1
    assert diagnostic.source_health_status == "healthy"


def test_event_detail_fixture_parses_fights():
    html = (FIXTURES / "ufcstats_event.html").read_text(encoding="utf-8")
    diagnostic = analyze_html("event_detail", "fixture", html, "manual_html")

    assert diagnostic.fights_parsed == 2
    assert diagnostic.source_health_status in {"healthy", "partially_usable"}


def test_fighter_profile_fixture_parses():
    html = (FIXTURES / "ufcstats_fighter.html").read_text(encoding="utf-8")
    diagnostic = analyze_html("fighter_profile", "fixture", html, "manual_html")

    assert diagnostic.fighter_profiles_parsed == 1
    assert diagnostic.source_health_status == "healthy"


def test_manual_html_diagnostic():
    result = diagnose_manual_html(FIXTURES / "ufcstats_events.html", "completed_events")

    assert result["source_health"] == "healthy"
    assert result["pages"][0]["events_parsed"] == 1


def test_source_health_classification():
    healthy = analyze_html("completed_events", "fixture", (FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8"), "manual_html")
    blocked = analyze_html("completed_events", "fixture", "Access denied captcha challenge", "manual_html")

    assert classify_source_health([healthy]) == "healthy"
    assert classify_source_health([healthy, blocked]) == "blocked"


def test_requests_fetcher_has_explicit_timeout(tmp_path):
    fetcher = RequestsFetcher(cache_dir=tmp_path, timeout=7.5, cache_only=True)

    assert fetcher.timeout == 7.5


def test_cache_only_mode_uses_cache(tmp_path):
    url = "http://example.test/statistics/events/completed"
    fetcher = RequestsFetcher(cache_dir=tmp_path, cache_only=True)
    fetcher.cache.write(url, (FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8"))

    result = fetcher.fetch(url)

    assert result.from_cache is True
    assert result.bytes_read > 0


def test_cache_only_challenge_is_blocked(tmp_path):
    url = "http://example.test/challenge"
    fetcher = RequestsFetcher(cache_dir=tmp_path, cache_only=True)
    fetcher.cache.write(url, "Checking your browser Cloudflare challenge")

    with pytest.raises(SourceBlockedError):
        fetcher.fetch(url)
