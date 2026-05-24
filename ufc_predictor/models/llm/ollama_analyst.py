"""Local Ollama analyst that returns strict JSON or stays offline."""

import json

from ufc_predictor.config import settings
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def get_ollama_status() -> dict:
    """Return one shared Ollama status shape for health and predictions."""
    try:
        import httpx

        response = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=2)
        response.raise_for_status()
        models = response.json().get("models", [])
        loaded_names = {model.get("name", "").split(":")[0] for model in models}
        loaded_full_names = {model.get("name", "") for model in models}
        model_loaded = (
            settings.OLLAMA_MODEL in loaded_names
            or settings.OLLAMA_MODEL in loaded_full_names
        )
        error = None if model_loaded else f"Model '{settings.OLLAMA_MODEL}' is not loaded in Ollama."
        status = {"available": True, "model_loaded": model_loaded, "error": error}
        if error:
            logger.warning("Ollama status warning: %s", error)
        return status
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        logger.exception("Ollama status check failed: %s", message)
        return {"available": False, "model_loaded": False, "error": message}


def ollama_status() -> dict:
    """Backward-compatible name used by older imports."""
    return get_ollama_status()


def analyze_matchup(stats_a: dict, stats_b: dict, comparison: dict, sklearn_prob, elo_prob) -> dict:
    status = get_ollama_status()
    if not status["available"] or not status["model_loaded"]:
        return {"available": False, **status}

    try:
        import httpx
    except ImportError as exc:
        message = f"{type(exc).__name__}: {exc}"
        logger.exception("Ollama analyst dependency failed: %s", message)
        return {"available": False, "model_loaded": status["model_loaded"], "error": message}

    prompt = _build_prompt(stats_a, stats_b, comparison, sklearn_prob, elo_prob)
    try:
        response = httpx.post(
            f"{settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "options": {"temperature": 0.2},
            },
            timeout=30,
        )
        response.raise_for_status()
        outer = response.json()
        payload = json.loads(outer.get("response", "{}"))
        return {"available": True, **status, **_validate_response(payload, stats_a["Name"], stats_b["Name"])}
    except Exception as exc:
        message = f"{type(exc).__name__}: {exc}"
        logger.exception("Ollama prediction call failed: %s", message)
        return {"available": False, "model_loaded": status["model_loaded"], "error": message}


def _build_prompt(stats_a, stats_b, comparison, sklearn_prob, elo_prob) -> str:
    payload = {
        "fighter_a": stats_a,
        "fighter_b": stats_b,
        "edges": comparison.get("edges", {}),
        "style_a": comparison.get("style1", {}),
        "style_b": comparison.get("style2", {}),
        "sklearn_prob_a": sklearn_prob,
        "elo_prob_a": elo_prob,
    }
    return (
        "You are an MMA matchup analyst. Use only the JSON stats provided. "
        "Do not invent injuries, camps, odds, or unprovided facts. Return strict JSON with keys: "
        "winner, confidence, reasoning, cited_fields. confidence must be 0.5 to 0.95. "
        f"Input JSON: {json.dumps(payload, default=str)}"
    )


def _validate_response(payload: dict, name_a: str, name_b: str) -> dict:
    winner = payload.get("winner")
    if winner not in {name_a, name_b, "Too close to call"}:
        winner = "Too close to call"
    try:
        confidence = min(0.95, max(0.5, float(payload.get("confidence", 0.5))))
    except (TypeError, ValueError):
        confidence = 0.5
    return {
        "winner": winner,
        "confidence": confidence,
        "reasoning": str(payload.get("reasoning") or "Local analyst did not provide reasoning."),
        "cited_fields": payload.get("cited_fields") or [],
    }
