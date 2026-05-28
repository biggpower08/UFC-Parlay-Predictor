"""Rich, deterministic fight analysis for prediction responses."""

from __future__ import annotations

import hashlib

from ufc_predictor.analysis.providers import generate_optional_ai_summary
from ufc_predictor.analysis.signals import confidence_label, data_quality_label, direction_for_names, volatility_label

WEIGHT_CLASS_ORDER = {
    "strawweight": 0,
    "flyweight": 1,
    "bantamweight": 2,
    "featherweight": 3,
    "lightweight": 4,
    "welterweight": 5,
    "middleweight": 6,
    "light heavyweight": 7,
    "heavyweight": 8,
}


def build_fight_analysis(comparison: dict, prediction: dict) -> dict:
    stats_a, stats_b = comparison["stats1"], comparison["stats2"]
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    confidence = float(prediction.get("confidence") or 0.5)
    prob_a = float(prediction.get("prob_a") or 0.5)
    winner = prediction.get("winner") or "Too close to call"
    matchup_type = _matchup_type(stats_a, stats_b)
    warnings = _warnings(stats_a, stats_b, confidence, matchup_type)
    labels = {
        "confidence": confidence_label(confidence),
        "volatility": volatility_label(confidence, warnings),
        "data_quality": data_quality_label(stats_a, stats_b),
    }
    drivers = _drivers(stats_a, stats_b, prediction, labels, warnings)
    secondary_reads = _secondary_reads(stats_a, stats_b, comparison, prediction, labels, warnings)
    prop_reads = _prop_reads(stats_a, stats_b, comparison, prediction, labels, warnings, matchup_type)
    sections = _sections(stats_a, stats_b, comparison, prediction, labels, drivers, warnings, secondary_reads, prop_reads)
    summary = _summary(stats_a, stats_b, prediction, labels, warnings)
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
        "matchup_type": matchup_type,
        "secondary_reads": secondary_reads,
        "prop_reads": prop_reads,
    }
    ai = generate_optional_ai_summary(structured)
    if ai:
        ai.setdefault("matchup_type", matchup_type)
        ai.setdefault("secondary_reads", secondary_reads)
        ai.setdefault("prop_reads", prop_reads)
        ai.setdefault("sections", sections)
        ai.setdefault("drivers", drivers)
        ai.setdefault("warnings", warnings)
        ai.setdefault("structured", structured)
        return ai

    return {
        "summary": summary,
        "confidence_label": labels["confidence"],
        "volatility_label": labels["volatility"],
        "data_quality_label": labels["data_quality"],
        "matchup_type": matchup_type,
        "secondary_reads": secondary_reads,
        "prop_reads": prop_reads,
        "responsible_use": "These prop reads are informational model analysis, not guarantees or financial advice. Fight outcomes are uncertain.",
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
        "fight read, not a certainty."
    )


