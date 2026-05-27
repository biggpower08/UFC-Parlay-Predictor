"""Prompt builder for future optional AI analysis providers."""

from __future__ import annotations


def build_analysis_prompt(payload: dict) -> str:
    return (
        "Create a cautious UFC/MMA matchup analysis from only the provided JSON. "
        "Do not invent missing stats, do not guarantee outcomes, and frame round "
        f"outlooks as scenarios.\n\nDATA:\n{payload}"
    )
