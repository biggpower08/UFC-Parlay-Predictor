"""Feature and label builders for dedicated prop models."""

from __future__ import annotations

import numpy as np

from ufc_predictor.features.matchup_builder import FEATURE_NAMES, build_matchup_features, features_to_vector, master_index_by_name
from ufc_predictor.utils.helpers import normalize_name

DECISION_METHODS = {"u-dec", "s-dec", "m-dec", "dec", "decision"}


def build_prop_datasets(fights_df, master_df, random_state: int = 42) -> dict:
    by_name = master_index_by_name(master_df)
    rows = {
        "finish_model": {"X": [], "y": []},
        "goes_distance_model": {"X": [], "y": []},
        "method_model": {"X": [], "y": []},
        "round_model": {"X": [], "y": []},
    }

    fights = fights_df.copy()
    fights["result"] = fights["result"].astype(str).str.lower().str.strip().str.split("\n").str[0]

    for _, fight in fights.iterrows():
        if fight["result"] != "win":
            continue
        winner_key = normalize_name(fight.get("fighter_1"))
        loser_key = normalize_name(fight.get("fighter_2"))
        if winner_key not in by_name or loser_key not in by_name:
            continue

        winner_row = by_name[winner_key]
        loser_row = by_name[loser_key]
        method = normalize_method(fight.get("method"))
        is_decision = method == "decision"
        finish_label = 0 if is_decision else 1
        round_phase = round_phase_label(fight.get("round"), is_decision)
        winner_features = features_to_vector(build_matchup_features(winner_row, loser_row))
        loser_features = features_to_vector(build_matchup_features(loser_row, winner_row))

        for features in (winner_features, loser_features):
            rows["finish_model"]["X"].append(features)
            rows["finish_model"]["y"].append(finish_label)
            rows["goes_distance_model"]["X"].append(features)
            rows["goes_distance_model"]["y"].append(1 if is_decision else 0)

        rows["method_model"]["X"].append(winner_features)
        rows["method_model"]["y"].append(method)
        rows["round_model"]["X"].append(winner_features)
        rows["round_model"]["y"].append(round_phase)

    return {
        name: {
            "X": np.vstack(payload["X"]) if payload["X"] else np.zeros((0, len(FEATURE_NAMES))),
            "y": np.array(payload["y"]),
        }
        for name, payload in rows.items()
    }


def normalize_method(value) -> str:
    method = str(value or "").strip().lower()
    if method in DECISION_METHODS or "dec" in method:
        return "decision"
    if "sub" in method:
        return "submission"
    if "ko" in method or "tko" in method:
        return "ko_tko"
    return "other_finish"


def round_phase_label(round_value, is_decision: bool) -> str:
    if is_decision:
        return "decision"
    try:
        round_number = int(float(round_value))
    except (TypeError, ValueError):
        return "unknown_finish_phase"
    if round_number <= 1:
        return "early"
    if round_number <= 3:
        return "middle"
    return "late"