def _sections(stats_a, stats_b, comparison, prediction, labels, drivers, warnings, secondary_reads, prop_reads):
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    winner = prediction.get("winner") or "Too close to call"
    style_a = comparison.get("style1", {}).get("label", "balanced")
    style_b = comparison.get("style2", {}).get("label", "balanced")
    method_read = _read_by_type(secondary_reads, "method_lean")
    pace_read = _read_by_type(secondary_reads, "pace_volume")
    round_read = _read_by_type(secondary_reads, "round_phase")
    sections = [
        {
            "title": "Main prediction read",
            "body": (
                f"The model read is {winner}, with {labels['confidence'].lower()} and "
                f"{labels['volatility'].lower()} volatility. This is a winner-probability forecast first; "
                "the notes below translate the matchup into scenario projections without treating them as exact outcomes."
            ),
        },
        {
            "title": "Method lean",
            "body": method_read["read"] if method_read else _method_lane(stats_a, stats_b, prediction),
        },
        {
            "title": f"{name_a} path to victory",
            "body": _path_to_win(stats_a, stats_b, style_a),
        },
        {
            "title": f"{name_b} path to victory",
            "body": _path_to_win(stats_b, stats_a, style_b),
        },
        {
            "title": "Prop-style angles",
            "body": _prop_section_read(prop_reads),
        },
        {
            "title": "Early fight phase",
            "body": (
                f"Early, {name_a} needs to show {_opening_theme(stats_a, stats_b)}, while {name_b} can interrupt that "
                f"by forcing {_opening_theme(stats_b, stats_a)}. The opening minutes matter most as a read on range, "
                "reaction time, and whether either fighter can make the other reset."
            ),
        },
        {
            "title": "Middle fight phase",
            "body": round_read["read"] if round_read else (
                "Rounds 2-3 should clarify which fighter can repeat their first-layer offense after adjustments begin."
            ),
        },
        {
            "title": "Late fight phase",
            "body": (
                f"Late, the read shifts toward composure and minute-winning. If {winner} is ahead, the safer lane is "
                "repeatable control rather than chasing a dramatic finish; if the fight is close, one defensive lapse "
                "or scramble can outweigh several quiet minutes."
            ),
        },
        {
            "title": "Key exchanges",
            "body": _key_exchanges(stats_a, stats_b),
        },
        {
            "title": "Pace and volume read",
            "body": pace_read["read"] if pace_read else _pace_volume_read(stats_a, stats_b),
        },
        {
            "title": "Volatility warning",
            "body": _volatility_prop_warning(labels, warnings),
        },
        {
            "title": "Data quality note",
            "body": _data_quality_note(labels, warnings),
        },
        {
            "title": "Final analyst read",
            "body": (
                f"The final read is {winner} with {labels['confidence'].lower()}. The better way to use this is as "
                "a structured fight preview: the favorite, the opponent's live routes back into the fight, the exchanges "
                "that can flip the forecast, and the uncertainty that should keep the read measured."
            ),
        },
    ]
    return sections


