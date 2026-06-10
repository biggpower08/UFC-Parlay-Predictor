from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _json(path: str) -> dict:
    return json.loads(_read(path))


def test_prediction_output_policy_exists_once_and_has_single_heading():
    policy_files = list((ROOT / "docs").glob("*prediction*policy*.md"))
    assert [path.name for path in policy_files] == ["prediction_output_policy.md"]
    text = _read("docs/prediction_output_policy.md")
    assert text.count("# Prediction Output Policy") == 1


def test_winner_interaction_status_matches_latest_report():
    interaction_report = _json("ufc_predictor/data/processed/interaction_discovery_report.json")
    winner = interaction_report["models"]["winner_model"]

    assert winner["selected_count"] == 0
    assert winner["selection_status"] == "base_features_kept"
    assert "selected a small interaction set" not in _read("docs/model_training_code_review.md")
    assert "winner selected a small interaction set" not in _read("docs/model_strengthening_plan.md").lower()


def test_production_ready_entries_do_not_have_source_holdout_not_run():
    registry = _json("ufc_predictor/data/processed/model_registry.json")
    for name, entry in registry.items():
        if entry.get("production_status") == "production_ready":
            assert "source_holdout_not_run" not in entry.get("failed_gates", []), name


def test_reports_include_source_holdout_gate_for_production_candidates():
    registry = _json("ufc_predictor/data/processed/model_registry.json")
    candidates = [
        name
        for name, entry in registry.items()
        if entry.get("production_status") == "production_candidate"
    ]
    report_text = _read("docs/model_accuracy_report.md")
    assert "Source-Holdout Transfer Summary" in report_text
    if candidates:
        for name in candidates:
            gates = registry[name].get("passed_gates", []) + registry[name].get("failed_gates", [])
            assert any(str(gate).startswith("source_holdout") for gate in gates), name
    else:
        downgraded = [
            entry
            for entry in registry.values()
            if entry.get("production_status") == "experimental"
            and any(str(gate).startswith("source_holdout") for gate in entry.get("failed_gates", []))
        ]
        assert downgraded


def test_report_segment_keys_do_not_keep_bout_suffix_variants():
    for path in [
        "ufc_predictor/data/processed/model_accuracy_report.json",
        "ufc_predictor/data/processed/backtest_report.json",
    ]:
        payload = _json(path)
        text = json.dumps(payload)
        assert "weight_class:bantamweight_bout" not in text
        assert "weight_class:women's_bantamweight_bout" not in text
