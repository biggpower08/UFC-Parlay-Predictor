"""Requests/httpx fetcher with cache, rate limiting, and safe failures."""

from __future__ import annotations

import random
import time
from pathlib import Path

import httpx

from ufc_predictor.config import settings
from ufc_predictor.data.fetchers.base import FetchResult
from ufc_predictor.data.fetchers.cache import FetchCache
from ufc_predictor.data.fetchers.errors import (
    FetchTimeoutError,
    RateLimitError,
    SourceBlockedError,
    SourceUnavailableError,
)
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


class RequestsFetcher:
    def __init__(
        self,
        cache_dir: Path | None = None,
        timeout: float = 15.0,
        retries: int = 2,
        rate_limit_seconds: float | None = None,
        user_agent: str | None = None,
        max_response_bytes: int | None = None,
        force_refresh: bool = False,
        cache_only: bool = False,
    ) -> None:
        self.cache = FetchCache(Path(cache_dir or settings.SCRAPER_CACHE_DIR / "ufcstats"))
        self.timeout = timeout
        self.retries = retries
        self.rate_limit_seconds = settings.SCRAPER_RATE_LIMIT_SECONDS if rate_limit_seconds is None else rate_limit_seconds
        self.user_agent = user_agent or settings.SCRAPER_USER_AGENT
        self.max_response_bytes = max_response_bytes or settings.SCRAPER_MAX_RESPONSE_BYTES
        self.force_refresh = force_refresh
        self.cache_only = cache_only

    def fetch(self, url: str) -> FetchResult:
        start = time.perf_counter()
        cached = None if self.force_refresh else self.cache.read(url)
        if cached and looks_like_browser_challenge(cached):
            raise SourceBlockedError(f"Cached response for {url} is a browser JavaScript challenge")
        if cached:
            logger.info("fetch cache_hit url=%s", url)
            return FetchResult(url, cached, None, True, _elapsed_ms(start), len(cached.encode("utf-8")))
        if self.cache_only:
            raise SourceUnavailableError(f"No usable cached response for {url}")

        last_error: Exception | None = None
        for attempt in range(1, self.retries + 2):
            try:
                logger.info("fetch attempt url=%s attempt=%s", url, attempt)
                with httpx.Client(
                    timeout=self.timeout,
                    headers={"User-Agent": self.user_agent},
                    follow_redirects=True,
                ) as client:
                    response = client.get(url)
                if response.status_code in {429, 503}:
                    raise RateLimitError(f"Source returned status {response.status_code}")
                if response.status_code >= 400:
                    raise SourceUnavailableError(f"Source returned status {response.status_code}")
                text = response.text
                size = len(text.encode("utf-8"))
                if size > self.max_response_bytes:
                    raise SourceUnavailableError(f"Response too large: {size} bytes")
                if looks_like_browser_challenge(text):
                    raise SourceBlockedError("Source returned a browser JavaScript challenge instead of scrapeable HTML")
                self.cache.write(url, text)
                time.sleep(self.rate_limit_seconds)
                return FetchResult(url, text, response.status_code, False, _elapsed_ms(start), size)
            except httpx.TimeoutException as exc:
                last_error = FetchTimeoutError(str(exc))
            except (SourceBlockedError, RateLimitError) as exc:
                logger.warning("fetch stopped url=%s error=%s", url, exc)
                raise
            except Exception as exc:
                last_error = exc

            if attempt <= self.retries:
                delay = min(8.0, self.rate_limit_seconds * (2 ** attempt)) + random.uniform(0, 0.25)
                logger.warning("fetch retry url=%s attempt=%s error=%s delay=%.2f", url, attempt, last_error, delay)
                time.sleep(delay)

        raise SourceUnavailableError(f"Could not fetch {url}: {last_error}")


def looks_like_browser_challenge(html: str) -> bool:
    text = (html or "").lower()
    return "checking your browser" in text or "requires javascript" in text or "cf-chl" in text


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
