import json
from pathlib import Path

import pandas as pd

from scripts.audit_winner_model_leakage import classify_feature, final_status, leakage_scan, runtime_parity_report
from scripts.evaluate_model_accuracy import chronological_train_validation_test_split
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


def test_committed_winner_audit_report_shape_if_present():
    path = Path("ufc_predictor/data/processed/winner_model_leakage_audit.json")
    if not path.is_file():
        return
    report = json.loads(path.read_text(encoding="utf-8"))

    assert report["winner_feature_list"]
    assert "source_holdout_results" in report
    assert any(item["variant"] == "shuffle_label_sanity_check" for item in report["ablation_results"])
    assert "runtime_parity" in report
