from __future__ import annotations

import pandas as pd

from scripts.source_transfer_diagnostics import (
    build_feature_label_drift_report,
    build_source_diagnostics,
    build_strategy_ablation_report,
)
from scripts.evaluate_model_accuracy import chronological_train_validation_test_split
from ufc_predictor.training.dataset_builder import build_training_rows


def _sample_rows() -> pd.DataFrame:
    rows = []
    sources = ["source_a", "ufc_stats_complete"]
    for index in range(80):
        source = sources[index % 2]
        finish = 1 if (index % 3 == 0 or source == "ufc_stats_complete") else 0
        rows.append(
            {
                "event": f"Event {index}",
                "event_date": f"2024-{(index % 12) + 1:02d}-01",
                "fighter_1": f"Fighter {index}",
                "fighter_2": f"Opponent {index}",
                "result": "win",
                "method": "KO/TKO" if finish else "Decision",
                "round": 1 if finish else 3,
                "time": "1:00" if finish else "5:00",
                "source_dataset": source,
                "source_file": f"{source}.csv",
                "weight_class": "Lightweight Bout" if index % 5 == 0 else "Lightweight",
                "fighter_a_sig_strikes": 40 + index,
                "fighter_b_sig_strikes": 20,
                "fighter_a_takedowns": index % 4,
                "fighter_b_takedowns": 0,
            }
        )
    return pd.DataFrame(rows)


def test_source_transfer_diagnostics_reports_ufc_stats_complete_and_drift_fields():
    raw = _sample_rows()
    dataset, audit = build_training_rows(raw)
    train, validation, test, split = chronological_train_validation_test_split(dataset, validation_size=0.2, test_size=0.2)
    model_report = {
        "models": {
            "fight_duration_model": {
                "source_holdout": {
                    "status": "unstable",
                    "by_source": [
                        {"source": "ufc_stats_complete", "rows": 20, "accuracy": 0.5, "balanced_accuracy": 0.45, "metric_drop": 0.2, "balanced_accuracy_drop": 0.25}
                    ],
                }
            }
        }
    }
    registry = {"fight_duration_model": {"production_status": "experimental"}}

    diagnostics = build_source_diagnostics(raw, dataset, train, validation, test, model_report, registry, audit.to_dict(), split)
    drift = build_feature_label_drift_report(dataset, train, validation, test, model_report, registry)
    strategy = build_strategy_ablation_report(diagnostics, drift, model_report, registry)

    assert "ufc_stats_complete" in diagnostics["source_reports"]
    ufc_report = diagnostics["source_reports"]["ufc_stats_complete"]
    assert ufc_report["target_coverage_by_model"]["fight_duration_model"] > 0
    assert "style" in ufc_report["missingness_by_feature_group"]
    assert ufc_report["drift_grade"] in {"low drift", "medium drift", "high drift", "dangerous drift"}
    assert drift["models"]["fight_duration_model"]["sources"]["ufc_stats_complete"]["overall_source_risk_score"] >= 0
    assert any(row["strategy"] == "exclude_ufc_stats_complete_from_training_test_on_it" for row in strategy["strategies"])