def _prop_reads(stats_a, stats_b, comparison, prediction, labels, warnings, matchup_type):
    # Future hook: replace or enrich these with dedicated method, round, strike-volume,
    # takedown/control, and goes-distance model outputs when trained models exist.
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    style_a = comparison.get("style1", {}).get("label", "balanced")
    style_b = comparison.get("style2", {}).get("label", "balanced")
    favorite = _favorite_stats(stats_a, stats_b, prediction)
    underdog = stats_b if favorite is stats_a else stats_a
    base_confidence = _prop_confidence(prediction, labels, warnings, matchup_type)
    scenario_confidence = "low" if base_confidence != "high" else "medium"
    support = "model_informed_read" if base_confidence in {"medium", "high"} else "scenario_read"
    method_style = _method_prop_style(favorite, underdog, prediction)
    prop_reads = [
        {
            "id": "favorite_method_lean",
            "category": "method",
            "label": f"{favorite['Name']} method lean",
            "fighter": favorite["Name"],
            "prop_style": method_style,
            "confidence": base_confidence,
            "support_level": support,
            "explanation": _method_lane(stats_a, stats_b, prediction),
            "caution": "This is a scenario read, not a trained method-prop probability.",
        },
        {
            "id": "ko_tko_lean",
            "category": "ko_tko",
            "label": "KO/TKO lean",
            "fighter": name_a,
            "prop_style": f"{name_a} KO/TKO pressure is plausible if the striking exchanges stay clean.",
            "confidence": scenario_confidence,
            "support_level": "scenario_read",
            "explanation": _ko_path(stats_a, stats_b, style_a),
            "caution": "No exact KO/TKO probability is available yet.",
        },
        {
            "id": "submission_lean",
            "category": "submission",
            "label": "Submission lean",
            "fighter": name_b,
            "prop_style": f"{name_b} submission is live if grappling exchanges extend.",
            "confidence": scenario_confidence,
            "support_level": "scenario_read",
            "explanation": _submission_path(stats_b, stats_a, style_b),
            "caution": "No exact submission probability is available yet.",
        },
        {
            "id": "decision_finish_lean",
            "category": "decision_finish",
            "label": "Finish vs decision lean",
            "fighter": favorite["Name"],
            "prop_style": _decision_finish_prop_style(stats_a, stats_b, prediction),
            "confidence": scenario_confidence,
            "support_level": support,
            "explanation": _decision_finish_read(stats_a, stats_b, prediction),
            "caution": "The current model does not price exact method or goes-distance probabilities.",
        },
        {
            "id": "round_phase_finish",
            "category": "round_phase",
            "label": "Round-phase finish read",
            "round_window": "Rounds 2-3",
            "prop_style": "Middle-round finish pressure is plausible if the stronger repeatable offense starts stacking up.",
            "confidence": "low" if warnings else scenario_confidence,
            "support_level": "scenario_read",
            "explanation": _middle_round_read(stats_a, stats_b, favorite, underdog),
            "caution": "This is not a round prediction model.",
        },
        {
            "id": "strike_volume",
            "category": "volume",
            "label": "Clean-strike volume read",
            "prop_style": _volume_prop_style(stats_a, stats_b),
            "confidence": "low" if labels["data_quality"] != "Complete" else scenario_confidence,
            "support_level": "limited_data" if labels["data_quality"] != "Complete" else "model_informed_read",
            "explanation": _pace_volume_read(stats_a, stats_b),
            "caution": "The current model does not yet directly project exact strike totals.",
        },
        {
            "id": "grappling_control",
            "category": "grappling",
            "label": "Grappling/control-time read",
            "fighter": _grappling_side(stats_a, stats_b)["Name"],
            "prop_style": _grappling_prop_style(stats_a, stats_b),
            "confidence": "low" if labels["data_quality"] == "Limited" else scenario_confidence,
            "support_level": "scenario_read",
            "explanation": "This read uses available takedown tendency and matchup style only; it does not project control time.",
            "caution": "No dedicated takedown or control-time model is active yet.",
        },
        {
            "id": "fighter_a_best_path",
            "category": "fighter_path",
            "label": f"{name_a} best prop-style path",
            "fighter": name_a,
            "prop_style": _fighter_prop_path(stats_a, stats_b, style_a),
            "confidence": scenario_confidence,
            "support_level": "scenario_read",
            "explanation": _path_to_win(stats_a, stats_b, style_a),
            "caution": "Treat this as a path-to-victory read, not a hard prop projection.",
        },
        {
            "id": "fighter_b_best_path",
            "category": "fighter_path",
            "label": f"{name_b} best prop-style path",
            "fighter": name_b,
            "prop_style": _fighter_prop_path(stats_b, stats_a, style_b),
            "confidence": scenario_confidence,
            "support_level": "scenario_read",
            "explanation": _path_to_win(stats_b, stats_a, style_b),
            "caution": "Treat this as a path-to-victory read, not a hard prop projection.",
        },
        {
            "id": "volatility_prop_warning",
            "category": "warning",
            "label": "Volatility prop warning",
            "prop_style": _prop_warning_style(labels, warnings, matchup_type),
            "confidence": "low",
            "support_level": "limited_data" if warnings else "model_informed_read",
            "explanation": _volatility_prop_warning(labels, warnings),
            "caution": _matchup_prop_caution(matchup_type),
        },
    ]
    if _needs_pass_read(prediction, labels, warnings):
        prop_reads.insert(
            0,
            {
                "id": "no_strong_prop_read",
                "category": "pass",
                "label": "No strong prop-style read",
                "prop_style": "No strong prop-style read from the current model.",
                "confidence": "low",
                "support_level": "limited_data",
                "explanation": "Winner confidence, volatility, or data quality is too soft to force a confident prop angle.",
                "caution": "Passing on a prop-style interpretation is the cleaner read for this matchup.",
            },
        )
    return prop_reads


