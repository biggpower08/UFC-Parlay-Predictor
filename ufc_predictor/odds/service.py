"""Service layer for odds status and future odds ingestion."""

from __future__ import annotations

from dataclasses import asdict

from ufc_predictor.odds.providers import get_provider


def get_odds_status() -> dict:
    return asdict(get_provider().status())


def get_odds_events() -> dict:
    provider = get_provider()
    return {
        "status": asdict(provider.status()),
        "events": [asdict(event) for event in provider.events()],
    }
