import pandas as pd

from ufc_predictor.training.dataset_builder import build_training_rows, normalize_method, round_phase_label
from ufc_predictor.training.split import chronological_split


def test_label_normalization_for_prop_models():
    assert normalize_method("KO/TKO") == "KO/TKO"
    assert normalize_method("SUB") == "Submission"
    assert normalize_method("U-DEC") == "Decision"
    assert normalize_method("DQ") == "Other"
    assert round_phase_label(1, False) == "early"
    assert round_phase_label(2, False) == "middle"
    assert round_phase_label(5, False) == "late"
    assert round_phase_label(3, True) == "decision"


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
    assert audit.label_availability["finish_binary"] == 2
    assert audit.label_availability["fighter_a_sig_strikes"] == 0


def test_chronological_split_preserves_order():
    train, test = chronological_split([1, 2, 3, 4, 5], test_size=0.4)

    assert train == [1, 2, 3]
    assert test == [4, 5]