def _secondary_reads(stats_a, stats_b, comparison, prediction, labels, warnings):
    name_a, name_b = stats_a["Name"], stats_b["Name"]
    winner = prediction.get("winner") or "Too close to call"
    style_a = comparison.get("style1", {}).get("label", "balanced")
    style_b = comparison.get("style2", {}).get("label", "balanced")
    favorite = _favorite_stats(stats_a, stats_b, prediction)
    underdog = stats_b if favorite is stats_a else stats_a
    base_confidence = _read_confidence(prediction, labels, warnings)
    scenario_confidence = "medium" if base_confidence == "high" else "low"
    return [
        {
            "type": "method_lean",
            "label": "Most likely winning lane",
            "fighter": favorite["Name"] if winner != "Too close to call" else None,
            "read": _method_lane(stats_a, stats_b, prediction),
            "confidence": base_confidence,
            "explanation": "This is a method lean from winner probability, style, Elo, and available fighter metadata, not a dedicated finish-method model.",
        },
        {
            "type": "ko_tko_path",
            "label": f"KO/TKO path for {name_a}",
            "fighter": name_a,
            "read": _ko_path(stats_a, stats_b, style_a),
            "confidence": scenario_confidence,
            "explanation": "The model does not predict an exact KO/TKO probability; this describes the striking conditions that would make that lane more plausible.",
        },
        {
            "type": "submission_path",
            "label": f"Submission path for {name_b}",
            "fighter": name_b,
            "read": _submission_path(stats_b, stats_a, style_b),
            "confidence": scenario_confidence,
            "explanation": "The model does not predict an exact submission probability; this is a grappling scenario read from available tendencies.",
        },
        {
            "type": "round_phase",
            "label": "Middle-round outlook",
            "round_window": "Rounds 2-3",
            "read": _middle_round_read(stats_a, stats_b, favorite, underdog),
            "confidence": "medium" if labels["data_quality"] != "Limited" else "low",
            "explanation": "This is a round-phase outlook, not a round prediction model.",
        },
        {
            "type": "pace_volume",
            "label": "Pace and clean-strike read",
            "read": _pace_volume_read(stats_a, stats_b),
            "confidence": "medium" if labels["data_quality"] == "Complete" else "low",
            "explanation": "This uses relative pace and clean-striking indicators without projecting a count.",
        },
        {
            "type": "decision_finish",
            "label": "Decision vs finish lean",
            "read": _decision_finish_read(stats_a, stats_b, prediction),
            "confidence": scenario_confidence,
            "explanation": "This is a scenario projection. No dedicated round or finish model is being treated as certain.",
        },
        {
            "type": "key_exchange",
            "label": "Key exchange",
            "read": _key_exchanges(stats_a, stats_b),
            "confidence": "medium",
            "explanation": "The exchange read highlights where the matchup can change shape minute to minute.",
        },
        {
            "type": "danger_zone",
            "label": "Danger zone",
            "fighter": underdog["Name"],
            "read": f"{favorite['Name']} still has to manage {_danger(favorite, underdog)}; {underdog['Name']} can make the forecast unstable if that weakness shows up repeatedly.",
            "confidence": "low" if warnings else "medium",
            "explanation": "Danger zones are matchup risks, not certain finishing sequences.",
        },
        {
            "type": "uncertainty",
            "label": "Uncertainty warning",
            "read": _data_quality_note(labels, warnings),
            "confidence": "medium",
            "explanation": "The public model should be read with extra caution when data quality, cross-division context, or close probabilities increase volatility.",
        },
    ]


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


def _favorite_stats(stats_a, stats_b, prediction):
    winner = prediction.get("winner")
    if winner == stats_a["Name"]:
        return stats_a
    if winner == stats_b["Name"]:
        return stats_b
    return stats_a if float(prediction.get("prob_a") or 0.5) >= 0.5 else stats_b


def _read_confidence(prediction, labels, warnings):
    confidence = float(prediction.get("confidence") or 0.5)
    if confidence >= 0.66 and labels["data_quality"] != "Limited" and not warnings:
        return "high"
    if confidence >= 0.58 and labels["data_quality"] != "Limited":
        return "medium"
    return "low"


def _read_by_type(reads, read_type):
    return next((read for read in reads if read.get("type") == read_type), None)


def _prop_confidence(prediction, labels, warnings, matchup_type):
    confidence = _read_confidence(prediction, labels, warnings)
    if matchup_type["severity"] == "high" or labels["data_quality"] == "Limited":
        return "low"
    if matchup_type["severity"] == "soft" and confidence == "high":
        return "medium"
    return confidence


def _needs_pass_read(prediction, labels, warnings):
    confidence = float(prediction.get("confidence") or 0.5)
    return confidence < 0.57 or labels["data_quality"] == "Limited" or len(warnings) >= 3


def _method_prop_style(favorite, opponent, prediction):
    if prediction.get("winner") == "Too close to call":
        return "No clear fighter method lean from the current model."
    if _usable_number(favorite.get("TD Avg")) > _usable_number(opponent.get("TD Avg")) + 0.8:
        return f"{favorite['Name']} by decision or submission pressure is the cleaner prop-style angle."
    if _usable_number(favorite.get("SLpM")) > _usable_number(opponent.get("SLpM")) + 0.7:
        return f"{favorite['Name']} by decision or late TKO pressure is the cleaner prop-style angle."
    return f"{favorite['Name']} by decision is the cleaner read if the matchup stays technical."


