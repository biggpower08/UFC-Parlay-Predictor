"""Prediction pipeline, reporting, and fighter selection."""

from ufc_predictor.config import settings
from ufc_predictor.features.feature_engineering import (
    analyze_style,
    build_master_df,
    compare_fighters,
    extract_stats,
    find_name_column,
    search_fighter,
)
from ufc_predictor.models.ensemble.predictor import predict_ensemble
from ufc_predictor.utils.logger import get_logger

logger = get_logger(__name__)


def select_fighters(df):
    print("\n--- Select Fighter A ---")
    fa = _pick_one(df, "Fighter A")
    print("\n--- Select Fighter B ---")
    fb = _pick_one(df, "Fighter B")
    return fa, fb


def _pick_one(df, label):
    name_col = find_name_column(df)
    while True:
        query = input(f"\nEnter {label} full name: ").strip()
        matches = search_fighter(df, query)
        if matches.empty:
            print("  No exact match.")
            continue
        row = matches.iloc[0]
        print(f"  Selected: {row[name_col]}")
        return row


def run_prediction(f1, f2):
    comparison = compare_fighters(f1, f2)
    prediction = _generate_prediction(f1, f2, comparison)
    summary = _generate_summary(comparison, prediction)
    logger.info(
        "Prediction %s vs %s -> %s",
        comparison["stats1"]["Name"],
        comparison["stats2"]["Name"],
        prediction["winner"],
    )
    return comparison, prediction, summary


def _generate_prediction(f1, f2, comparison):
    return predict_ensemble(f1, f2, comparison)


def _generate_summary(comparison, prediction):
    s1, s2 = comparison["stats1"], comparison["stats2"]
    n1, n2 = s1["Name"], s2["Name"]
    prob_a = prediction.get("prob_a", 0.5)
    lean = _model_lean_text(n1, n2, prob_a)
    path1 = _win_condition_text(s1, s2, comparison["style1"])
    path2 = _win_condition_text(s2, s1, comparison["style2"])
    danger1 = _danger_text(s1, s2)
    danger2 = _danger_text(s2, s1)
    return (
        f"This profiles as a {comparison['style1']['label']} vs "
        f"{comparison['style2']['label']} matchup, with {n1} trying to win through "
        f"{path1} and {n2} needing {path2}. The biggest danger for {n1} is {danger1}; "
        f"for {n2}, it is {danger2}. {lean}, but this is MMA, so the read should stay "
        f"measured rather than absolute."
    )


def _model_lean_text(name1, name2, prob_a):
    if abs(prob_a - 0.5) < 0.08:
        return "The model sees it close to a coin flip"
    leader = name1 if prob_a > 0.5 else name2
    equity = max(prob_a, 1 - prob_a)
    if equity < 0.62:
        return f"The model gives a slight lean to {leader}"
    if equity < 0.72:
        return f"The model gives {leader} a meaningful edge"
    return f"The model gives {leader} the clearer statistical edge"


def _win_condition_text(stats_self, stats_opp, style_self):
    style = style_self.get("label", "balanced")
    if style == "grappler-leaning":
        if stats_self["TD Avg"] > stats_opp["TD Avg"]:
            return "takedowns, top control, and submission threats"
        return "clinches, grappling exchanges, and forcing scrambles"
    if style == "striker-leaning":
        if stats_self["SLpM"] >= stats_opp["SLpM"]:
            return "pace, cleaner volume, and damage on the feet"
        return "timing, counters, and making the striking exchanges count"
    if stats_self["TD Avg"] > 1.0 and stats_self["SLpM"] > 3.0:
        return "mixing striking volume with timely takedowns"
    if stats_self["TD Avg"] > stats_opp["TD Avg"]:
        return "changing levels and making the fight messy"
    return "staying defensively sound and winning enough minutes"


def _danger_text(stats_self, stats_opp):
    if stats_opp["TD Avg"] > stats_self["TD Avg"] + 1.0:
        return "getting stuck underneath after early takedowns"
    if stats_opp["SLpM"] > stats_self["SLpM"] + 1.0:
        return "falling behind against higher striking volume"
    if stats_opp["Reach (cm)"] > stats_self["Reach (cm)"] + 5:
        return "dealing with the range and first-contact exchanges"
    if stats_opp["Sub Avg"] > stats_self["Sub Avg"] + 0.5:
        return "giving up a scramble that turns into a submission look"
    if stats_self.get("Elo Available") and stats_opp.get("Elo Available") and stats_opp["Elo"] > stats_self["Elo"] + 40:
        return "letting the more proven fighter settle into rhythm"
    return "small mistakes snowballing in a fight that looks competitive on paper"


def print_report(comparison, prediction, summary):
    s1, s2 = comparison["stats1"], comparison["stats2"]
    n1, n2 = s1["Name"], s2["Name"]
    conf = prediction.get("confidence", 0.5)

    print("\n" + "=" * 60)
    print("1. SIDE-BY-SIDE FIGHTER STATS")
    print("=" * 60)
    _print_side_by_side(s1, s2)

    print("\n" + "=" * 60)
    print("2. KEY ADVANTAGES")
    print("=" * 60)
    for label, strengths, style in (
        (n1, comparison["strengths1"], comparison["style1"]["label"]),
        (n2, comparison["strengths2"], comparison["style2"]["label"]),
    ):
        print(f"\n{label} ({style}):")
        for item in strengths:
            print(f"  • {item}")

    print("\n" + "=" * 60)
    print("3. WEAKNESSES")
    print("=" * 60)
    for label, weak in ((n1, comparison["weaknesses1"]), (n2, comparison["weaknesses2"])):
        print(f"\n{label}:")
        for item in weak:
            print(f"  • {item}")

    print("\n" + "=" * 60)
    print("4. PREDICTED WINNER (not betting advice)")
    print("=" * 60)
    print(f"\nPrediction: {prediction['winner']}")
    print(f"Confidence: {conf:.1%}")
    print(f"Win prob: {n1} {prediction['prob_a']:.1%} | {n2} {prediction['prob_b']:.1%}")
    print(f"\nReasoning: {prediction['reasoning']}")

    print("\n" + "=" * 60)
    print("5. FIGHT SUMMARY")
    print("=" * 60)
    print(f"\n{summary}\n")


def _print_side_by_side(s1, s2):
    keys = [k for k in s1 if k != "Name"]
    w = 24
    print(f"\n{'STAT':<18} | {s1['Name'][:w]:<{w}} | {s2['Name'][:w]}")
    print("-" * (18 + w * 2 + 6))
    for key in keys:
        v1, v2 = s1[key], s2[key]
        if isinstance(v1, float):
            v1 = f"{v1:.2f}"
        if isinstance(v2, float):
            v2 = f"{v2:.2f}"
        print(f"{key:<18} | {str(v1):<{w}} | {v2}")
