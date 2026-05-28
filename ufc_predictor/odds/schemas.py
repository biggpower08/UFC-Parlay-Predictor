"""Schemas for odds provider status and normalized odds payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OddsProviderStatus:
    odds_enabled: bool
    provider: str
    message: str
    cache_ttl_seconds: int


@dataclass(frozen=True)
class OddsEvent:
    id: str
    name: str
    start_time: str | None = None
    fights: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class NormalizedOddsMarket:
    market_type: str
    sportsbook: str | None
    selection_name: str
    american_odds: int | None = None
    decimal_odds: float | None = None
    source_timestamp: str | None = None
    raw_payload: dict[str, Any] | None = None
