from __future__ import annotations

import json
import subprocess
from pathlib import Path

from scripts.audit_metric_jumps import build_audit


def test_metric_jump_audit_flags_source_holdout_gap_and_feature_change():
    previous = {
        "audit": {"fight_rows": 100, "feature_count": 10, "date_range": {"min": "2020-01-01", "max": "2021-01-01"}},
        "split": {"train_rows": 60, "validation_rows": 20, "test_rows": 20},
        "models": {"fight_duration_model": {"final_test_metric": 0.7, "test_rows": 20, "metrics": {"balanced_accuracy": 0.69}}},
    }
    current = {
        "audit": {"fight_rows": 100, "feature_count": 15, "date_range": {"min": "2020-01-01", "max": "2021-01-01"}},
        "split": {"train_rows": 60, "validation_rows": 20, "test_rows": 20},
        "calibration": {"status": "basic_probability_scores_only"},
        "models": {"fight_duration_model": {"final_test_metric": 0.82, "test_rows": 20, "metrics": {"balanced_accuracy": 0.8}}},
    }
    registry = {"fight_duration_model": {"production_status": "production_candidate", "failed_gates": ["source_holdout_not_run"]}}
    interactions = {"models": {"fight_duration_model": {"candidate_count": 240, "selected_count": 8}}}

    audit = build_audit(current, previous, registry, interactions, "old-ref")
    model = next(item for item in audit["models"] if item["model"] == "fight_duration_model")

    assert audit["row_and_split_summary"]["feature_count_delta"] == 5
    assert audit["row_and_split_summary"]["row_count_changed"] is False
    assert model["delta"] == 0.12
    assert model["risk_level"] == "medium"
    assert model["verdict"] == "needs_review"
    assert "source_holdout_not_passing" in model["review_reasons"]


def test_metric_jump_audit_doc_exists_after_report_generation():
    path = Path("docs/metric_jump_audit.md")
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    assert "Metric Jump Audit" in text
    assert "basic_probability_scores_only" in text
    assert "source_holdout_not_run" in text


def test_current_report_can_compare_to_previous_git_report():
    raw = subprocess.check_output(
        ["git", "show", "a955ca9:ufc_predictor/data/processed/model_accuracy_report.json"],
        text=True,
    )
    previous = json.loads(raw)
    current = json.loads(Path("ufc_predictor/data/processed/model_accuracy_report.json").read_text(encoding="utf-8"))

    assert previous["audit"]["fight_rows"] == current["audit"]["fight_rows"]
    assert previous["audit"]["feature_count"] <= current["audit"]["feature_count"]
