from difflib import SequenceMatcher

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
    assert analysis["matchup_type"]["label"] == "Same-division matchup"
    assert analysis["secondary_reads"]
    assert analysis["prop_reads"]
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
    assert analysis["matchup_type"]["label"] == "Cross-division matchup"
    assert analysis["matchup_type"]["severity"] == "high"
    assert any("different divisions" in warning for warning in analysis["warnings"])
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
    assert "not a certainty" in analysis["summary"].lower()


def test_section_titles_are_unique_and_bodies_are_distinct():
    comparison = {
        "stats1": _stats("Alpha Fighter", elo=1180, slpm=5.1, td_avg=0.4),
        "stats2": _stats("Beta Fighter", elo=1080, slpm=3.2, td_avg=2.1),
        "style1": {"label": "striker-leaning"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.63, "prob_a": 0.63}

    analysis = build_fight_analysis(comparison, prediction)
    titles = [section["title"] for section in analysis["sections"]]
    bodies = [section["body"] for section in analysis["sections"]]

    assert titles == [
        "Main prediction read",
        "Method lean",
        "Alpha Fighter path to victory",
        "Beta Fighter path to victory",
        "Prop-style angles",
        "Early fight phase",
        "Middle fight phase",
        "Late fight phase",
        "Key exchanges",
        "Pace and volume read",
        "Volatility warning",
        "Data quality note",
        "Final analyst read",
    ]
    assert len(titles) == len(set(titles))
    for left_index, left in enumerate(bodies):
        for right in bodies[left_index + 1 :]:
            assert SequenceMatcher(None, left, right).ratio() < 0.82


def test_same_adjacent_and_missing_weight_class_metadata():
    same = {
        "stats1": _stats("Alpha Fighter", weight_class="Lightweight"),
        "stats2": _stats("Beta Fighter", weight_class="Lightweight"),
        "style1": {"label": "balanced"},
        "style2": {"label": "balanced"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    adjacent = {
        **same,
        "stats2": _stats("Welter Fighter", weight_class="Welterweight"),
    }
    missing = {
        **same,
        "stats2": _stats("Unknown Fighter", weight_class="Unknown"),
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.61, "prob_a": 0.61}

    assert build_fight_analysis(same, prediction)["matchup_type"] == {
        "label": "Same-division matchup",
        "severity": "none",
        "explanation": "Both fighters are listed in the same division.",
    }
    adjacent_meta = build_fight_analysis(adjacent, prediction)["matchup_type"]
    assert adjacent_meta["label"] == "Potential cross-division matchup"
    assert adjacent_meta["severity"] == "soft"
    missing_meta = build_fight_analysis(missing, prediction)["matchup_type"]
    assert missing_meta["label"] == "Weight-class data incomplete"
    assert missing_meta["severity"] == "soft"


def test_secondary_reads_avoid_unsupported_exact_claims():
    comparison = {
        "stats1": _stats("Alpha Fighter", slpm=5.2, td_avg=0.2),
        "stats2": _stats("Beta Fighter", slpm=3.1, td_avg=2.4),
        "style1": {"label": "striker-leaning"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.64, "prob_a": 0.64}

    analysis = build_fight_analysis(comparison, prediction)
    reads = analysis["secondary_reads"]
    combined = " ".join(
        f"{read.get('label', '')} {read.get('read', '')} {read.get('explanation', '')}" for read in reads
    ).lower()

    assert {read["type"] for read in reads} >= {
        "method_lean",
        "ko_tko_path",
        "submission_path",
        "round_phase",
        "pace_volume",
    }
    assert "prop" not in combined
    assert "%" not in combined
    assert "strike total" not in combined
    assert "guarantee" not in combined


def test_prop_reads_have_required_fields_and_support_levels():
    comparison = {
        "stats1": _stats("Alpha Fighter", slpm=5.2, td_avg=0.2),
        "stats2": _stats("Beta Fighter", slpm=3.1, td_avg=2.4),
        "style1": {"label": "striker-leaning"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.64, "prob_a": 0.64}

    analysis = build_fight_analysis(comparison, prediction)
    reads = analysis["prop_reads"]

    assert reads
    assert {read["category"] for read in reads} >= {
        "method",
        "ko_tko",
        "submission",
        "decision_finish",
        "round_phase",
        "volume",
        "grappling",
        "fighter_path",
        "warning",
    }
    for read in reads:
        assert read["id"]
        assert read["category"]
        assert read["label"]
        assert read["prop_style"]
        assert read["confidence"] in {"low", "medium", "high"}
        assert read["support_level"] in {
            "model_supported",
            "model_informed_read",
            "scenario_read",
            "limited_data",
            "not_available",
        }
        assert read["support_level"] != "model_supported"
        assert read["explanation"]
        assert read["caution"]


def test_prop_reads_do_not_generate_unsupported_or_hype_claims():
    comparison = {
        "stats1": _stats("Alpha Fighter", slpm=5.2, td_avg=0.2),
        "stats2": _stats("Beta Fighter", slpm=3.1, td_avg=2.4),
        "style1": {"label": "striker-leaning"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.64, "prob_a": 0.64}

    analysis = build_fight_analysis(comparison, prediction)
    combined = " ".join(
        f"{read.get('label', '')} {read.get('prop_style', '')} {read.get('explanation', '')} {read.get('caution', '')}"
        for read in analysis["prop_reads"]
    ).lower()

    for forbidden in ["will hit", "guaranteed", "lock", "free money", "place bet", "value bet", "units", "roi"]:
        assert forbidden not in combined
    assert "%" not in combined
    assert "projected over" not in combined


def test_cross_division_prop_reads_are_lower_confidence_and_warn():
    comparison = {
        "stats1": _stats("Alpha Fighter", weight_class="Lightweight", slpm=5.2),
        "stats2": _stats("Heavy Fighter", weight_class="Heavyweight", td_avg=2.4),
        "style1": {"label": "striker-leaning"},
        "style2": {"label": "grappler-leaning"},
        "matchup": "Alpha Fighter vs Heavy Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.68, "prob_a": 0.68}

    analysis = build_fight_analysis(comparison, prediction)
    reads = analysis["prop_reads"]
    warning = next(read for read in reads if read["id"] == "volatility_prop_warning")

    assert all(read["confidence"] in {"low", "medium"} for read in reads)
    assert any(read["confidence"] == "low" for read in reads)
    assert "Cross-division matchup: prop-style reads are less reliable." in warning["prop_style"]


def test_same_division_prop_reads_do_not_show_cross_division_warning():
    comparison = {
        "stats1": _stats("Alpha Fighter", weight_class="Lightweight"),
        "stats2": _stats("Beta Fighter", weight_class="Lightweight"),
        "style1": {"label": "balanced"},
        "style2": {"label": "balanced"},
        "matchup": "Alpha Fighter vs Beta Fighter.",
    }
    prediction = {"winner": "Alpha Fighter", "confidence": 0.62, "prob_a": 0.62}

    analysis = build_fight_analysis(comparison, prediction)
    combined = " ".join(read["prop_style"] for read in analysis["prop_reads"])

    assert "Cross-division" not in combined


def test_missing_data_prop_reads_include_caution_or_pass_read():
    limited = _stats("Limited Fighter", weight_class="Unknown")
    limited.update({"Elo Available": False, "Elo": 1000, "SLpM": 0, "TD Avg": 0, "Reach (cm)": 0, "Stance": "N/A"})
    comparison = {
        "stats1": limited,
        "stats2": _stats("Known Fighter"),
        "style1": {"label": "balanced"},
        "style2": {"label": "balanced"},
        "matchup": "Limited Fighter vs Known Fighter.",
    }
    prediction = {"winner": "Known Fighter", "confidence": 0.55, "prob_a": 0.45}

    analysis = build_fight_analysis(comparison, prediction)
    combined = " ".join(f"{read['label']} {read['prop_style']} {read['caution']}" for read in analysis["prop_reads"])

    assert analysis["prop_reads"][0]["id"] == "no_strong_prop_read"
    assert "Weight-class data incomplete" in combined
