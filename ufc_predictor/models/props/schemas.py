"""Schemas for future method, round, volume, and odds-edge models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PropModelAvailability = Literal["available", "unavailable", "trained", "not_trained", "insufficient_data"]


@dataclass(frozen=True)
class PropModelStatus:
    name: str
    status: PropModelAvailability
    support_level: str
    message: str
