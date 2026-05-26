"""Fetch backends for scraper sources."""

from ufc_predictor.data.fetchers.base import FetchResult
from ufc_predictor.data.fetchers.errors import (
    FetchTimeoutError,
    ParseError,
    RateLimitError,
    SourceBlockedError,
    SourceUnavailableError,
)
from ufc_predictor.data.fetchers.requests_fetcher import RequestsFetcher

__all__ = [
    "FetchResult",
    "FetchTimeoutError",
    "ParseError",
    "RateLimitError",
    "RequestsFetcher",
    "SourceBlockedError",
    "SourceUnavailableError",
]
