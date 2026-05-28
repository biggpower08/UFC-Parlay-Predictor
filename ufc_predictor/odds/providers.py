"""Odds provider abstractions.

No live sportsbook provider is enabled by default. Future integrations should
implement BaseOddsProvider without changing API consumers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ufc_predictor.config import settings
from ufc_predictor.odds.schemas import OddsEvent, OddsProviderStatus


class BaseOddsProvider(ABC):
    name = "base"

    @abstractmethod
    def status(self) -> OddsProviderStatus:
        """Return provider readiness without fetching protected or paid data."""

    @abstractmethod
    def events(self) -> list[OddsEvent]:
        """Return available events, or an empty list when unavailable."""


class EmptyOddsProvider(BaseOddsProvider):
    name = "none"

    def status(self) -> OddsProviderStatus:
        return OddsProviderStatus(
            odds_enabled=False,
            provider="none",
            message="Live odds provider is not configured.",
            cache_ttl_seconds=settings.ODDS_CACHE_TTL_SECONDS,
        )

    def events(self) -> list[OddsEvent]:
        return []


class TheOddsAPIProvider(EmptyOddsProvider):
    name = "the_odds_api"

    def status(self) -> OddsProviderStatus:
        return OddsProviderStatus(
            odds_enabled=False,
            provider=self.name,
            message="TheOddsAPI provider hook exists, but live fetching is not enabled in this build.",
            cache_ttl_seconds=settings.ODDS_CACHE_TTL_SECONDS,
        )


class OddsJamProvider(EmptyOddsProvider):
    name = "oddsjam"

    def status(self) -> OddsProviderStatus:
        return OddsProviderStatus(
            odds_enabled=False,
            provider=self.name,
            message="OddsJam provider hook exists, but live fetching is not enabled in this build.",
            cache_ttl_seconds=settings.ODDS_CACHE_TTL_SECONDS,
        )


def get_provider() -> BaseOddsProvider:
    if not settings.ENABLE_ODDS:
        return EmptyOddsProvider()
    provider = (settings.ODDS_PROVIDER or "none").strip().lower()
    if provider in {"theoddsapi", "the_odds_api"}:
        return TheOddsAPIProvider()
    if provider in {"oddsjam", "odds_jam"}:
        return OddsJamProvider()
    return EmptyOddsProvider()
