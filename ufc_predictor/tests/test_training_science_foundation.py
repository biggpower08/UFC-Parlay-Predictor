import pandas as pd
from pathlib import Path

import numpy as np

from scripts.evaluate_model_accuracy import feature_names_for_model, finish_rows
from scripts.backtest_historical_fights import method_umbrella_probabilities, model_prediction_payload
from scripts.train_prop_models import registry_entry_from_artifact
from ufc_predictor.features.feature_schema import get_feature_schema
from ufc_predictor.features.matchup_features import (
    build_historical_feature_set,
    build_matchup_feature_set,
    validate_feature_set,
)
from ufc_predictor.training.leakage import scan_dataframe
from ufc_predictor.training.size_context import build_size_context
from ufc_predictor.training.splits import chronological_split_df, event_grouped_split
from ufc_predictor.training.targets import build_bettor_targets, safe_f1_wins


def test_safe_f1_wins_drops_missing_or_unmatched_winner():
    row = pd.Series({"f_1_name": "Alpha Fighter", "f_2_name": "Beta Fighter", "winner": "  alpha fighter "})
    assert safe_f1_wins(row, "f_1_name", "f_2_name", "winner") == (1, None)

    row = pd.Series({"f_1_name": "Alpha Fighter", "f_2_name": "Beta Fighter", "winner": "No Contest"})
    assert safe_f1_wins(row, "f_1_name", "f_2_name", "winner") == (None, "missing_or_non_win_winner")

    row = pd.Series({"f_1_name": "Alpha Fighter", "f_2_name": "Beta Fighter", "winner": "Gamma Fighter"})
    assert safe_f1_wins(row, "f_1_name", "f_2_name", "winner") == (None, "missing_or_unmatched_winner")


def test_bettor_targets_keep_props_independent_from_winner():
    frame = pd.DataFrame(
        [
            {
                "f_1_name": "Alpha Fighter",
                "f_2_name": "Beta Fighter",
                "winner": "Beta Fighter",
                "result": "Decision",
                "finish_round": 3,
                "finish_time": "5:00",
                "f_1_sig_strikes_succ": 80,
                "f_2_sig_strikes_succ": 30,
                "f_1_takedown_succ": 2,
                "f_2_takedown_succ": 0,
                "event_date": "2024-01-01",
            }
        ]
    )

    targeted, report = build_bettor_targets(frame)

    assert targeted.iloc[0]["f1_wins"] == 0
    assert targeted.iloc[0]["fighter_1_over_50_sig_strikes"] == 1
    assert targeted.iloc[0]["fighter_1_over_1_5_takedowns"] == 1
    assert report.valid_winner_targets == 1


def test_leakage_scanner_flags_outcomes_and_current_fight_stats():
    frame = pd.DataFrame(
        columns=[
            "winner",
            "result",
            "finish_round",
            "f_1_sig_strikes_succ",
            "f_1_takedown_succ",
            "f_1_fighter_reach_cm",
            "f_1_fighter_stance",
            "pre_fight_moneyline_f1",
        ]
    )

    report = scan_dataframe(frame)
    by_column = {row["column"]: row["classification"] for row in report["columns"]}

    assert by_column["winner"] == "label_only"
    assert by_column["result"] == "label_only"
    assert by_column["finish_round"] == "label_only"
    assert by_column["f_1_sig_strikes_succ"] == "leakage_excluded"
    assert by_column["f_1_takedown_succ"] == "leakage_excluded"
    assert by_column["f_1_fighter_reach_cm"] == "runtime_available"
    assert by_column["pre_fight_moneyline_f1"] == "safe_prefight_feature"


def test_target_columns_cannot_become_features():
    schema = get_feature_schema("winner")
    target_columns = {
        "f1_wins",
        "went_distance",
        "over_2_5",
        "over_1_5_binary",
        "over_2_5_binary",
        "ends_before_round_3_binary",
        "finish_in_round_1_binary",
        "finish_type_class",
        "method_class",
        "fighter_a_sig_strikes",
        "fighter_b_takedowns",
        "grappling_heavy_binary",
    }

    assert not target_columns.intersection(schema.all_features())
    assert {"f1_wins", "method_class", "finish_type_class", "over_2_5_binary", "grappling_heavy_binary"} <= set(schema.forbidden_features)


def test_duration_model_features_exclude_outcome_labels():
    frame = pd.DataFrame(
        [
            {
                "a_prior_fights": 1,
                "b_prior_fights": 1,
                "a_prior_wins": 1,
                "b_prior_wins": 0,
                "a_prior_finishes": 1,
                "b_prior_finishes": 0,
                "a_prior_decisions": 0,
                "b_prior_decisions": 0,
                "finish_binary": 1,
                "goes_distance_binary": 0,
                "result": "win",
                "method_class": "KO/TKO",
                "round_number": 1,
            }
        ]
    )

    features = feature_names_for_model(frame, frame, frame, "fight_duration_model")

    assert "finish_binary" not in features
    assert "goes_distance_binary" not in features
    assert "method_class" not in features
    assert "round_number" not in features
    assert "result" not in features


