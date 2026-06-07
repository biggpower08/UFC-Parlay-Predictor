"""Source priority rules for multi-source UFC/MMA normalization."""

from __future__ import annotations


SOURCE_PRIORITY = {
    "ufc_fight_forecast": 10,
    "ufc_stats_complete": 20,
    "ufc_1994_2026": 30,
    "ufc_1994_2025": 40,
    "mdabbert_ultimate": 50,
    "mdabbert_2010_2020_odds": 60,
    "ufc_datalab": 70,
    "unknown": 999,
}


def priority_for_source(dataset_key: str | None) -> int:
    return SOURCE_PRIORITY.get(str(dataset_key or "unknown"), SOURCE_PRIORITY["unknown"])


def source_use_notes(dataset_key: str | None) -> list[str]:
    key = str(dataset_key or "unknown")
    if key == "ufc_stats_complete":
        return ["Prefer for detailed fight-stat labels when event dates and fight identity are present."]
    if key.startswith("mdabbert"):
        return ["Use odds only when timestamp quality is pre-fight or clearly reviewable."]
    if key == "ufc_datalab":
        return ["Use scorecards as post-fight labels/analysis artifacts, not pre-fight features."]
    return ["Use after leakage scan and deduping."]
