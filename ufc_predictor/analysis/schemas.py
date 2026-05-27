"""Small schema helpers for fight analysis responses."""

from __future__ import annotations

from typing import TypedDict


class AnalysisSection(TypedDict):
    title: str
    body: str


class AnalysisDriver(TypedDict):
    label: str
    direction: str
    explanation: str
