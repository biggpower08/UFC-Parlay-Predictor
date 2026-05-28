from ufc_predictor.config import settings
from ufc_predictor.models.props import prop_model_status
from ufc_predictor.odds import get_odds_events, get_odds_status


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


def test_prop_model_registry_returns_not_trained():
    statuses = prop_model_status()

    assert statuses
    for model in statuses.values():
        assert model["status"] == "not_trained"
        assert model["support_level"] == "not_available"
