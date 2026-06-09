import pandas as pd

from scripts.backtest_historical_fights import (
    FORBIDDEN_BACKTEST_INPUTS,
    backtest_segments,
    examples,
    round_family_backtest_model,
    run_backtest,
)


def _synthetic_dataset(rows: int = 80) -> pd.DataFrame:
    records = []
    for index in range(rows):
        event_date = pd.Timestamp("2020-01-01") + pd.Timedelta(days=index * 7)
        finish = 1 if index % 3 else 0
        method = "Decision" if finish == 0 else ("KO/TKO" if index % 2 else "Submission")
        round_phase = "decision" if method == "Decision" else ("early" if index % 2 else "middle")
        records.append(
            {
                "event_date": str(event_date.date()),
                "event": f"Event {index}",
                "fighter_a": f"Alpha {index}",
                "fighter_b": f"Beta {index}",
                "source_order": index,
                "winner": f"Alpha {index}",
                "weight_class": "Lightweight" if index % 2 else "Welterweight",
                "a_prior_fights": index % 10,
                "b_prior_fights": (index + 2) % 10,
                "a_prior_wins": index % 5,
                "b_prior_wins": (index + 1) % 5,
                "a_prior_finishes": index % 4,
                "b_prior_finishes": (index + 1) % 4,
                "a_prior_decisions": index % 3,
                "b_prior_decisions": (index + 2) % 3,
                "minimum_history_count": index % 6,
                "finish_binary": finish,
                "goes_distance_binary": 1 - finish,
                "method_class": method,
                "round_number": 3 if method == "Decision" else (1 if round_phase == "early" else 2),
                "round_phase_class": round_phase,
                "combined_sig_strikes": 45 + index,
                "fighter_a_sig_strikes": 20 + index,
                "fighter_b_sig_strikes": 15 + index,
                "grappling_heavy_binary": float(index % 2),
                "fighter_a_takedowns": index % 3,
                "fighter_b_takedowns": (index + 1) % 3,
            }
        )
    return pd.DataFrame(records)


def test_backtest_uses_newer_chronological_fights_as_test_set():
    payload, predictions = run_backtest(
        _synthetic_dataset(),
        test_size=0.2,
        all_test_fights=True,
        min_train_rows=10,
        min_test_rows=5,
    )

    assert payload["split"]["final_test_held_out"] is True
    assert payload["split"]["date_range_train"]["max"] < payload["summary"]["date_range"]["min"]
    assert predictions


def test_backtest_prediction_records_hide_result_features_until_scoring():
    payload, predictions = run_backtest(
        _synthetic_dataset(),
        test_size=0.2,
        limit=8,
        min_train_rows=10,
        min_test_rows=5,
    )
    record = predictions[0]

    assert set(record["prediction_feature_names"]).isdisjoint(FORBIDDEN_BACKTEST_INPUTS)
    assert record["forbidden_inputs_used"] == []
    assert "actual_result" in record
    assert "scoring" in record
    assert payload["blind_simulation"]["final_test_used_for_calibration"] is False


def test_backtest_scores_models_and_baselines():
    payload, _predictions = run_backtest(
        _synthetic_dataset(),
        test_size=0.2,
        all_test_fights=True,
        by_segment=True,
        min_train_rows=10,
        min_test_rows=5,
    )

    finish = payload["models"]["finish_model"]
    assert finish["available"] is True
    assert finish["fights_tested"] > 0
    assert "baseline_metric" in finish
    assert "relative_improvement" in finish
    assert "beats_baseline" in finish
    assert payload["overall_ranking"]


def test_backtest_keeps_prop_scoring_independent_from_winner():
    _payload, predictions = run_backtest(
        _synthetic_dataset(),
        test_size=0.2,
        limit=10,
        min_train_rows=10,
        min_test_rows=5,
    )

    assert any(record["scoring"]["fighter_1_over_50_sig_strikes_correct"] for record in predictions)
    assert all(record["scoring"]["winner_model_correct"] is None for record in predictions)


def test_backtest_skips_unavailable_models_honestly():
    payload, _predictions = run_backtest(
        _synthetic_dataset(20),
        test_size=0.2,
        all_test_fights=True,
        min_train_rows=50,
        min_test_rows=10,
    )

    assert payload["models"]["winner_model"]["status"] == "skipped"
    assert payload["models"]["odds_calibration_model"]["status"] == "skipped"
    assert payload["summary"]["models_skipped"]


def test_round_family_carries_selected_interactions_for_runtime_columns():
    interaction = {
        "name": "int__fighter_1_striker_score_x_fighter_2_strike_absorption_weakness",
        "kind": "strength_vs_weakness",
        "input_features": ("fighter_1_striker_score", "fighter_2_strike_absorption_weakness"),
        "groups": ("striking", "opponent_weakness"),
        "expression": "strength_vs_weakness",
    }
    models = {
        "over_2_5_model": {
            "available": True,
            "feature_names": ["fighter_1_striker_score", interaction["name"]],
            "classes": ["0", "1"],
            "model": object(),
            "interaction_feature_count": 1,
            "selected_interactions": [interaction],
            "interaction_selection_status": "selected",
            "train_rows": 100,
            "test_rows": 25,
        }
    }

    family = round_family_backtest_model(models)

    assert family["selected_interactions"] == [interaction]
    assert family["interaction_feature_count"] == 1
    assert family["interaction_selection_status"] == "selected"


def test_backtest_segment_keys_normalize_weight_class_case():
    rows = pd.DataFrame(
        {
            "weight_class": ["Bantamweight"] * 30 + ["bantamweight"] * 30 + ["Bantamweight Bout"] * 30,
            "minimum_history_count": [5] * 90,
            "finish_binary": ["1"] * 90,
            "_pred": ["1"] * 90,
        }
    )

    segments = backtest_segments(rows, "finish_binary")

    assert list(key for key in segments if key.startswith("weight_class:")) == ["weight_class:bantamweight"]
    assert segments["weight_class:bantamweight"]["rows"] == 90


def test_backtest_examples_skip_compatibility_aliases():
    prediction = {
        "fight_id": "fight-1",
        "event_date": "2025-01-01",
        "fighter_1": "Alpha",
        "fighter_2": "Beta",
        "models_run": {
            "fight_duration_model": {"available": True, "predicted_class": "1", "probabilities": {"1": 0.8}},
            "finish_model": {"available": True, "predicted_class": "1", "probabilities": {"1": 0.8}},
            "goes_distance_model": {"available": True, "predicted_class": "0", "probabilities": {"0": 0.8}},
            "method_model": {"available": True, "predicted_class": "Decision", "probabilities": {"Decision": 0.8}},
        },
        "actual_result": {},
        "scoring": {
            "fight_duration_model_correct": True,
            "finish_model_correct": True,
            "goes_distance_correct": True,
            "method_model_correct": True,
        },
    }

    result = examples([prediction])
    models = {row["model"] for row in result["best_predictions"]}

    assert "fight_duration_model" in models
    assert "finish_model" not in models
    assert "goes_distance_model" not in models
    assert "method_model" not in models
