import json
from pathlib import Path

import pandas as pd

from scripts.audit_winner_model_leakage import classify_feature, final_status, leakage_scan, runtime_parity_report
from scripts.evaluate_model_accuracy import chronological_train_validation_test_split, production_gate_result
from ufc_predictor.training.deduping import stable_fight_key


def test_winner_feature_classification_flags_leakage_like_columns():
    assert classify_feature("winner")["classification"] == "leakage_excluded"
    assert classify_feature("fighter_a_sig_strikes")["classification"] == "leakage_excluded"
    assert classify_feature("a_prior_fights")["classification"] in {"runtime_available", "safe_pre_fight"}


def test_winner_leakage_scan_has_no_direct_target_columns_for_safe_features():
    report = leakage_scan(["a_prior_fights", "b_prior_fights", "win_rate_diff"])

    assert report["passed"] is True
    assert report["leakage_excluded_in_feature_set"] == []


def test_runtime_parity_report_blocks_missing_runtime_features():
    report = runtime_parity_report(["a_prior_fights", "training_only_magic_feature"])

    assert report["runtime_compatible"] is False
    assert report["missing_runtime_features"][0]["feature"] == "training_only_magic_feature"


def test_same_canonical_fight_cannot_cross_audit_splits():
    rows = []
    for day in range(1, 16):
        for left, right in [(f"Alpha {day}", f"Beta {day}"), (f"Beta {day}", f"Alpha {day}")]:
            row = {
                "event_date": f"2024-01-{day:02d}",
                "event": "Event",
                "fighter_a": left,
                "fighter_b": right,
                "source_order": day,
            }
            row["fight_key"] = stable_fight_key(row)
            rows.append(row)
    frame = pd.DataFrame(rows)

    train, validation, test, report = chronological_train_validation_test_split(frame, validation_size=0.2, test_size=0.2)

    assert report["no_cross_split_fight_leakage"] is True
    assert set(train["_split_fight_key"]).isdisjoint(set(validation["_split_fight_key"]))
    assert set(train["_split_fight_key"]).isdisjoint(set(test["_split_fight_key"]))


def test_winner_model_cannot_be_production_ready_when_runtime_parity_fails():
    payload = {
        "runtime_parity": {"runtime_compatible": False},
        "leakage_scan": {"passed": True, "suspicious_review_needed": []},
        "source_holdout_results": [{"metrics": {"balanced_accuracy": 0.8}}],
        "stress_tests": {"low_history_any_fighter_under_3": {"metrics": {"balanced_accuracy": 0.8}}},
    }
    full = {"metrics": {"balanced_accuracy": 0.9}}

    status = final_status(payload, full)

    assert status["status"] != "production_ready"
    assert status["status"] == "high_confidence_only"


def test_source_holdout_weakness_blocks_production_ready():
    result = {
        "status": "evaluated",
        "beats_baseline": True,
        "feature_names": ["a_prior_fights"],
        "test_rows": 1000,
        "metrics": {"balanced_accuracy": 0.9, "brier_score": 0.1, "log_loss": 0.3},
        "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
    }
    split = {"no_cross_split_fight_leakage": True}
    audit = {
        "final_status": {
            "leakage_scan_ok": True,
            "runtime_parity_ok": True,
            "source_holdout_ok": False,
            "low_history_ok": True,
        }
    }

    gates = production_gate_result("winner_model", result, split, audit)

    assert gates["production_status"] == "high_confidence_only"
    assert "source_holdout_stable" in gates["failed_gates"]
    assert gates["public_warning_text"]


def test_high_confidence_only_status_is_allowed_when_manual_review_gate_fails():
    result = {
        "status": "evaluated",
        "beats_baseline": True,
        "feature_names": ["a_prior_fights"],
        "test_rows": 1000,
        "metrics": {"balanced_accuracy": 0.9, "brier_score": 0.1, "log_loss": 0.3},
        "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
    }
    split = {"no_cross_split_fight_leakage": True}
    audit = {
        "final_status": {
            "leakage_scan_ok": True,
            "runtime_parity_ok": True,
            "source_holdout_ok": True,
            "low_history_ok": True,
            "status": "high_confidence_only",
        }
    }

    gates = production_gate_result("winner_model", result, split, audit)

    assert gates["production_status"] == "production_candidate"
    assert "source_holdout_manual_review_required" in gates["failed_gates"]


def test_winner_leakage_audit_blocks_production_ready():
    result = {
        "status": "evaluated",
        "beats_baseline": True,
        "feature_names": ["a_prior_fights"],
        "test_rows": 1000,
        "metrics": {"balanced_accuracy": 0.9, "brier_score": 0.1, "log_loss": 0.3},
        "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
    }
    split = {"no_cross_split_fight_leakage": True}
    audit = {
        "final_status": {
            "leakage_scan_ok": False,
            "runtime_parity_ok": True,
            "source_holdout_ok": True,
            "low_history_ok": True,
        }
    }

    gates = production_gate_result("winner_model", result, split, audit)

    assert gates["production_status"] == "high_confidence_only"
    assert "winner_leakage_audit_passes" in gates["failed_gates"]


def test_weak_and_odds_models_get_blocked_or_experimental_gate_statuses():
    weak = production_gate_result(
        "round_phase_model",
        {
            "status": "weak_or_failed_baseline",
            "beats_baseline": False,
            "feature_names": ["a_prior_fights"],
            "metrics": {"balanced_accuracy": 0.3, "log_loss": 1.2},
            "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
        },
        {"no_cross_split_fight_leakage": True},
        {},
    )
    odds = production_gate_result(
        "odds_calibration_model",
        {"status": "blocked", "limitations": ["Pre-fight odds timestamps are not trusted."]},
        {"no_cross_split_fight_leakage": True},
        {},
    )

    assert weak["production_status"] == "weak_or_failed_baseline"
    assert odds["production_status"] == "blocked"
    assert "model_blocked" in odds["failed_gates"]


def test_committed_winner_audit_report_shape_if_present():
    path = Path("ufc_predictor/data/processed/winner_model_leakage_audit.json")
    if not path.is_file():
        return
    report = json.loads(path.read_text(encoding="utf-8"))

    assert report["winner_feature_list"]
    assert "source_holdout_results" in report
    assert any(item["variant"] == "shuffle_label_sanity_check" for item in report["ablation_results"])
    assert "runtime_parity" in report


def test_registry_entries_have_production_gate_fields_if_present():
    path = Path("ufc_predictor/data/processed/model_registry.json")
    if not path.is_file():
        return
    registry = json.loads(path.read_text(encoding="utf-8"))
    for name, entry in registry.items():
        assert entry.get("production_status_reason"), name
        assert "failed_gates" in entry, name
        assert "passed_gates" in entry, name
        if entry.get("production_status") == "high_confidence_only":
            assert entry.get("public_warning_text"), name