def _decision_finish_prop_style(stats_a, stats_b, prediction):
    favorite = _favorite_stats(stats_a, stats_b, prediction)
    opponent = stats_b if favorite is stats_a else stats_a
    if float(prediction.get("confidence") or 0.5) < 0.57:
        return "Finish vs decision is too volatile for a strong prop-style lean."
    if _usable_number(favorite.get("TD Avg")) > 1.5 or _usable_number(favorite.get("SLpM")) > _usable_number(opponent.get("SLpM")) + 1.0:
        return f"Finish pressure is plausible if {favorite['Name']} turns repeated advantages into damage or dominant positions."
    return "Fight goes distance is the cleaner lean if both fighters stay disciplined and the pace remains technical."


def _volume_prop_style(stats_a, stats_b):
    slpm_a = _usable_number(stats_a.get("SLpM"))
    slpm_b = _usable_number(stats_b.get("SLpM"))
    if max(slpm_a, slpm_b) <= 0:
        return "No strong clean-strike volume read from the current data."
    if abs(slpm_a - slpm_b) < 0.5:
        return "A steady striking pace is plausible, but neither side has a clear volume edge."
    leader = stats_a if slpm_a > slpm_b else stats_b
    return f"A higher-volume striking fight is plausible if {leader['Name']} keeps the matchup standing."


def _grappling_side(stats_a, stats_b):
    return stats_a if _usable_number(stats_a.get("TD Avg")) >= _usable_number(stats_b.get("TD Avg")) else stats_b


def _grappling_prop_style(stats_a, stats_b):
    grappler = _grappling_side(stats_a, stats_b)
    other = stats_b if grappler is stats_a else stats_a
    if _usable_number(grappler.get("TD Avg")) <= 0:
        return "No strong grappling/control prop-style read from the current data."
    if _usable_number(grappler.get("TD Avg")) > _usable_number(other.get("TD Avg")) + 0.8:
        return f"{grappler['Name']} control pressure is plausible if level changes become repeatable."
    return "Grappling/control pressure is possible, but the current data does not show a dominant control lean."


def _fighter_prop_path(stats_self, stats_opp, style):
    name = stats_self["Name"]
    if style == "grappler-leaning" or _usable_number(stats_self.get("TD Avg")) > _usable_number(stats_opp.get("TD Avg")) + 0.8:
        return f"{name} submission or decision-control is the plausible fighter-specific prop-style path."
    if style == "striker-leaning" or _usable_number(stats_self.get("SLpM")) > _usable_number(stats_opp.get("SLpM")) + 0.7:
        return f"{name} decision or late TKO pressure is the plausible fighter-specific prop-style path."
    return f"{name} by decision is the cleaner fighter-specific angle if the fight stays balanced."


def _prop_warning_style(labels, warnings, matchup_type):
    if matchup_type["label"] == "Cross-division matchup":
        return "Cross-division matchup: prop-style reads are less reliable."
    if matchup_type["label"] == "Potential cross-division matchup":
        return "Potential cross-division matchup: prop-style reads should be treated cautiously."
    if matchup_type["label"] == "Weight-class data incomplete":
        return "Weight-class data incomplete. Prop-style reads may be less reliable."
    if labels["volatility"] == "High":
        return "High-chaos matchup: avoid forcing a strong prop-style read."
    if warnings:
        return warnings[0]
    return "Same-division matchup with normal prop-read caution."


def _matchup_prop_caution(matchup_type):
    if matchup_type["label"] == "Cross-division matchup":
        return "Cross-division matchup: prop-style reads are less reliable."
    if matchup_type["label"] == "Weight-class data incomplete":
        return "Weight-class data incomplete. Prop-style reads may be less reliable."
    return "This should be treated as scenario analysis, not a hard projection."


def _volatility_prop_warning(labels, warnings):
    if warnings:
        return " ".join(_sentence(warning) for warning in warnings)
    return f"Volatility is {labels['volatility'].lower()}; prop-style reads still need caution because the current model does not price exact props."


def _prop_section_read(prop_reads):
    strong = next((read for read in prop_reads if read["category"] != "warning" and read["confidence"] == "medium"), None)
    if not strong:
        strong = next((read for read in prop_reads if read["category"] == "pass"), None)
    if strong:
        return f"{strong['prop_style']} {strong['caution']}"
    return "No strong prop-style read from the current model. The safer interpretation is to use the reads as scenario analysis."


