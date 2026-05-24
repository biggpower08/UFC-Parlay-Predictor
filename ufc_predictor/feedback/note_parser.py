"""Parse qualitative user notes into feature flags."""

from pathlib import Path

from ufc_predictor.config import settings

NOTE_FLAG_NAMES = [
    "injury_flag",
    "short_notice_flag",
    "weight_cut_issue_flag",
    "stylistic_mismatch_flag",
    "cardio_issue_flag",
    "layoff_concern_flag",
    "age_decline_flag",
    "chin_decline_flag",
    "momentum_flag",
    "home_crowd_flag",
]


def _load_tag_config():
    path = settings.NOTE_TAGS_YAML
    with open(path, encoding="utf-8") as f:
        text = f.read()
    try:
        import yaml

        return yaml.safe_load(text)
    except ImportError:
        return _minimal_yaml_tag_config(text)


def _minimal_yaml_tag_config(text: str) -> dict:
    """Small fallback parser for config/note_tags.yaml when PyYAML is absent."""
    categories = {}
    current = None
    in_keywords = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped == "categories:":
            continue
        if raw_line.startswith("  ") and not raw_line.startswith("    ") and stripped.endswith(":"):
            current = stripped[:-1]
            categories[current] = {"keywords": []}
            in_keywords = False
        elif current and stripped.startswith("flag:"):
            categories[current]["flag"] = stripped.split(":", 1)[1].strip()
        elif current and stripped.startswith("keywords:"):
            in_keywords = True
        elif current and in_keywords and stripped.startswith("- "):
            categories[current]["keywords"].append(stripped[2:].strip())
    return {"categories": categories}


def parse_user_notes(notes: str) -> dict:
    """
    Convert free-text notes to binary flags.
    Example: "fighter looked injured" -> injury_flag=1
    """
    text = (notes or "").lower()
    config = _load_tag_config()
    flags = {name: 0 for name in NOTE_FLAG_NAMES}

    for _category, spec in config.get("categories", {}).items():
        flag_name = spec.get("flag")
        if flag_name not in flags:
            continue
        for keyword in spec.get("keywords", []):
            if keyword.lower() in text:
                flags[flag_name] = 1
                break
    return flags


def assign_flags_to_fighters(
    notes: str,
    fighter_a_name: str,
    fighter_b_name: str,
) -> tuple[dict, dict]:
    """
    If notes mention a fighter name, assign flags to that side; else both.
    """
    flags = parse_user_notes(notes)
    if not any(flags.values()):
        return {}, {}

    text = (notes or "").lower()
    a_key = fighter_a_name.lower()
    b_key = fighter_b_name.lower()
    flags_a, flags_b = {}, {}

    if a_key in text and b_key not in text:
        flags_a = flags
    elif b_key in text and a_key not in text:
        flags_b = flags
    else:
        flags_a = flags
        flags_b = flags
    return flags_a, flags_b


def note_flags_to_delta_features(flags_a: dict, flags_b: dict) -> dict:
    """Delta note features for matchup (A minus B)."""
    deltas = {}
    for name in NOTE_FLAG_NAMES:
        a_val = flags_a.get(name, 0)
        b_val = flags_b.get(name, 0)
        deltas[f"delta_{name}"] = float(a_val - b_val)
    return deltas
