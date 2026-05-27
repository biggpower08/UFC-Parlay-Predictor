"""Derive qualitative matchup labels and drivers from prediction data."""

from __future__ import annotations


def confidence_label(confidence: float) -> str:
    if confidence >= 0.65:
        return "High Confidence"
    if confidence >= 0.57:
        return "Medium Confidence"
    return "Low Confidence"


def volatility_label(confidence: float, warnings: list[str]) -> str:
    if confidence < 0.57 or any("Cross-division" in warning for warning in warnings):
        return "High"
    if confidence < 0.65 or warnings:
        return "Medium"
    return "Lower"


def data_quality_label(stats_a: dict, stats_b: dict) -> str:
    needed = ["SLpM", "SApM", "TD Avg", "TD Def %", "Reach (cm)", "Stance"]
    available = 0
    total = len(needed) * 2 + 2
    for stats in (stats_a, stats_b):
        for key in needed:
            value = stats.get(key)
            if value not in (None, "", "N/A", 0, 0.0):
                available += 1
        if stats.get("Elo Available"):
            available += 1
    ratio = available / max(total, 1)
    if ratio >= 0.78:
        return "Strong"
    if ratio >= 0.5:
        return "Partial"
    return "Limited"


def direction_for_names(winner: str, name_a: str, name_b: str) -> str:
    if winner == name_a:
        return "favors_fighter_a"
    if winner == name_b:
        return "favors_fighter_b"
    return "neutral"
