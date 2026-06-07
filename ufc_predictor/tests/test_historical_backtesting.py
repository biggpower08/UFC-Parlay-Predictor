import pandas as pd

from scripts.backtest_historical_fights import (
    FORBIDDEN_BACKTEST_INPUTS,
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
