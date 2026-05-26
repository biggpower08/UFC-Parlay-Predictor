from pathlib import Path

import pytest

from ufc_predictor.data.fetchers.cache import FetchCache
from ufc_predictor.data.fetchers.errors import SourceBlockedError, SourceUnavailableError
from ufc_predictor.data.fetchers.requests_fetcher import RequestsFetcher, looks_like_browser_challenge


def test_fetcher_reads_cached_response_without_network(tmp_path: Path):
    url = "http://example.test/events"
    cache = FetchCache(tmp_path)
    cache.write(url, "<html><a href='/event-details/1'>Event</a></html>")

    fetcher = RequestsFetcher(cache_dir=tmp_path, cache_only=True)
    result = fetcher.fetch(url)

    assert result.from_cache is True
    assert "event-details" in result.text


def test_fetcher_cache_only_fails_when_cache_missing(tmp_path: Path):
    fetcher = RequestsFetcher(cache_dir=tmp_path, cache_only=True)

    with pytest.raises(SourceUnavailableError):
        fetcher.fetch("http://example.test/missing")


def test_browser_challenge_is_detected_from_cached_response(tmp_path: Path):
    url = "http://example.test/challenge"
    cache = FetchCache(tmp_path)
    cache.write(url, "<html><title>Checking your browser before accessing</title><script>cf-chl</script></html>")

    fetcher = RequestsFetcher(cache_dir=tmp_path, cache_only=True)

    with pytest.raises(SourceBlockedError):
        fetcher.fetch(url)


def test_browser_challenge_detector_matches_common_block_pages():
    assert looks_like_browser_challenge("Checking your browser before accessing this page")
    assert looks_like_browser_challenge("This site requires JavaScript to continue")
    assert looks_like_browser_challenge("window._cf_chl_opt = {}; cf-chl")
