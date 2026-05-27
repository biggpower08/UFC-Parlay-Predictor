"""Optional AI summary provider boundary.

Public predictions do not depend on any AI provider. This module exists so a
future provider can be added behind configuration without changing the API
shape or breaking the deterministic fallback analysis.
"""

from __future__ import annotations

from ufc_predictor.config import settings
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def generate_optional_ai_summary(structured_payload: dict) -> dict | None:
    if not settings.ENABLE_AI_SUMMARY:
        return None
    provider = (settings.AI_SUMMARY_PROVIDER or "none").strip().lower()
    if provider in {"", "none"}:
        return None
    logger.warning("AI summary provider requested but not configured provider=%s", provider)
    return None
