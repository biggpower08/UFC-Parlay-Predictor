"""Rich, deterministic fight analysis for prediction responses."""

from __future__ import annotations

import hashlib

from ufc_predictor.analysis.providers import generate_optional_ai_summary
from ufc_predictor.analysis.signals import confidence_label, data_quality_label, direction_for_names, volatility_label


def build_fight_analysis(comparison: dict, prediction: dict) -> dict:
    stats_a, stats_b = comparison["stats1"], comparison["stats2"]
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    confidence = float(prediction.get("confidence") or 0.5)
    prob_a = float(prediction.get("prob_a") or 0.5)
    winner = prediction.get("winner") or "Too close to call"
    warnings = _warnings(stats_a, stats_b, confidence)
    labels = {
        "confidence": confidence_label(confidence),
        "volatility": volatility_label(confidence, warnings),
        "data_quality": data_quality_label(stats_a, stats_b),
    }
    structured = {
        "fighter_a": _fighter_payload(stats_a, comparison.get("style1", {})),
        "fighter_b": _fighter_payload(stats_b, comparison.get("style2", {})),
        "predicted_winner": winner,
        "model_probability": round(confidence, 4),
        "probability_fighter_a": round(prob_a, 4),
        "confidence_label": labels["confidence"],
        "volatility_label": labels["volatility"],
        "data_quality_label": labels["data_quality"],
        "warnings": warnings,
        "elo_difference": _elo_difference(stats_a, stats_b),
        "weight_class_match": _same_weight_class(stats_a, stats_b),
    }
    ai = generate_optional_ai_summary(structured)
    if ai:
        return ai

    drivers = _drivers(stats_a, stats_b, prediction, labels, warnings)
    sections = _sections(stats_a, stats_b, comparison, prediction, labels, drivers, warnings)
    summary = _summary(stats_a, stats_b, prediction, labels, warnings)
    return {
        "summary": summary,
        "confidence_label": labels["confidence"],
        "volatility_label": labels["volatility"],
        "data_quality_label": labels["data_quality"],
        "sections": sections,
        "drivers": drivers,
        "warnings": warnings,
        "structured": structured,
        "provider": "deterministic_fallback",
    }


def _fighter_payload(stats: dict, style: dict) -> dict:
    return {
        "name": stats.get("Name"),
        "record": stats.get("Record"),
        "weight_class": stats.get("Weight Class"),
        "stance": stats.get("Stance"),
        "height_cm": _usable_number(stats.get("Height (cm)")),
        "reach_cm": _usable_number(stats.get("Reach (cm)")),
        "elo": stats.get("Elo") if stats.get("Elo Available") else None,
        "elo_available": bool(stats.get("Elo Available")),
        "elo_fights": stats.get("Elo Fights"),
        "style": style.get("label", "balanced"),
    }


def _summary(stats_a: dict, stats_b: dict, prediction: dict, labels: dict, warnings: list[str]) -> str:
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    winner = prediction.get("winner") or "Too close to call"
    danger_a = _danger(stats_a, stats_b)
    danger_b = _danger(stats_b, stats_a)
    lean_text = (
        f"the model leans toward {winner}"
        if winner not in {"Too close to call", None}
        else "the model reads this as a narrow matchup"
    )
    caveat = " Cross-division uncertainty is part of the read." if any("Cross-division" in w for w in warnings) else ""
    return (
        f"This matchup between {name_a} and {name_b} profiles as {labels['confidence'].lower()} with "
        f"{labels['volatility'].lower()} volatility: {lean_text}, but the biggest danger for {name_a} is "
        f"{danger_a}, while the biggest danger for {name_b} is {danger_b}.{caveat} This is a scenario-based "
        "fight read, not a guarantee."
    )