def _method_lane(stats_a, stats_b, prediction) -> str:
    favorite = _favorite_stats(stats_a, stats_b, prediction)
    opponent = stats_b if favorite is stats_a else stats_a
    if prediction.get("winner") == "Too close to call":
        return (
            f"The method lean is narrow rather than decisive: {stats_a['Name']} has to win repeatable exchanges, "
            f"while {stats_b['Name']} needs to deny rhythm and create momentum swings."
        )
    if _usable_number(favorite.get("TD Avg")) > _usable_number(opponent.get("TD Avg")) + 0.8:
        return f"The clearest lane for {favorite['Name']} is mixed offense: enough striking to make level changes credible, then control sequences that bank minutes or create submission threats."
    if _usable_number(favorite.get("SLpM")) > _usable_number(opponent.get("SLpM")) + 0.7:
        return f"The clearest lane for {favorite['Name']} is clean volume: land first, exit before counters, and turn repeated striking exchanges into a scorecard gap or late damage."
    if favorite.get("Elo Available") and opponent.get("Elo Available") and favorite["Elo"] > opponent["Elo"] + 40:
        return f"The clearest lane for {favorite['Name']} is a composed decision-style fight: keep the matchup orderly, avoid risky scrambles, and let proven form show over time."
    return f"The method lean for {favorite['Name']} is control of the middle: win enough clean exchanges, avoid extended defensive stretches, and stay disciplined if the finish does not appear."


def _ko_path(stats_self, stats_opp, style: str) -> str:
    name = stats_self["Name"]
    opponent = stats_opp["Name"]
    if style == "striker-leaning" or _usable_number(stats_self.get("SLpM")) > _usable_number(stats_opp.get("SLpM")) + 0.8:
        return f"{name}'s KO/TKO scenario is built around first-touch offense: make {opponent} react at range, stack clean strikes, and punish rushed entries."
    if _usable_number(stats_self.get("Reach (cm)")) > _usable_number(stats_opp.get("Reach (cm)")) + 5:
        return f"{name}'s KO/TKO scenario is distance control: keep {opponent} at the end of straight shots, then attack when forced entries become predictable."
    return f"{name}'s KO/TKO scenario likely comes from a transition moment rather than pure volume: a counter during an entry, a clinch break, or damage after a scramble."


def _submission_path(stats_self, stats_opp, style: str) -> str:
    name = stats_self["Name"]
    opponent = stats_opp["Name"]
    if style == "grappler-leaning" or _usable_number(stats_self.get("Sub Avg")) > _usable_number(stats_opp.get("Sub Avg")) + 0.3:
        return f"{name}'s submission scenario is to make {opponent} defend in layers: level change, mat return, forced scramble, then attack the neck or an exposed limb."
    if _usable_number(stats_self.get("TD Avg")) > _usable_number(stats_opp.get("TD Avg")) + 0.8:
        return f"{name}'s submission scenario starts with wrestling control. If {opponent} gives up a back take or posts hard to stand, the grappling read gets live."
    return f"{name}'s submission scenario is opportunistic: survive the first wave, force a messy exchange, and turn a defensive scramble into top control or back exposure."


def _middle_round_read(stats_a, stats_b, favorite, underdog) -> str:
    if _usable_number(favorite.get("TD Avg")) > _usable_number(underdog.get("TD Avg")) + 0.8:
        return f"Rounds 2-3 are where {favorite['Name']} can make wrestling accumulation matter. If the first entries force reactions, the middle phase could open control time or a submission look."
    if _usable_number(underdog.get("SLpM")) > _usable_number(favorite.get("SLpM")) + 0.6:
        return f"Rounds 2-3 are the danger window for the model favorite. {underdog['Name']} can narrow the read if pace starts piling up before {favorite['Name']} settles the exchanges."
    return f"Rounds 2-3 should test adjustments more than raw explosiveness. The fighter who keeps their preferred range after the first reads are shown is likely to own the cleaner minutes."


