"""Metrics helpers for future dedicated prop-model training."""

from __future__ import annotations

from collections import Counter


def majority_class_baseline(labels) -> dict:
    counts = Counter(labels)
    total = sum(counts.values())
    if not total:
        return {"label": None, "accuracy": None, "class_counts": {}}
    label, count = counts.most_common(1)[0]
    return {
        "label": label,
        "accuracy": round(count / total, 4),
        "class_counts": {str(key): int(value) for key, value in counts.items()},
    }
