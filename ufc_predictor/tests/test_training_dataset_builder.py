import pandas as pd

from ufc_predictor.training.dataset_builder import (
    build_training_rows,
    ends_before_round_3_label,
    finish_in_round_1_label,
    normalize_method,
    normalize_result_type,
    over_round_half_label,
    parse_round_time_seconds,
    round_phase_label,
)
from ufc_predictor.training.split import chronological_split


def test_label_normalization_for_prop_models():
    assert normalize_method("KO/TKO") == "KO/TKO"
    assert normalize_method("SUB") == "Submission"
    assert normalize_method("U-DEC") == "Decision"
    assert normalize_method("DQ") == "Other"
    assert normalize_result_type("No Contest") == "nc"
    assert normalize_result_type("Overturned") == "nc"
    assert normalize_result_type("Draw") == "draw"
    assert round_phase_label(1, False) == "early"
    assert round_phase_label(2, False) == "middle"
    assert round_phase_label(5, False) == "late"
    assert round_phase_label(3, True) == "decision"
    assert parse_round_time_seconds("2:31") == 151
    assert over_round_half_label(2, 151, False, threshold_round=1) == 1
    assert over_round_half_label(2, 149, False, threshold_round=1) == 0
    assert over_round_half_label(2, None, False, threshold_round=1) is None
    assert over_round_half_label(3, 151, False, threshold_round=2) == 1
    assert ends_before_round_3_label(2, False) == 1
    assert ends_before_round_3_label(3, False) == 0
    assert finish_in_round_1_label(1, False) == 1
    assert finish_in_round_1_label(2, False) == 0


def test_dataset_builder_uses_prior_history_only():
    fights = pd.DataFrame(
        [
            {
                "event": "Event 1",
                "event_date": "2024-01-01",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "result": "win",
                "method": "KO/TKO",
                "round": 1,
                "time": "1:00",
            },
            {
                "event": "Event 2",
                "event_date": "2024-06-01",
                "fighter_1": "Alpha",
                "fighter_2": "Gamma",
                "result": "win",
                "method": "U-DEC",
                "round": 3,
                "time": "5:00",
            },
        ]
    )

    dataset, audit = build_training_rows(fights)

    assert len(dataset) == 2
    assert dataset.iloc[0]["a_prior_fights"] == 0
    assert dataset.iloc[1]["a_prior_fights"] == 1
    assert dataset.iloc[1]["a_prior_finishes"] == 1
    assert dataset.iloc[1]["finish_binary"] == 0
    assert dataset.iloc[1]["goes_distance_binary"] == 1
    assert dataset.iloc[0]["finish_type_class"] == "KO/TKO"
    assert pd.isna(dataset.iloc[1]["finish_type_class"])
    assert dataset.iloc[0]["over_1_5_binary"] == 0
    assert dataset.iloc[1]["over_1_5_binary"] == 1
    assert dataset.iloc[0]["ends_before_round_3_binary"] == 1
    assert dataset.iloc[1]["ends_before_round_3_binary"] == 0
    assert dataset.iloc[0]["finish_in_round_1_binary"] == 1
    assert dataset.iloc[1]["finish_in_round_1_binary"] == 0
    assert audit.label_availability["finish_binary"] == 2
    assert audit.label_availability["fighter_a_sig_strikes"] == 0


def test_non_win_results_do_not_create_prop_model_labels():
    fights = pd.DataFrame(
        [
            {
                "event": "Event 1",
                "event_date": "2024-01-01",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "result": "No Contest",
                "method": "No Contest",
                "round": 1,
                "time": "1:00",
            },
            {
                "event": "Event 2",
                "event_date": "2024-06-01",
                "fighter_1": "Gamma",
                "fighter_2": "Delta",
                "result": "Draw",
                "method": "Decision - Majority",
                "round": 3,
                "time": "5:00",
            },
        ]
    )

    dataset, audit = build_training_rows(fights)

    assert audit.label_availability["finish_binary"] == 0
    assert dataset["finish_binary"].isna().all()
    assert dataset["method_class"].isna().all()
    assert dataset["round_phase_class"].isna().all()


def test_style_and_weakness_scores_use_prior_fights_only():
    fights = pd.DataFrame(
        [
            {
                "event": "Event 1",
                "event_date": "2024-01-01",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "result": "win",
                "method": "KO/TKO",
                "round": 1,
                "time": "1:00",
                "fighter_a_sig_strikes": 40,
                "fighter_b_sig_strikes": 5,
                "fighter_a_sig_strikes_attempted": 80,
                "fighter_b_sig_strikes_attempted": 20,
                "fighter_a_takedowns": 2,
                "fighter_b_takedowns": 0,
                "fighter_a_takedowns_attempted": 4,
                "fighter_b_takedowns_attempted": 1,
                "fighter_a_control_time_seconds": 120,
                "fighter_b_control_time_seconds": 5,
            },
            {
                "event": "Event 2",
                "event_date": "2024-06-01",
                "fighter_1": "Alpha",
                "fighter_2": "Gamma",
                "result": "win",
                "method": "U-DEC",
                "round": 3,
                "time": "5:00",
                "fighter_a_sig_strikes": 200,
                "fighter_b_sig_strikes": 1,
                "fighter_a_sig_strikes_attempted": 250,
                "fighter_b_sig_strikes_attempted": 3,
                "fighter_a_takedowns": 8,
                "fighter_b_takedowns": 0,
                "fighter_a_takedowns_attempted": 10,
                "fighter_b_takedowns_attempted": 0,
                "fighter_a_control_time_seconds": 600,
                "fighter_b_control_time_seconds": 0,
            },
        ]
    )

    dataset, _audit = build_training_rows(fights)
    first = dataset.iloc[0]
    second = dataset.iloc[1]

    assert pd.isna(first["fighter_1_striker_score"])
    assert second["fighter_1_striker_score"] == 0.8
    assert second["fighter_1_high_volume_striker_score"] == 0.8889
    assert second["fighter_1_wrestler_score"] == 0.6667
    assert second["fighter_1_power_finisher_score"] == 1.0
    assert second["fighter_1_strike_absorption_weakness"] == 0.1
    assert second["fighter_1_striker_score"] < 1.0
    assert second["fighter_1_control_fighter_score"] == 0.4


def test_chronological_split_preserves_order():
    train, test = chronological_split([1, 2, 3, 4, 5], test_size=0.4)

    assert train == [1, 2, 3]
    assert test == [4, 5]
