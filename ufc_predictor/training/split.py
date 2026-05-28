"""Chronological split helpers for leakage-safe model validation."""

from __future__ import annotations


def chronological_split(rows, test_size: float = 0.2):
    if not 0 < test_size < 1:
        raise ValueError("test_size must be between 0 and 1.")
    total = len(rows)
    split_at = max(1, int(total * (1 - test_size)))
    return rows[:split_at], rows[split_at:]