def test_finish_type_rows_keep_only_finished_fights():
    rows = pd.DataFrame(
        [
            {"finish_binary": 1, "finish_type_class": "KO/TKO"},
            {"finish_binary": 0, "finish_type_class": None},
            {"finish_binary": 1.0, "finish_type_class": "Submission"},
        ]
    )

    filtered = finish_rows(rows)

    assert filtered["finish_type_class"].tolist() == ["KO/TKO", "Submission"]


def test_goes_distance_probability_is_inverse_of_finish_probability():
    payload = model_prediction_payload("goes_distance_model", "1", ["0", "1"], np.asarray([0.35, 0.65]))

    assert payload["finish_probability"] == 0.65
    assert payload["goes_distance_probability"] == 0.35
    assert payload["predicted_class"] == "0"


class _FixedProbabilityModel:
    def __init__(self, classes, probabilities):
        self.classes_ = np.asarray(classes)
        self._probabilities = np.asarray(probabilities)

    def predict_proba(self, rows):
        return np.tile(self._probabilities, (len(rows), 1))


def test_method_umbrella_probabilities_are_conditional_and_sum_to_one():
    info = {
        "classes": ["Decision", "KO/TKO", "Submission"],
        "duration_classes": ["0", "1"],
        "duration_model": _FixedProbabilityModel(["0", "1"], [0.4, 0.6]),
        "finish_type_classes": ["KO/TKO", "Submission"],
        "finish_type_model": _FixedProbabilityModel(["KO/TKO", "Submission"], [0.25, 0.75]),
    }

    probs = method_umbrella_probabilities(info, pd.DataFrame({"a_prior_fights": [1]}))

    assert probs.shape == (1, 3)
    assert abs(float(probs.sum()) - 1.0) < 0.0001
    assert round(float(probs[0][0]), 4) == 0.4
    assert round(float(probs[0][1]), 4) == 0.15
    assert round(float(probs[0][2]), 4) == 0.45


def test_chronological_and_event_grouped_splits_are_safe():
    frame = pd.DataFrame(
        [
            {"event_name": "Event 1", "event_date": "2024-01-01", "fighter_1": "A", "fighter_2": "B", "f1_wins": 1},
            {"event_name": "Event 1", "event_date": "2024-01-01", "fighter_1": "C", "fighter_2": "D", "f1_wins": 0},
            {"event_name": "Event 2", "event_date": "2024-02-01", "fighter_1": "E", "fighter_2": "F", "f1_wins": 1},
            {"event_name": "Event 3", "event_date": "2024-03-01", "fighter_1": "G", "fighter_2": "H", "f1_wins": 0},
        ]
    )

    train, test, report = chronological_split_df(frame, test_size=0.25)
    assert report["status"] == "ok"
    assert train["event_date"].max() <= test["event_date"].min()

    train, test, report = event_grouped_split(frame, test_size=0.34)
    assert report["event_overlap"] == []
    assert set(train["event_name"]).isdisjoint(set(test["event_name"]))


def test_permanent_agent_instructions_document_training_rules():
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "C:\\venvs\\mma-ai\\Scripts\\python.exe" in text
    assert "pre-fight features only" in text
    assert "chronological final-test evaluation" in text
    assert "Do not mark `production_ready` unless" in text
    assert "--basetemp $TempTestDir" in text


def test_model_accuracy_report_includes_baseline_and_relative_improvement():
    text = Path("docs/model_accuracy_report.md").read_text(encoding="utf-8")

    assert "Baseline" in text
    assert "Improvement" in text
    assert "Beats Baseline" in text


def test_weak_models_are_not_production_ready_in_registry():
    registry_path = Path("ufc_predictor/data/processed/model_registry.json")
    if not registry_path.is_file():
        return
    import json

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    for model in registry.values():
        if model.get("beats_baseline") is False or model.get("backtest_beats_baseline") is False:
            assert model.get("status") != "production_ready"


def test_size_context_and_pound_for_pound_mode():
    actual = build_size_context(
        {"Weight Class": "Flyweight", "Height (cm)": 165, "Reach (cm)": 170},
        {"Weight Class": "Heavyweight", "Height (cm)": 190, "Reach (cm)": 205},
    )
    p4p = build_size_context(
        {"Weight Class": "Flyweight", "Height (cm)": 165, "Reach (cm)": 170},
        {"Weight Class": "Heavyweight", "Height (cm)": 190, "Reach (cm)": 205},
        pound_for_pound=True,
    )

    assert actual["cross_division"] is True
    assert actual["severity"] == "high"
    assert p4p["label"] == "pound-for-pound view"
    assert p4p["size_features_used"] is False
    assert p4p["estimated_weight_gap_lbs"] == 0


