from pathlib import Path

import pandas as pd

from ufc_predictor.data.scrapers.ufcstats import (
    ScrapedEvent,
    parse_completed_events,
    parse_event_fights,
    parse_fighter_profile,
)
from ufc_predictor.rankings.generator import build_weight_class_history


FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_completed_events_fixture():
    events = parse_completed_events((FIXTURES / "ufcstats_events.html").read_text(encoding="utf-8"))

    assert len(events) == 1
    assert events[0].name == "UFC Test: Alpha vs Beta"
    assert events[0].event_date == "2026-05-10"
    assert events[0].location == "Las Vegas, Nevada, USA"


def test_parse_event_fights_fixture():
    event = ScrapedEvent(
        name="UFC Test: Alpha vs Beta",
        url="http://ufcstats.com/event-details/sample-event",
        event_date="2026-05-10",
    )
    fights = parse_event_fights((FIXTURES / "ufcstats_event.html").read_text(encoding="utf-8"), event)

    assert len(fights) == 2
    assert fights[0].fighter_1 == "Alpha Fighter"
    assert fights[0].fighter_2 == "Beta Fighter"
    assert fights[0].result == "win"
    assert fights[0].weight_class == "Lightweight"
    assert fights[1].result == "draw"


def test_parse_fighter_profile_fixture():
    profile = parse_fighter_profile((FIXTURES / "ufcstats_fighter.html").read_text(encoding="utf-8"))

    assert profile.name == "Alpha Fighter"
    assert profile.nickname == "The Example"
    assert profile.stance == "Orthodox"
    assert profile.date_of_birth == "1990-01-01"


def test_weight_class_history_from_scraped_fights():
    event = ScrapedEvent(
        name="UFC Test: Alpha vs Beta",
        url="http://ufcstats.com/event-details/sample-event",
        event_date="2026-05-10",
    )
    fights = parse_event_fights((FIXTURES / "ufcstats_event.html").read_text(encoding="utf-8"), event)
    rows = build_weight_class_history(pd.DataFrame([fight.__dict__ for fight in fights]))

    alpha = next(row for row in rows if row["normalized_name"] == "alpha fighter")
    assert alpha["weight_class"] == "Lightweight"
    assert alpha["fights_count"] == 1
