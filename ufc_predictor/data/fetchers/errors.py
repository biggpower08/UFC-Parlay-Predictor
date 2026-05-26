"""Structured scraper fetch errors."""


class FetchError(RuntimeError):
    """Base class for source fetch failures."""


class SourceBlockedError(FetchError):
    """The source returned an explicit browser challenge or block page."""


class SourceUnavailableError(FetchError):
    """The source could not be reached or returned an unusable response."""


class ParseError(FetchError):
    """A source response could not be parsed into expected records."""


class RateLimitError(FetchError):
    """The source appears to be rate-limiting requests."""


class FetchTimeoutError(FetchError):
    """The source request timed out."""
