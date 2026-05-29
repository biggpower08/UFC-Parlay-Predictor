"""Fetcher interface shared by scraper sources."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FetchResult:
    url: str
    text: str
    status_code: int | None
    from_cache: bool
    elapsed_ms: float
    bytes_read: int
    challenged: bool = False
    final_url: str | None = None
    content_type: str | None = None
