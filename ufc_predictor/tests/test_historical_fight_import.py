from pathlib import Path

from scripts.import_historical_fights import (
    build_event_rows,
    build_fighter_rows,
    import_historical_fights,
    normalize_result,
    prepare_fight_rows,
)


FIXTURES = Path(__file__).parent / "fixtures"


def test_prepare_historical_fights_dedupes_and_normalizes_rows():
    rows, stats = prepare_fight_rows(FIXTURES / "historical_fights_sample.csv")

    assert stats["source_rows"] == 4
    assert stats["duplicate_source_rows"] == 1
    assert stats["invalid_rows"] == 0
    assert len(rows) == 3
    assert rows[0]["result"] == "win"
    assert rows[1]["result"] == "draw"
    assert rows[2]["result"] == "nc"
    assert rows[0]["source_hash"]


def test_build_events_and_fighters_from_prepared_fights():
    fights, _stats = prepare_fight_rows(FIXTURES / "historical_fights_sample.csv")

    events = build_event_rows(fights)
    fighters = build_fighter_rows(fights)

    assert len(events) == 3
    assert len(fighters) == 6
    assert {event["normalized_name"] for event in events} == {"ufc test 1", "ufc test 2", "ufc test 3"}
    assert any(fighter["normalized_name"] == "alpha fighter" for fighter in fighters)


def test_dry_run_import_does_not_require_database_connection():
    summary = import_historical_fights(FIXTURES / "historical_fights_sample.csv", dry_run=True)

    assert summary.dry_run is True
    assert summary.prepared_rows == 3
    assert summary.fights_before is None
    assert summary.fights_after is None


def test_result_mapping():
    assert normalize_result("W/L") == "win"
    assert normalize_result("Draw") == "draw"
    assert normalize_result("No Contest") == "nc"
    assert normalize_result("") == "unknown"
