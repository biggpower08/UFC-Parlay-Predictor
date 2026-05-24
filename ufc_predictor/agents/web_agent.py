"""Thin coordinator for scraper and validator agents."""

from ufc_predictor.agents.scraper_agent import scrape_fighter
from ufc_predictor.agents.validator_agent import validate_and_normalize


def fetch_and_normalize_fighter(name: str) -> dict:
    raw = scrape_fighter(name)
    if raw is None:
        raise LookupError(f"No web profile found for {name}")
    return validate_and_normalize(raw)
