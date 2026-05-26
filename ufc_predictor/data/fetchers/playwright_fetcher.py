"""Optional Playwright fetcher for ordinary JavaScript-rendered pages.

This is not used to bypass explicit source blocks or CAPTCHA. If a rendered
page still looks challenged, it raises SourceBlockedError.
"""

from __future__ import annotations

import time
from pathlib import Path

from ufc_predictor.config import settings
from ufc_predictor.data.fetchers.base import FetchResult
from ufc_predictor.data.fetchers.cache import FetchCache
from ufc_predictor.data.fetchers.errors import SourceBlockedError, SourceUnavailableError
from ufc_predictor.data.fetchers.requests_fetcher import looks_like_browser_challenge


class PlaywrightFetcher:
    def __init__(
        self,
        cache_dir: Path | None = None,
        timeout: float = 20.0,
        force_refresh: bool = False,
        cache_only: bool = False,
    ) -> None:
        self.cache = FetchCache(Path(cache_dir or settings.SCRAPER_CACHE_DIR / "ufcstats"))
        self.timeout = timeout
        self.force_refresh = force_refresh
        self.cache_only = cache_only

    def fetch(self, url: str) -> FetchResult:
        start = time.perf_counter()
        cached = None if self.force_refresh else self.cache.read(url)
        if cached and looks_like_browser_challenge(cached):
            raise SourceBlockedError(f"Cached response for {url} is a browser JavaScript challenge")
        if cached:
            return FetchResult(url, cached, None, True, _elapsed_ms(start), len(cached.encode("utf-8")))
        if self.cache_only:
            raise SourceUnavailableError(f"No usable cached response for {url}")

        try:
            from playwright.sync_api import sync_playwright
        except Exception as exc:  # pragma: no cover - depends on optional install
            raise SourceUnavailableError("Playwright fetcher requested but Playwright is not installed.") from exc

        try:
            with sync_playwright() as pw:
                browser = pw.chromium.launch(headless=True)
                page = browser.new_page(user_agent=settings.SCRAPER_USER_AGENT)
                response = page.goto(url, wait_until="domcontentloaded", timeout=int(self.timeout * 1000))
                html = page.content()
                status = response.status if response else None
                browser.close()
        except Exception as exc:  # pragma: no cover - browser runtime varies
            raise SourceUnavailableError(f"Playwright fetch failed for {url}: {exc}") from exc

        if looks_like_browser_challenge(html):
            raise SourceBlockedError("Rendered page is still a browser challenge; refusing to bypass source protection.")
        self.cache.write(url, html)
        return FetchResult(url, html, status, False, _elapsed_ms(start), len(html.encode("utf-8")))


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
