import pandas as pd

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
