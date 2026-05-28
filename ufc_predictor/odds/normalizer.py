"""Normalization helpers for future odds provider payloads."""

from __future__ import annotations

from ufc_predictor.odds.schemas import NormalizedOddsMarket


def empty_markets() -> list[NormalizedOddsMarket]:
    return []
