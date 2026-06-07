"""Weighted winner ensemble for sklearn, Elo, and optional private analyst."""

from ufc_predictor.config import settings
from ufc_predictor.models.elo.elo_engine import expected_score
from ufc_predictor.models.llm.ollama_analyst import analyze_matchup
from ufc_predictor.models.props.predictor import predict_supported_prop_models
from ufc_predictor.models.sklearn.predictor import explain_top_features, predict_matchup
from ufc_predictor.utils.logger import get_logger


logger = get_logger(__name__)


def predict_ensemble(f1, f2, comparison: dict) -> dict:
    stats1, stats2 = comparison["stats1"], comparison["stats2"]
    name1, name2 = stats1["Name"], stats2["Name"]
    elo_prob = expected_score(stats1["Elo"], stats2["Elo"])
    elo_available = bool(stats1.get("Elo Available") and stats2.get("Elo Available"))
    elo_diagnostics = {
        "fighter_a_elo": stats1["Elo"],
        "fighter_b_elo": stats2["Elo"],
        "fighter_a_elo_available": bool(stats1.get("Elo Available")),
        "fighter_b_elo_available": bool(stats2.get("Elo Available")),
        "fighter_a_elo_source": stats1.get("Elo Source"),
        "fighter_b_elo_source": stats2.get("Elo Source"),
        "fighter_a_elo_fights": stats1.get("Elo Fights"),
        "fighter_b_elo_fights": stats2.get("Elo Fights"),
        "delta_elo": stats1["Elo"] - stats2["Elo"],
        "elo_expected_a": elo_prob,
        "ensemble_elo_available": elo_available,
    }

    signals = {}
    sklearn_prediction = predict_matchup(f1, f2) if settings.USE_SKLEARN_MODEL else None
    if sklearn_prediction is not None:
        signals["sklearn"] = {
            "prob_a": sklearn_prediction["prob_a_wins"],
            "available": True,
            "top_features": explain_top_features(sklearn_prediction, 3),
            "diagnostics": sklearn_prediction.get("diagnostics"),
        }

    if settings.USE_ELO_FALLBACK:
        signals["elo"] = {"prob_a": elo_prob, "available": elo_available}

    if settings.USE_LLM_ANALYST:
        llm = analyze_matchup(
            stats1,
            stats2,
            comparison,
            signals.get("sklearn", {}).get("prob_a"),
            elo_prob,
        )
        if llm.get("available"):
            llm_prob = _winner_to_prob(llm["winner"], name1, name2, llm["confidence"])
            signals["llm"] = {"prob_a": llm_prob, **llm}

    prop_model_predictions = predict_supported_prop_models(stats1, stats2)
    supporting_signals = _supporting_model_signals(prop_model_predictions, stats1, stats2)
    for key, signal in supporting_signals.items():
        if signal.get("available") and signal.get("use_in_score"):
            signals[key] = signal

    prob_a = _weighted_probability(signals)
    winner = _winner_from_probability(prob_a, name1, name2)

    if _is_sklearn_close(signals) and signals.get("llm", {}).get("available"):
        winner = signals["llm"]["winner"]
        prob_a = signals["llm"]["prob_a"]

    confidence = max(prob_a, 1 - prob_a)
    ensemble_breakdown = _ensemble_breakdown(
        signals=signals,
        prop_model_predictions=prop_model_predictions,
        prob_a=prob_a,
        confidence=confidence,
        elo_diagnostics=elo_diagnostics,
        sklearn_prediction=sklearn_prediction,
        comparison=comparison,
    )
    diagnostics = {
        "elo": elo_diagnostics,
        "sklearn": (signals.get("sklearn") or {}).get("diagnostics"),
        "ensemble_weights": settings.ENSEMBLE_WEIGHTS,
        "available_signals": [key for key, signal in signals.items() if signal.get("available")],
        "prop_model_predictions": prop_model_predictions,
    }
    logger.info(
        "prediction_elo_diagnostics fighter_a=%s fighter_b=%s elo_a=%s elo_b=%s delta_elo=%s "
        "elo_available=%s sklearn_elo_features=%s available_signals=%s",
        name1,
        name2,
        elo_diagnostics["fighter_a_elo"],
        elo_diagnostics["fighter_b_elo"],
        elo_diagnostics["delta_elo"],
        elo_available,
        diagnostics["sklearn"].get("elo_features_present") if diagnostics["sklearn"] else None,
        diagnostics["available_signals"],
    )
    return {
        "winner": winner,
        "confidence": confidence,
        "prob_a": prob_a,
        "prob_b": 1 - prob_a,
        "model": "ensemble",
        "signals": signals,
        "ensemble_breakdown": ensemble_breakdown,
        "diagnostics": diagnostics,
        "reasoning": _reasoning(name1, name2, prob_a, elo_prob, signals, comparison),
    }


