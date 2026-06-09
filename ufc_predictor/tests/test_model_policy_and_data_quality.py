from __future__ import annotations

import json
from pathlib import Path

from scripts.evaluate_model_accuracy import backfill_registry_gate_fields
from ufc_predictor.features.data_quality import score_matchup_data_quality


def test_data_quality_flags_dangerous_matchup_and_hides_weak_models():
    result = score_matchup_data_quality(
        {
            "minimum_history_count": 0,
            "missing_profile_warning": True,
            "missing_stats_warning": True,
            "cross_division": True,
            "unknown_size_context": True,
            "fighter_1_elo_available": False,
            "fighter_2_elo_available": True,
        },
        {
            "winner_model": "high_confidence_only",
            "finish_type_model": "weak_or_failed_baseline",
            "odds_calibration_model": "blocked",
        },
    )

    assert result["data_quality"] == "dangerous"
    assert "debutant_or_no_prior_history" in result["warning_reasons"]
    assert "cross_division_or_catchweight_context" in result["warning_reasons"]
    assert "finish_type_model" in result["models_hidden_or_context_only"]
    assert "odds_calibration_model" in result["models_hidden_or_context_only"]
    assert "winner_model" in result["models_allowed_for_matchup"]


def test_data_quality_keeps_clean_matchup_strong():
    result = score_matchup_data_quality(
        {
            "minimum_history_count": 8,
            "fighter_1_elo_available": True,
            "fighter_2_elo_available": True,
        },
        {"winner_model": "high_confidence_only"},
    )

    assert result["data_quality"] == "strong"
    assert result["score"] == 0


def test_registry_backfill_adds_policy_fields_to_legacy_entries():
    registry = {"legacy_model": {"status": "not_trained", "limitations": ["missing artifact"]}}

    backfill_registry_gate_fields(registry, {}, {}, {}, "2026-01-01T00:00:00+00:00")

    entry = registry["legacy_model"]
    assert entry["production_status_reason"]
    assert "failed_gates" in entry
    assert "passed_gates" in entry
    assert "public_warning_text" in entry
    assert "data_quality_requirements" in entry
    assert "selective_prediction_policy" in entry


def test_prediction_policy_doc_keeps_weak_models_context_only():
    text = Path("docs/prediction_output_policy.md").read_text(encoding="utf-8").lower()

    assert "finish_type_model" in text
    assert "context only" in text
    assert "odds_calibration_model" in text
    assert "blocked" in text


def test_artifact_packaging_doc_excludes_weak_and_raw_files():
    text = Path("docs/model_artifact_packaging_plan.md").read_text(encoding="utf-8").lower()

    assert "do not package `weak_or_failed_baseline`" in text
    assert "data/imports/" in text
    assert "training_imports" in text
    assert "backtest_predictions.json" in text


def test_registry_has_policy_fields_if_present():
    path = Path("ufc_predictor/data/processed/model_registry.json")
    if not path.is_file():
        return
    registry = json.loads(path.read_text(encoding="utf-8"))
    for entry in registry.values():
        assert "production_status_reason" in entry
        assert "failed_gates" in entry
        assert "passed_gates" in entry
        assert "public_warning_text" in entry
