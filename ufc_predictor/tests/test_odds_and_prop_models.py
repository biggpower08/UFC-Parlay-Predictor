from ufc_predictor.config import settings
from ufc_predictor.models.props import prop_model_status
from ufc_predictor.odds import get_odds_events, get_odds_status
import json
from pathlib import Path


def test_odds_status_disabled_by_default():
    original_enabled = settings.ENABLE_ODDS
    original_provider = settings.ODDS_PROVIDER
    settings.ENABLE_ODDS = False
    settings.ODDS_PROVIDER = "none"
    try:
        status = get_odds_status()
    finally:
        settings.ENABLE_ODDS = original_enabled
        settings.ODDS_PROVIDER = original_provider

    assert status["odds_enabled"] is False
    assert status["provider"] == "none"
    assert status["message"] == "Live odds provider is not configured."


def test_odds_events_empty_when_provider_disabled():
    events = get_odds_events()

    assert events["status"]["odds_enabled"] is False
    assert events["events"] == []


def test_prop_model_registry_reports_current_training_status():
    statuses = prop_model_status()

    assert statuses
    assert statuses["winner_model"]["status"] in {"not_trained", "blocked", "trained", "experimental", "production_ready"}
    for model_name in ("finish_model", "goes_distance_model", "method_model", "round_model"):
        assert statuses[model_name]["status"] in {"not_trained", "trained", "experimental", "production_ready"}
        assert statuses[model_name]["support_level"] in {"not_available", "model_supported"}
    for model_name in ("strike_volume_model", "takedown_control_model"):
        assert statuses[model_name]["status"] in {"not_trained", "insufficient_data", "experimental", "trained", "production_ready"}
        assert statuses[model_name]["support_level"] in {"not_available", "model_supported"}
    assert statuses["odds_calibration_model"]["status"] in {"not_trained", "blocked", "insufficient_data"}
    for model_name in ("odds_calibration_model",):
        assert statuses[model_name]["support_level"] == "not_available"


def test_odds_registry_stays_blocked_after_timestamp_audit():
    path = Path("ufc_predictor/data/processed/model_registry.json")
    if not path.is_file():
        return
    registry = json.loads(path.read_text(encoding="utf-8"))
    odds = registry.get("odds_calibration_model", {})

    assert odds.get("production_status") == "blocked"
    assert odds.get("odds_timestamp_audit_status") in {
        "blocked_missing_snapshot_timestamps",
        "blocked_no_files",
        "blocked_post_event_snapshots",
        "research_only_timezone_ambiguous",
        None,
    }
