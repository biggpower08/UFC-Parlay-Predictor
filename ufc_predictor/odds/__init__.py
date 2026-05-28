"""Odds provider boundary for future sportsbook integrations."""

from ufc_predictor.odds.service import get_odds_events, get_odds_status

__all__ = ["get_odds_status", "get_odds_events"]
