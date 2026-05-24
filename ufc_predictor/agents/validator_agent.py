"""Normalize scraped fighter profiles into the stats schema."""

from ufc_predictor.config import settings
from ufc_predictor.utils.helpers import normalize_name, safe_float


SOURCE_CONFIDENCE = {
    "ufcstats": 0.99,
    "tapology": 0.93,
    "sherdog": 0.88,
    "wikipedia": 0.80,
}


def validate_and_normalize(raw: dict) -> dict:
    source = raw.get("source", "unknown")
    confidence = SOURCE_CONFIDENCE.get(source, 0.5)
    name = raw.get("name") or raw.get("fighter") or raw.get("title")
    if not name:
        raise ValueError("Scraped profile did not include a fighter name")

    record = {
        "name": name,
        "nickname": raw.get("nickname"),
        "wins": safe_float(raw.get("wins"), 0),
        "losses": safe_float(raw.get("losses"), 0),
        "draws": safe_float(raw.get("draws"), 0),
        "height_cm": safe_float(raw.get("height_cm"), 0),
        "weight_in_kg": safe_float(raw.get("weight_in_kg"), 0),
        "reach_in_cm": safe_float(raw.get("reach_in_cm"), 0),
        "stance": raw.get("stance") or "",
        "date_of_birth": raw.get("date_of_birth"),
        "significant_strikes_landed_per_minute": safe_float(raw.get("slpm"), 0),
        "significant_striking_accuracy": safe_float(raw.get("str_acc"), 0),
        "significant_strikes_absorbed_per_minute": safe_float(raw.get("sapm"), 0),
        "significant_strike_defence": safe_float(raw.get("str_def"), 0),
        "average_takedowns_landed_per_15_minutes": safe_float(raw.get("td_avg"), 0),
        "takedown_accuracy": safe_float(raw.get("td_acc"), 0),
        "takedown_defense": safe_float(raw.get("td_def"), 0),
        "average_submissions_attempted_per_15_minutes": safe_float(raw.get("sub_avg"), 0),
        "elo": settings.ELO_INITIAL,
        "peak_elo": settings.ELO_INITIAL,
        "source": source,
        "source_confidence": confidence,
    }
    record["normalized_name"] = normalize_name(record["name"])
    record["_search_name"] = record["normalized_name"]
    return record
