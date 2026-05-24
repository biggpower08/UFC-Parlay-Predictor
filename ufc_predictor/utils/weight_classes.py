"""Simple UFC weight class helpers."""

from ufc_predictor.utils.helpers import safe_float


WEIGHT_CLASSES_KG = [
    ("Strawweight", 52.16),
    ("Flyweight", 56.70),
    ("Bantamweight", 61.23),
    ("Featherweight", 65.77),
    ("Lightweight", 70.31),
    ("Welterweight", 77.11),
    ("Middleweight", 83.91),
    ("Light Heavyweight", 93.00),
    ("Heavyweight", 120.20),
]


def detect_weight_class(row_or_stats) -> str:
    """Use a dataset weight class when present, otherwise infer from weight."""
    for key in ("weight_class", "Weight Class", "division", "Division"):
        value = _get_value(row_or_stats, key)
        if value:
            return str(value)

    weight_kg = safe_float(
        _get_value(row_or_stats, "weight_in_kg")
        or _get_value(row_or_stats, "Weight (kg)")
        or _get_value(row_or_stats, "weight"),
        0,
    )
    if weight_kg <= 0:
        return "Unknown"

    for label, limit_kg in WEIGHT_CLASSES_KG:
        if weight_kg <= limit_kg + 0.25:
            return label
    return "Heavyweight"


def same_weight_class(class_a: str, class_b: str) -> bool:
    if not class_a or not class_b:
        return True
    if "unknown" in {class_a.lower(), class_b.lower()}:
        return True
    return class_a == class_b


def _get_value(row_or_stats, key):
    if isinstance(row_or_stats, dict):
        return row_or_stats.get(key)
    try:
        return row_or_stats.get(key)
    except AttributeError:
        return None