def test_historical_feature_generation_uses_only_prior_fights():
    fights = pd.DataFrame(
        [
            {
                "event": "Early Event",
                "event_date": "2024-01-01",
                "fighter_1": "Alpha Fighter",
                "fighter_2": "Beta Fighter",
                "result": "win",
                "method": "KO/TKO",
                "round": 1,
            },
            {
                "event": "Middle Event",
                "event_date": "2024-02-01",
                "fighter_1": "Alpha Fighter",
                "fighter_2": "Gamma Fighter",
                "result": "win",
                "method": "Decision",
                "round": 3,
            },
            {
                "event": "Target Event",
                "event_date": "2024-03-01",
                "fighter_1": "Alpha Fighter",
                "fighter_2": "Beta Fighter",
                "result": "win",
                "method": "Submission",
                "round": 2,
            },
        ]
    )

    feature_set = build_historical_feature_set(fights.iloc[2], fights, model_family="finish")

    assert feature_set.validation["valid"] is True
    assert feature_set.features["a_prior_fights"] == 2
    assert feature_set.features["b_prior_fights"] == 1
    assert "method" not in feature_set.features
    assert "winner" not in feature_set.features


def test_live_and_historical_feature_outputs_share_schema_keys():
    schema = get_feature_schema("finish")
    historical = build_historical_feature_set(
        pd.Series(
            {
                "event_date": "2024-02-01",
                "fighter_1": "Alpha Fighter",
                "fighter_2": "Beta Fighter",
                "result": "win",
                "method": "Decision",
                "round": 3,
            }
        ),
        pd.DataFrame(
            [
                {
                    "event_date": "2024-01-01",
                    "fighter_1": "Alpha Fighter",
                    "fighter_2": "Beta Fighter",
                    "result": "win",
                    "method": "KO/TKO",
                    "round": 1,
                }
            ]
        ),
        model_family="finish",
    )
    live = build_matchup_feature_set(
        {"name": "Alpha Fighter", "wins": 10, "losses": 2, "height_cm": 180, "reach_cm": 185, "weight_class": "Lightweight"},
        {"name": "Beta Fighter", "wins": 8, "losses": 4, "height_cm": 175, "reach_cm": 178, "weight_class": "Lightweight"},
        mode="live",
        model_family="finish",
    )

    assert set(historical.features) == set(schema.all_features())
    assert set(live.features) == set(schema.all_features())
    assert live.model_feature_coverage["required_features_available"] is True


def test_feature_validation_rejects_label_and_current_fight_columns():
    schema = get_feature_schema("finish")
    features = {name: 0 for name in schema.required_features}
    features["winner"] = "Alpha Fighter"
    features["fighter_a_sig_strikes"] = 80

    validation = validate_feature_set(features, "finish")

    assert validation["valid"] is False
    assert "winner" in validation["leakage_columns_found"]
    assert "fighter_a_sig_strikes" in validation["leakage_columns_found"]


def test_runtime_feature_factory_supports_pound_for_pound_mode():
    feature_set = build_matchup_feature_set(
        {"name": "Small Fighter", "wins": 5, "losses": 1, "height_cm": 165, "reach_cm": 170, "weight_class": "Flyweight"},
        {"name": "Large Fighter", "wins": 5, "losses": 1, "height_cm": 190, "reach_cm": 205, "weight_class": "Heavyweight"},
        mode="live",
        model_family="winner",
        feature_mode="pound_for_pound",
    )

    assert feature_set.features["pound_for_pound_mode"] is True
    assert feature_set.features["size_features_used"] is False
    assert feature_set.features["estimated_weight_gap_lbs"] == 0
    assert feature_set.features["height_gap"] == 0


def test_registry_entry_records_feature_schema_metadata(tmp_path):
    artifact = {
        "metadata": {
            "model_name": "finish_model",
            "target_label": "finish_binary",
            "model_type": "nearest_centroid_softmax_baseline",
            "status": "trained",
            "training_rows": 10,
            "validation_rows": 5,
            "date_range": {"min": "2024-01-01", "max": "2024-02-01"},
            "split_type": "chronological",
            "leakage_checked": True,
            "feature_names": get_feature_schema("finish").required_features,
            "class_distribution": {"0": 5, "1": 10},
            "limitations": [],
            "source_datasets": ["synthetic"],
            "source_files": [],
            "trained_at": "2024-03-01T00:00:00+00:00",
        },
        "metrics": {"validation": {"accuracy": 0.6}, "majority_class_baseline": {"accuracy": 0.5}},
    }

    entry = registry_entry_from_artifact(artifact, tmp_path / "finish_model.json")

    assert entry["feature_schema_name"] == "finish_v1"
    assert entry["feature_schema_version"] == "1.0"
    assert entry["feature_factory_supported"] is True
    assert entry["required_features_available"] is True