def _weighted_probability(signals: dict) -> float:
    total_weight = 0.0
    total = 0.0
    for key, signal in signals.items():
        weight = float(signal.get("weight", settings.ENSEMBLE_WEIGHTS.get(key, 0)))
        if not signal.get("available"):
            continue
        total_weight += weight
        total += weight * float(signal["prob_a"])
    if total_weight == 0:
        return 0.5
    return min(0.99, max(0.01, total / total_weight))


def _supporting_model_signals(prop_predictions: dict, stats1: dict, stats2: dict) -> dict:
    signals = {}
    strike = prop_predictions.get("strike_volume_model", {})
    if strike.get("status") == "trained" and strike.get("label"):
        style_prob = _style_signal_probability(stats1, stats2, "SLpM")
        signals["strike_volume"] = _scoring_signal(
            "strike_volume_model",
            style_prob,
            0.03,
            "trained",
            f"Strike-volume model context: {strike.get('label')}.",
        )
    grappling = prop_predictions.get("takedown_control_model", {})
    if grappling.get("status") == "trained" and grappling.get("label"):
        style_prob = _style_signal_probability(stats1, stats2, "TD Avg")
        signals["takedown_control"] = _scoring_signal(
            "takedown_control_model",
            style_prob,
            0.03,
            "trained",
            f"Takedown/control model context: {grappling.get('label')}.",
        )
    return signals


def _scoring_signal(model_name: str, prob_a: float, weight: float, status: str, message: str) -> dict:
    return {
        "prob_a": min(0.62, max(0.38, float(prob_a))),
        "weight": weight,
        "available": True,
        "use_in_score": True,
        "model_name": model_name,
        "status": status,
        "message": message,
    }


def _style_signal_probability(stats1: dict, stats2: dict, key: str) -> float:
    value_a = _safe_float(stats1.get(key))
    value_b = _safe_float(stats2.get(key))
    diff = value_a - value_b
    return 0.5 + max(-0.08, min(0.08, diff * 0.03))


def _safe_float(value) -> float:
    try:
        number = float(value or 0.0)
    except (TypeError, ValueError):
        return 0.0
    return number if number == number else 0.0


def _ensemble_breakdown(
    signals: dict,
    prop_model_predictions: dict,
    prob_a: float,
    confidence: float,
    elo_diagnostics: dict,
    sklearn_prediction: dict | None,
    comparison: dict,
) -> dict:
    unavailable = []
    breakdown = {
        "winner_model_signal": _winner_signal(signals.get("sklearn"), sklearn_prediction),
        "elo_signal": _elo_signal(signals.get("elo"), elo_diagnostics),
        "finish_model_signal": _context_signal("finish_model", prop_model_predictions, unavailable),
        "method_model_signal": _context_signal("method_model", prop_model_predictions, unavailable),
        "round_model_signal": _context_signal("round_model", prop_model_predictions, unavailable),
        "strike_volume_signal": _context_signal("strike_volume_model", prop_model_predictions, unavailable, signals.get("strike_volume")),
        "takedown_control_signal": _context_signal("takedown_control_model", prop_model_predictions, unavailable, signals.get("takedown_control")),
        "odds_calibration_signal": {
            "available": False,
            "status": "blocked",
            "used_in_score": False,
            "message": "Historical odds calibration is not available yet.",
        },
        "final_probability": round(float(prob_a), 4),
        "confidence": round(float(confidence), 4),
        "data_quality": _ensemble_data_quality(signals, comparison),
        "unavailable_models": unavailable,
    }
    if not breakdown["odds_calibration_signal"]["available"]:
        unavailable.append("odds_calibration_model")
    return breakdown


