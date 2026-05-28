"""Fetch backends for scraper sources."""

from ufc_predictor.data.fetchers.base import FetchResult
from ufc_predictor.data.fetchers.errors import (
    FetchTimeoutError,
    ParseError,
    RateLimitError,
    SourceBlockedError,
    SourceUnavailableError,
)

__all__ = [
    "FetchResult",
    "FetchTimeoutError",
    "ParseError",
    "RateLimitError",
    "RequestsFetcher",
    "SourceBlockedError",
    "SourceUnavailableError",
]


def __getattr__(name):
    if name == "RequestsFetcher":
        from ufc_predictor.data.fetchers.requests_fetcher import RequestsFetcher

        return RequestsFetcher
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
