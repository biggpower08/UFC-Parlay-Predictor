from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

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