def _pace_volume_read(stats_a, stats_b) -> str:
    slpm_a = _usable_number(stats_a.get("SLpM"))
    slpm_b = _usable_number(stats_b.get("SLpM"))
    sapm_a = _usable_number(stats_a.get("SApM"))
    sapm_b = _usable_number(stats_b.get("SApM"))
    if slpm_a > slpm_b + 0.7:
        return f"{stats_a['Name']} profiles as the cleaner volume side if the fight stays at range, but that only matters if defensive exits keep {stats_b['Name']} from answering back."
    if slpm_b > slpm_a + 0.7:
        return f"{stats_b['Name']} profiles as the cleaner volume side if the fight stays at range, but the read softens if {stats_a['Name']} disrupts rhythm with clinches or level changes."
    if sapm_a and sapm_b and abs(sapm_a - sapm_b) > 0.7:
        sturdier = stats_a if sapm_a < sapm_b else stats_b
        return f"The pace read is less about raw output and more about who absorbs fewer clean looks. Available defense data gives {sturdier['Name']} a slightly cleaner minute-winning lane."
    return "The pace/volume read is close. Neither side should be treated as having a clear volume projection, so clean entries and defensive resets matter more than raw output."


def _decision_finish_read(stats_a, stats_b, prediction) -> str:
    favorite = _favorite_stats(stats_a, stats_b, prediction)
    opponent = stats_b if favorite is stats_a else stats_a
    if float(prediction.get("confidence") or 0.5) < 0.57:
        return "Because the winner probability is close, the decision-vs-finish lean is volatile. A competitive decision and a sudden momentum-changing finish both remain plausible scenarios."
    if _usable_number(favorite.get("TD Avg")) > 1.5 or _usable_number(favorite.get("SLpM")) > _usable_number(opponent.get("SLpM")) + 1.0:
        return f"The finish scenario is more live if {favorite['Name']} can turn repeated advantages into damage or dominant positions, but the model is still not calling an exact method."
    return f"The cleaner projection is a decision-leaning fight for {favorite['Name']}: win rounds through repeatable exchanges, while staying alert to counters and scrambles that could change the result."


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


def _warnings(stats_a, stats_b, confidence, matchup_type):
    warnings = []
    if matchup_type["severity"] != "none":
        warnings.append(matchup_type["explanation"])
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


def _matchup_type(stats_a, stats_b):
    class_a = _weight_class_value(stats_a)
    class_b = _weight_class_value(stats_b)
    if _missing_weight_class(class_a) or _missing_weight_class(class_b):
        return {
            "label": "Weight-class data incomplete",
            "severity": "soft",
            "explanation": "One or both fighters are missing reliable weight-class data, so confidence may be lower.",
        }
    normalized_a = _normalize_weight_class(class_a)
    normalized_b = _normalize_weight_class(class_b)
    if normalized_a == normalized_b:
        return {
            "label": "Same-division matchup",
            "severity": "none",
            "explanation": "Both fighters are listed in the same division.",
        }
    index_a = WEIGHT_CLASS_ORDER.get(normalized_a)
    index_b = WEIGHT_CLASS_ORDER.get(normalized_b)
    if index_a is None or index_b is None or abs(index_a - index_b) <= 1:
        return {
            "label": "Potential cross-division matchup",
            "severity": "soft",
            "explanation": "These fighters are listed near different or uncertain divisions, so the model may be less confident.",
        }
    return {
        "label": "Cross-division matchup",
        "severity": "high",
        "explanation": "These fighters are listed in different divisions. The prediction is still shown, but matchup realism and confidence may be lower.",
    }


def _same_weight_class(stats_a, stats_b):
    matchup = _matchup_type(stats_a, stats_b)
    return matchup["severity"] in {"none", "soft"} and matchup["label"] != "Potential cross-division matchup"


def _weight_class_value(stats):
    return stats.get("Weight Class") or stats.get("weight_class") or stats.get("Division") or stats.get("division")


def _missing_weight_class(value) -> bool:
    return not value or str(value).strip().lower() in {"unknown", "n/a", "na", "none", "null"}


def _normalize_weight_class(value) -> str:
    normalized = str(value or "").strip().lower()
    for prefix in ("women's ", "womens ", "women "):
        if normalized.startswith(prefix):
            normalized = normalized.removeprefix(prefix)
    return normalized


def _weight_class_label(stats):
    value = _weight_class_value(stats)
    return "Unknown" if _missing_weight_class(value) else str(value)


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