def _sections(stats_a, stats_b, comparison, prediction, labels, drivers, warnings):
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    winner = prediction.get("winner") or "Too close to call"
    style_a = comparison.get("style1", {}).get("label", "balanced")
    style_b = comparison.get("style2", {}).get("label", "balanced")
    sections = [
        {
            "title": "Main prediction",
            "body": (
                f"The official model read is {winner}. Confidence is labeled {labels['confidence']} because "
                f"the model edge, Elo availability, and data completeness point to a {labels['volatility'].lower()} "
                "volatility matchup."
            ),
        },
        {
            "title": "Big-picture fight read",
            "body": (
                f"One likely version of the fight is a {style_a} profile from {name_a} against a {style_b} profile "
                f"from {name_b}. {comparison.get('matchup', '')} The read is strongest when the available stats agree, "
                "and softer where fighter data is missing."
            ),
        },
        {
            "title": "Why the model leans this way",
            "body": " ".join(driver["explanation"] for driver in drivers[:4]),
        },
        {
            "title": f"How {name_a} could win",
            "body": _path_to_win(stats_a, stats_b, style_a),
        },
        {
            "title": f"How {name_b} could win",
            "body": _path_to_win(stats_b, stats_a, style_b),
        },
        {
            "title": "Early fight outlook",
            "body": (
                f"Early, {name_a} will likely need to establish { _opening_theme(stats_a, stats_b) }, while "
                f"{name_b} can change the tone by forcing { _opening_theme(stats_b, stats_a) }. A fast start matters, "
                "but the model does not treat the opening round as decisive by itself."
            ),
        },
        {
            "title": "Middle-round outlook",
            "body": (
                "The middle rounds could reveal whether the first layer of offense is repeatable. If takedown entries, "
                "range control, or volume trends start stacking up, the fighter winning those repeatable exchanges "
                "should begin to separate."
            ),
        },
        {
            "title": "Late-fight outlook",
            "body": (
                "Late, volatility usually rises if the matchup is close. Cardio, defensive discipline, and avoiding "
                "low-percentage scrambles become more important than any single stat edge."
            ),
        },
        {
            "title": "Key exchanges to watch",
            "body": _key_exchanges(stats_a, stats_b),
        },
        {
            "title": "Swing factors",
            "body": _swing_factors(stats_a, stats_b, warnings),
        },
        {
            "title": "Data quality and uncertainty",
            "body": _data_quality_note(labels, warnings),
        },
        {
            "title": "Final model read",
            "body": (
                f"The final read is {winner} with {labels['confidence'].lower()}. The better way to use this is as "
                "a structured fight preview: what the model sees, where the matchup can flip, and which missing data "
                "should make the forecast more cautious."
            ),
        },
    ]
    return sections


def _drivers(stats_a, stats_b, prediction, labels, warnings):
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    winner = prediction.get("winner") or "Too close to call"
    drivers = [
        {
            "label": "Model favorite",
            "direction": direction_for_names(winner, name_a, name_b),
            "explanation": (
                f"The model favors {winner}." if winner != "Too close to call" else "The model sees the winner call as close."
            ),
        }
    ]
    if stats_a.get("Elo Available") and stats_b.get("Elo Available"):
        diff = stats_a["Elo"] - stats_b["Elo"]
        leader = name_a if diff > 0 else name_b if diff < 0 else "neither fighter"
        drivers.append(
            {
                "label": "Elo profile",
                "direction": "favors_fighter_a" if diff > 0 else "favors_fighter_b" if diff < 0 else "neutral",
                "explanation": f"Elo profile favors {leader} based on completed fight history." if diff else "Elo profile is essentially even.",
            }
        )
    else:
        drivers.append(
            {
                "label": "Elo profile",
                "direction": "limited",
                "explanation": "Elo is limited because at least one fighter does not have computed Elo history.",
            }
        )
    drivers.append(
        {
            "label": "Data quality",
            "direction": labels["data_quality"].lower(),
            "explanation": f"Data quality is {labels['data_quality'].lower()}, so the model read should be interpreted with that level of caution.",
        }
    )
    if warnings:
        drivers.append(
            {
                "label": "Uncertainty",
                "direction": "caution",
                "explanation": warnings[0],
            }
        )
    return drivers


def _path_to_win(stats_self, stats_opp, style: str) -> str:
    name = stats_self["Name"]
    if style == "grappler-leaning":
        return f"{name} can build the cleanest case by forcing level changes, clinch work, mat returns, or scrambles that turn striking exchanges into grappling exchanges."
    if style == "striker-leaning":
        return f"{name} can build the cleanest case by managing range, landing first in exchanges, and making the opponent pay for entries."
    if _usable_number(stats_self.get("TD Avg")) > _usable_number(stats_opp.get("TD Avg")):
        return f"{name} has a practical path through mixed offense: enough striking to hide entries, then timely wrestling to bank minutes."
    return f"{name} likely needs a balanced fight: avoid extended defensive stretches, win enough minutes, and punish mistakes without chasing a low-percentage finish."


