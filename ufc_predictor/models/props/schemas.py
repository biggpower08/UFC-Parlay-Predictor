"""Schemas for future method, round, volume, and odds-edge models."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PropModelAvailability = Literal[
    "not_trained",
    "insufficient_data",
    "blocked_missing_labels",
    "blocked_missing_dates",
    "training_data_ready",
    "trained",
    "experimental",
    "unavailable",
]


@dataclass(frozen=True)
class PropModelStatus:
    name: str
    status: PropModelAvailability
    support_level: str
    message: str