def _winner_signal(signal: dict | None, sklearn_prediction: dict | None) -> dict:
    if not signal:
        return {
            "available": False,
            "status": "not_available",
            "used_in_score": False,
            "message": "Winner model is unavailable; prediction falls back to available signals.",
        }
    return {
        "available": True,
        "status": "trained",
        "used_in_score": True,
        "probability_fighter_a": round(float(signal["prob_a"]), 4),
        "message": "Primary learned winner signal is available.",
        "top_features": signal.get("top_features") or [],
        "diagnostics_available": bool(sklearn_prediction and sklearn_prediction.get("diagnostics")),
    }


def _elo_signal(signal: dict | None, elo_diagnostics: dict) -> dict:
    return {
        "available": bool(signal and signal.get("available")),
        "status": "computed" if signal and signal.get("available") else "limited",
        "used_in_score": bool(signal and signal.get("available")),
        "probability_fighter_a": round(float(signal["prob_a"]), 4) if signal and signal.get("available") else None,
        "message": "Elo is included because both fighters have computed Elo." if signal and signal.get("available") else "Elo is limited because one or both fighters only have baseline Elo.",
        "fighter_a_elo_available": elo_diagnostics.get("fighter_a_elo_available"),
        "fighter_b_elo_available": elo_diagnostics.get("fighter_b_elo_available"),
    }


def _context_signal(model_name: str, prop_predictions: dict, unavailable: list[str], scoring_signal: dict | None = None) -> dict:
    prediction = prop_predictions.get(model_name) or {}
    status = prediction.get("status") or "not_trained"
    available = status in {"trained", "experimental"} and bool(prediction.get("label"))
    used_in_score = bool(scoring_signal and scoring_signal.get("use_in_score") and status == "trained")
    if not available:
        unavailable.append(model_name)
    return {
        "available": available,
        "status": status,
        "used_in_score": used_in_score,
        "probability_fighter_a": round(float(scoring_signal["prob_a"]), 4) if used_in_score else None,
        "label": prediction.get("label"),
        "confidence": prediction.get("confidence"),
        "message": _context_message(model_name, status, available, used_in_score),
    }


def _context_message(model_name: str, status: str, available: bool, used_in_score: bool) -> str:
    if used_in_score:
        return f"{model_name} is trained and used as a small supporting style signal."
    if available and status == "trained":
        return f"{model_name} is trained and informs confidence or analysis text, not winner direction."
    if available and status == "experimental":
        return f"{model_name} is experimental and used only for labeled scenario context."
    return f"{model_name} is unavailable for this matchup or not trained."


def _ensemble_data_quality(signals: dict, comparison: dict) -> str:
    if not signals.get("sklearn") and not signals.get("elo", {}).get("available"):
        return "limited"
    warnings = comparison.get("warnings") or []
    return "caution" if warnings else "usable"


def _winner_to_prob(winner: str, name1: str, name2: str, confidence: float) -> float:
    if winner == name1:
        return confidence
    if winner == name2:
        return 1 - confidence
    return 0.5


def _winner_from_probability(prob_a: float, name1: str, name2: str) -> str:
    if abs(prob_a - 0.5) < settings.CLOSE_CALL_PROB_THRESHOLD:
        return "Too close to call"
    return name1 if prob_a > 0.5 else name2


def _is_sklearn_close(signals: dict) -> bool:
    sklearn = signals.get("sklearn")
    return bool(sklearn) and abs(float(sklearn["prob_a"]) - 0.5) < settings.CLOSE_CALL_PROB_THRESHOLD


def _reasoning(name1, name2, prob_a, elo_prob, signals, comparison) -> str:
    parts = [f"Ensemble: {name1} {prob_a:.0%} vs {name2} {1 - prob_a:.0%}."]
    if "sklearn" in signals:
        top = signals["sklearn"].get("top_features") or []
        contrib = ", ".join(f"{n} ({v:+.2f})" for n, v in top) if top else "mixed features"
        parts.append(f"Sklearn signal {signals['sklearn']['prob_a']:.0%}; drivers: {contrib}.")
    if signals.get("elo", {}).get("available"):
        parts.append(f"Elo signal {elo_prob:.0%}.")
    else:
        parts.append("Elo signal unavailable; using starting baseline only.")
    if signals.get("llm", {}).get("available"):
        parts.append(f"Analyst signal: {signals['llm']['reasoning']}")
    else:
        parts.append("Decision used the statistical model and Elo signals.")
    parts.append(comparison["matchup"])
    return " ".join(parts)
