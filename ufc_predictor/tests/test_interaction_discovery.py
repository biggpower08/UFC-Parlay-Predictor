from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.evaluate_model_accuracy import production_gate_result
from ufc_predictor.features.feature_groups import group_features
from ufc_predictor.features.interaction_discovery import add_interaction_features, discover_candidate_interactions
from ufc_predictor.features.feature_schema import FORBIDDEN_FEATURES


def _frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "a_prior_fights": range(120),
            "b_prior_fights": range(1, 121),
            "a_prior_wins": [value % 7 for value in range(120)],
            "b_prior_wins": [value % 5 for value in range(120)],
            "a_prior_finishes": [value % 4 for value in range(120)],
            "b_prior_finishes": [value % 3 for value in range(120)],
            "a_prior_decisions": [value % 2 for value in range(120)],
            "b_prior_decisions": [(value + 1) % 2 for value in range(120)],
            "win_rate_diff": [value / 100 for value in range(120)],
            "finish_rate_diff": [(value % 17) / 20 for value in range(120)],
            "reach_gap": [(-1) ** value * (value % 8) for value in range(120)],
            "scheduled_rounds": [3 for _ in range(120)],
            "fighter_1_striker_score": [(value % 20) / 20 for value in range(120)],
            "fighter_2_strike_absorption_weakness": [(value % 13) / 13 for value in range(120)],
            "fighter_1_wrestler_score": [(value % 11) / 11 for value in range(120)],
            "fighter_2_takedown_defense_weakness_proxy": [(value % 9) / 9 for value in range(120)],
            "fighter_1_power_finisher_score": [(value % 7) / 7 for value in range(120)],
            "fighter_2_durability_weakness": [(value % 5) / 5 for value in range(120)],
            "fighter_1_high_pace_score": [(value % 17) / 17 for value in range(120)],
            "fighter_2_poor_recent_form_weakness": [(value % 6) / 6 for value in range(120)],
            "same_division": [1 for _ in range(120)],
            "low_sample_warning": [1 if value < 20 else 0 for value in range(120)],
            "finish_binary": [value % 2 for value in range(120)],
            "method_class": ["Decision" if value % 2 else "KO/TKO" for value in range(120)],
        }
    )


def test_feature_groups_are_safe_prefight_only():
    groups = group_features("fight_duration_model", list(_frame().columns))
    flat = {feature for values in groups.values() for feature in values}

    assert "finish_binary" not in flat
    assert "method_class" not in flat
    assert flat


def test_interaction_generator_rejects_forbidden_and_builds_runtime_features():
    frame = _frame()
    report = discover_candidate_interactions(frame, "fight_duration_model", list(frame.columns), max_candidates=12)

    assert report["accepted_count"] > 0
    for item in report["accepted"]:
        assert not set(item["input_features"]).intersection(FORBIDDEN_FEATURES)
    enriched = add_interaction_features(frame, report["accepted"][:3])
    for item in report["accepted"][:3]:
        assert item["name"] in enriched.columns
        assert enriched[item["name"]].notna().mean() >= 0.65
        assert enriched[item["name"]].var() > 0


def test_interaction_discovery_documents_final_test_is_not_used():
    report = discover_candidate_interactions(_frame(), "winner_model", list(_frame().columns), max_candidates=5)

    assert report["selection_rules"]["final_test_used_for_selection"] is False
    assert report["safety_checks"]["selection_uses_validation_only"] is True
    assert report["safety_checks"]["final_test_used_for_selection"] is False


def test_interaction_audit_counts_types_groups_and_rejections():
    report = discover_candidate_interactions(_frame(), "fight_duration_model", list(_frame().columns), max_candidates=80)

    assert "candidate_count_by_interaction_type" in report
    assert "pairwise_products" in report["candidate_count_by_interaction_type"]
    assert report["candidate_count_by_interaction_type"]["fighter_strength_vs_opponent_weakness"] > 0
    assert "candidate_count_by_feature_group_pair" in report
    for family in [
        "striking x opponent weakness",
        "grappling x opponent weakness",
        "finishing x durability",
        "pace x age/activity",
        "scheduled rounds x pace/duration",
    ]:
        assert report["candidate_count_by_feature_group_pair"][family] > 0
    assert "rejection_counts" in report
    assert "missingness" in report["rejection_counts"]
    assert "validation_did_not_improve" in report["rejection_counts"]


def test_selected_interactions_are_runtime_computable_from_base_features():
    frame = _frame()
    report = discover_candidate_interactions(frame, "winner_model", list(frame.columns), max_candidates=8)
    selected = report["accepted"][:3]
    enriched = add_interaction_features(frame, selected)

    base_features = set(frame.columns)
    for item in selected:
        assert set(item["input_features"]).issubset(base_features)
        assert item["name"] in enriched.columns


def test_interaction_reports_and_registry_fields_if_present():
    report_path = Path("ufc_predictor/data/processed/interaction_discovery_report.json")
    registry_path = Path("ufc_predictor/data/processed/model_registry.json")
    if not report_path.is_file():
        return
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "models" in report
    assert "selection_policy" in report
    if registry_path.is_file():
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        for name in report["models"]:
            entry = registry.get(name)
            if entry:
                assert "interaction_feature_count" in entry
                assert "selected_interactions" in entry
                assert "interaction_selection_status" in entry
                if entry.get("selected_interactions"):
                    assert "selected_interactions_detailed" in entry


def test_registry_records_interaction_audit_if_present():
    registry_path = Path("ufc_predictor/data/processed/model_registry.json")
    if not registry_path.is_file():
        return
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    entries_with_interactions = [entry for entry in registry.values() if entry.get("interaction_feature_count")]
    for entry in entries_with_interactions:
        assert "interaction_audit_summary" in entry
        assert "interaction_safety_checks" in entry


def test_source_holdout_regression_blocks_production_ready_for_interactions():
    result = {
        "status": "evaluated",
        "beats_baseline": True,
        "feature_names": ["a_prior_fights", "b_prior_fights"],
        "interaction_feature_count": 1,
        "interaction_discovery": {
            "source_holdout_regression_detected": True,
            "safety_checks": {
                "final_test_used_for_selection": False,
                "forbidden_target_columns_excluded": True,
                "selected_interactions_runtime_computable": True,
            },
        },
        "metrics": {"balanced_accuracy": 0.8, "brier_score": 0.12},
        "selective_prediction": {
            "best_accuracy": {"sample_count": 200, "coverage_percent": 10, "accuracy": 0.8}
        },
    }
    split = {"no_cross_split_fight_leakage": True}

    gates = production_gate_result("fight_duration_model", result, split, {})

    assert gates["production_status"] != "production_ready"
    assert "interaction_source_holdout_regression" in gates["failed_gates"]
