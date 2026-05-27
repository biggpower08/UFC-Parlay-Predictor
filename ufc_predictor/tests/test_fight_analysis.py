from ufc_predictor.analysis import build_fight_analysis
from ufc_predictor.config import settings


def _stats(name, elo=1100, weight_class="Lightweight", slpm=4.0, td_avg=1.2):
    return {
        "Name": name,
        "Record": "10W-2L",
        "Elo": elo,
        "Elo Available": True,
        "Elo Source": "computed",
        "Elo Fights": 10,
        "Weight Class": weight_class,
        "SLpM": slpm,
        "SApM": 3.0,
        "TD Avg": td_avg,
        "TD Def %": 70,
        "Reach (cm)": 180,
        "Height (cm)": 178,
        "Stance": "Orthodox",
        "Sub Avg": 0.4,
    }


def test_fallback_analysis_shape_without_ai_provider():
    settings.ENABLE_AI_SUMMARY = False
    comparison = {
        "stats1": _stats("Alpha Fighter", elo=1200),
        "stats2": _stats("Beta Fighter", elo=1000),
        "style1": {"label": "balanced"},
        "style2": {"label": "striker-leaning"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.66, "prob_a": 0.66}

    analysis = build_fight_analysis(comparison, prediction)

    assert analysis["provider"] == "deterministic_fallback"
    assert analysis["confidence_label"] == "High Confidence"
    assert analysis["summary"]
    assert len(analysis["sections"]) >= 8
    assert analysis["drivers"]
    assert "guaranteed" not in analysis["summary"].lower()


def test_cross_division_warning_and_volatility():
    comparison = {
        "stats1": _stats("Alpha Fighter", weight_class="Lightweight"),
        "stats2": _stats("Heavy Fighter", weight_class="Heavyweight"),
        "style1": {"label": "balanced"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Heavy Fighter.",
    }
    prediction = {"winner": "Too close to call", "confidence": 0.53, "prob_a": 0.53}

    analysis = build_fight_analysis(comparison, prediction)

    assert analysis["volatility_label"] == "High"
    assert any("Cross-division" in warning for warning in analysis["warnings"])
    assert analysis["confidence_label"] == "Low Confidence"


def test_missing_data_does_not_invent_stats():
    limited = _stats("Limited Fighter")
    limited.update({"Elo Available": False, "Elo": 1000, "SLpM": 0, "TD Avg": 0, "Reach (cm)": 0, "Stance": "N/A"})
    comparison = {
        "stats1": limited,
        "stats2": _stats("Known Fighter"),
        "style1": {"label": "balanced"},
        "style2": {"label": "balanced"},
        "matchup": "Limited Fighter vs Known Fighter.",
    }
    prediction = {"winner": "Known Fighter", "confidence": 0.6, "prob_a": 0.4}

    analysis = build_fight_analysis(comparison, prediction)

    assert analysis["data_quality_label"] in {"Partial", "Limited"}
    assert any("limited" in warning.lower() for warning in analysis["warnings"])
    assert "not a guarantee" in analysis["summary"].lower()