def _opening_theme(stats_self, stats_opp) -> str:
    if _usable_number(stats_self.get("Reach (cm)")) > _usable_number(stats_opp.get("Reach (cm)")) + 5:
        return "range and first-contact exchanges"
    if _usable_number(stats_self.get("TD Avg")) > _usable_number(stats_opp.get("TD Avg")) + 0.8:
        return "credible level changes"
    if _usable_number(stats_self.get("SLpM")) > _usable_number(stats_opp.get("SLpM")) + 0.8:
        return "pace and volume"
    return "clean reads without overcommitting"


def _key_exchanges(stats_a, stats_b) -> str:
    ideas = [
        f"{stats_a['Name']} entering safely against {stats_b['Name']}'s first layer of defense",
        f"{stats_b['Name']} answering after the first clean exchange instead of letting momentum stack",
    ]
    if _usable_number(stats_a.get("TD Avg")) or _usable_number(stats_b.get("TD Avg")):
        ideas.append("whether wrestling threats change the striking rhythm")
    if _usable_number(stats_a.get("Reach (cm)")) != _usable_number(stats_b.get("Reach (cm)")):
        ideas.append("who controls distance before combinations start")
    return "Watch " + "; ".join(ideas) + "."


def _swing_factors(stats_a, stats_b, warnings):
    factors = []
    if warnings:
        factors.extend(warnings)
    if not stats_a.get("Elo Available") or not stats_b.get("Elo Available"):
        factors.append("limited Elo history makes the confidence softer")
    if abs(_usable_number(stats_a.get("SLpM")) - _usable_number(stats_b.get("SLpM"))) < 0.4:
        factors.append("similar striking volume could make minute-winning difficult to separate")
    if not factors:
        factors.append("the biggest swing factor is whether the favorite can repeat their preferred exchanges without giving up counters")
    return " ".join(_sentence(factor) for factor in factors)


def _data_quality_note(labels, warnings):
    note = f"Data quality is {labels['data_quality'].lower()} and volatility is {labels['volatility'].lower()}."
    if warnings:
        note += " " + " ".join(warnings)
    return note + " The summary only uses available model output and fighter metadata."


def _warnings(stats_a, stats_b, confidence):
    warnings = []
    if not _same_weight_class(stats_a, stats_b):
        warnings.append("Cross-division uncertainty lowers confidence because the matchup is outside the listed weight class.")
    if not stats_a.get("Elo Available") or not stats_b.get("Elo Available"):
        warnings.append("At least one fighter has limited computed Elo history.")
    if confidence < 0.57:
        warnings.append("The model probability is close, so the matchup is volatile.")
    if data_quality_label(stats_a, stats_b) == "Limited":
        warnings.append("Several useful fighter fields are missing, so the read is less complete.")
    return warnings


def _danger(stats_self, stats_opp):
    if _usable_number(stats_opp.get("TD Avg")) > _usable_number(stats_self.get("TD Avg")) + 1.0:
        return "getting stuck defending takedowns and losing long control stretches"
    if _usable_number(stats_opp.get("SLpM")) > _usable_number(stats_self.get("SLpM")) + 1.0:
        return "letting the opponent's volume create a scoring gap"
    if _usable_number(stats_opp.get("Reach (cm)")) > _usable_number(stats_self.get("Reach (cm)")) + 5:
        return "being forced to cross distance before landing clean offense"
    if stats_opp.get("Elo Available") and stats_self.get("Elo Available") and stats_opp["Elo"] > stats_self["Elo"] + 40:
        return "letting the more proven fighter settle into a comfortable rhythm"
    return "small mistakes turning a competitive matchup into a momentum swing"


def _elo_difference(stats_a, stats_b):
    if stats_a.get("Elo Available") and stats_b.get("Elo Available"):
        return round(float(stats_a["Elo"]) - float(stats_b["Elo"]), 2)
    return None


def _same_weight_class(stats_a, stats_b):
    class_a = (stats_a.get("Weight Class") or "Unknown").lower()
    class_b = (stats_b.get("Weight Class") or "Unknown").lower()
    return "unknown" in {class_a, class_b} or class_a == class_b


def _usable_number(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number else 0.0


def _sentence(text: str) -> str:
    text = text.strip()
    if not text:
        return ""
    return text if text.endswith((".", "!", "?")) else f"{text}."


def _choose(options: list[str], key: str) -> str:
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
    return options[int(digest[:4], 16) % len(options)]
