"""Weighted winner ensemble for sklearn, Elo, and optional private analyst."""

from ufc_predictor.config import settings
from ufc_predictor.models.elo.elo_engine import expected_score
from ufc_predictor.models.llm.ollama_analyst import analyze_matchup
from ufc_predictor.models.sklearn.predictor import explain_top_features, predict_matchup


def predict_ensemble(f1, f2, comparison: dict) -> dict:
    stats1, stats2 = comparison["stats1"], comparison["stats2"]
    name1, name2 = stats1["Name"], stats2["Name"]
    elo_prob = expected_score(stats1["Elo"], stats2["Elo"])

    signals = {}
    sklearn_prediction = predict_matchup(f1, f2) if settings.USE_SKLEARN_MODEL else None
    if sklearn_prediction is not None:
        signals["sklearn"] = {
            "prob_a": sklearn_prediction["prob_a_wins"],
            "available": True,
            "top_features": explain_top_features(sklearn_prediction, 3),
        }

    if settings.USE_ELO_FALLBACK:
        signals["elo"] = {"prob_a": elo_prob, "available": True}

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

    prob_a = _weighted_probability(signals)
    winner = _winner_from_probability(prob_a, name1, name2)

    if _is_sklearn_close(signals) and signals.get("llm", {}).get("available"):
        winner = signals["llm"]["winner"]
        prob_a = signals["llm"]["prob_a"]

    confidence = max(prob_a, 1 - prob_a)
    return {
        "winner": winner,
        "confidence": confidence,
        "prob_a": prob_a,
        "prob_b": 1 - prob_a,
        "model": "ensemble",
        "signals": signals,
        "reasoning": _reasoning(name1, name2, prob_a, elo_prob, signals, comparison),
    }


def _weighted_probability(signals: dict) -> float:
    total_weight = 0.0
    total = 0.0
    for key, signal in signals.items():
        weight = settings.ENSEMBLE_WEIGHTS.get(key, 0)
        if not signal.get("available"):
            continue
        total_weight += weight
        total += weight * float(signal["prob_a"])
    if total_weight == 0:
        return 0.5
    return min(0.99, max(0.01, total / total_weight))


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
    parts.append(f"Elo signal {elo_prob:.0%}.")
    if signals.get("llm", {}).get("available"):
        parts.append(f"Analyst signal: {signals['llm']['reasoning']}")
    else:
        parts.append("Decision used the statistical model and Elo signals.")
    parts.append(comparison["matchup"])
    return " ".join(parts)
