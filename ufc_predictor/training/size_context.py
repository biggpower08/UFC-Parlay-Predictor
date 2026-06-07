"""Cross-division and size-context features for MMA matchups."""

from __future__ import annotations


WEIGHT_CLASS_WEIGHTS = {
    "strawweight": 115,
    "flyweight": 125,
    "bantamweight": 135,
    "featherweight": 145,
    "lightweight": 155,
    "welterweight": 170,
    "middleweight": 185,
    "light heavyweight": 205,
    "heavyweight": 265,
}

WEIGHT_CLASS_ORDER = {name: index for index, name in enumerate(WEIGHT_CLASS_WEIGHTS)}


def build_size_context(fighter_1: dict, fighter_2: dict, pound_for_pound: bool = False) -> dict:
    class_1 = _weight_class(fighter_1)
    class_2 = _weight_class(fighter_2)
    unknown = not class_1 or not class_2
    class_gap = None if unknown else WEIGHT_CLASS_ORDER.get(class_1, 0) - WEIGHT_CLASS_ORDER.get(class_2, 0)
    weight_gap = None if unknown else WEIGHT_CLASS_WEIGHTS.get(class_1, 0) - WEIGHT_CLASS_WEIGHTS.get(class_2, 0)
    height_gap = _number(fighter_1.get("height_cm") or fighter_1.get("Height (cm)")) - _number(fighter_2.get("height_cm") or fighter_2.get("Height (cm)"))
    reach_gap = _number(fighter_1.get("reach_cm") or fighter_1.get("Reach (cm)")) - _number(fighter_2.get("reach_cm") or fighter_2.get("Reach (cm)"))
    age_gap = _number(fighter_1.get("age") or fighter_1.get("Age")) - _number(fighter_2.get("age") or fighter_2.get("Age"))
    if unknown:
        label = "size context limited"
        severity = "soft"
    elif class_gap == 0:
        label = "same division"
        severity = "none"
    elif abs(class_gap) == 1:
        label = "possible cross-division"
        severity = "soft"
    else:
        label = "cross-division"
        severity = "high"
    return {
        "fighter_1_weight_class": class_1 or "unknown",
        "fighter_2_weight_class": class_2 or "unknown",
        "weight_class_gap": 0 if pound_for_pound and class_gap is not None else class_gap,
        "estimated_weight_gap_lbs": 0 if pound_for_pound and weight_gap is not None else weight_gap,
        "height_gap": 0 if pound_for_pound else round(height_gap, 2),
        "reach_gap": 0 if pound_for_pound else round(reach_gap, 2),
        "age_gap": round(age_gap, 2),
        "division_jump_direction": _jump_direction(class_gap),
        "same_division": bool(class_gap == 0 and not unknown),
        "cross_division": bool(class_gap is not None and abs(class_gap) > 1),
        "catchweight": "catch" in (class_1 or "") or "catch" in (class_2 or ""),
        "unknown_size_context": unknown,
        "pound_for_pound_mode": pound_for_pound,
        "size_features_used": not pound_for_pound,
        "label": "pound-for-pound view" if pound_for_pound else label,
        "severity": "none" if pound_for_pound else severity,
        "warning": _warning(label, pound_for_pound),
    }


def _weight_class(fighter: dict) -> str | None:
    value = fighter.get("weight_class") or fighter.get("Weight Class") or fighter.get("division")
    if not value:
        return None
    text = str(value).strip().lower()
    if text in WEIGHT_CLASS_WEIGHTS:
        return text
    for known in WEIGHT_CLASS_WEIGHTS:
        if known in text:
            return known
    if "catch" in text:
        return "catchweight"
    return None


def _jump_direction(class_gap: int | None) -> str:
    if class_gap is None or class_gap == 0:
        return "none"
    return "fighter_1_heavier" if class_gap > 0 else "fighter_2_heavier"


def _warning(label: str, pound_for_pound: bool) -> str | None:
    if pound_for_pound:
        return "Pound-for-pound view reduces size advantages and should be read separately from actual fight context."
    if label == "cross-division":
        return "Cross-division size context can reduce matchup realism and confidence."
    if label == "size context limited":
        return "Weight-class data is incomplete; size context is estimated or unavailable."
    if label == "possible cross-division":
        return "Adjacent or uncertain divisions make the size read less certain."
    return None


def _number(value) -> float:
    try:
        number = float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number else 0.0
