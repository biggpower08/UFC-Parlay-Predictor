"""Matchup feature vectors for training and prediction."""

import numpy as np
import pandas as pd

from ufc_predictor.feedback.note_parser import NOTE_FLAG_NAMES, note_flags_to_delta_features
from ufc_predictor.utils.helpers import normalize_name, safe_float

BASE_FEATURE_NAMES = [
    "delta_slpm",
    "delta_str_acc",
    "delta_str_def",
    "delta_sapm",
    "delta_td_avg",
    "delta_td_acc",
    "delta_td_def",
    "delta_sub_avg",
    "delta_reach",
    "delta_elo",
    "delta_points_p4p",
    "delta_rank_p4p",
    "delta_points_dom",
    "delta_rank_dom",
    "elo_expected_a",
]

FEATURE_NAMES = BASE_FEATURE_NAMES + [f"delta_{f}" for f in NOTE_FLAG_NAMES]

STAT_COL_MAP = {
    "delta_slpm": "significant_strikes_landed_per_minute",
    "delta_str_acc": "significant_striking_accuracy",
    "delta_str_def": "significant_strike_defence",
    "delta_sapm": "significant_strikes_absorbed_per_minute",
    "delta_td_avg": "average_takedowns_landed_per_15_minutes",
    "delta_td_acc": "takedown_accuracy",
    "delta_td_def": "takedown_defense",
    "delta_sub_avg": "average_submissions_attempted_per_15_minutes",
    "delta_reach": "reach_in_cm",
}


def _safe(row, col, default=0.0):
    if col not in row.index or pd.isna(row[col]):
        return default
    return safe_float(row[col], default)


def build_matchup_features(fighter_a_row, fighter_b_row, note_flags_a=None, note_flags_b=None):
    feats = {}
    for feat, col in STAT_COL_MAP.items():
        feats[feat] = _safe(fighter_a_row, col) - _safe(fighter_b_row, col)

    elo_a = _safe(fighter_a_row, "elo", 1000)
    elo_b = _safe(fighter_b_row, "elo", 1000)
    feats["delta_elo"] = elo_a - elo_b
    feats["elo_expected_a"] = 1 / (1 + 10 ** ((elo_b - elo_a) / 400))

    for prefix in ("p4p", "dom"):
        feats[f"delta_points_{prefix}"] = _safe(fighter_a_row, f"points_{prefix}") - _safe(
            fighter_b_row, f"points_{prefix}"
        )
        feats[f"delta_rank_{prefix}"] = _safe(fighter_b_row, f"rank_{prefix}") - _safe(
            fighter_a_row, f"rank_{prefix}"
        )

    note_deltas = note_flags_to_delta_features(note_flags_a or {}, note_flags_b or {})
    feats.update(note_deltas)
    return {k: feats.get(k, 0.0) for k in FEATURE_NAMES}


def features_to_vector(feature_dict) -> np.ndarray:
    return np.array([feature_dict[k] for k in FEATURE_NAMES], dtype=float)


def master_index_by_name(master_df):
    indexed = {}
    for _, row in master_df.iterrows():
        key = row["_search_name"]
        if key and key not in indexed:
            indexed[key] = row
    return indexed


def build_training_dataset(fights_df, master_df, random_state=42):
    rng = np.random.default_rng(random_state)
    by_name = master_index_by_name(master_df)
    X_list = []
    y_list = []

    fights = fights_df.copy()
    if "result" not in fights.columns:
        fights = fights.reset_index()
    fights["result"] = (
        fights["result"].astype(str).str.lower().str.strip().str.split("\n").str[0]
    )

    for _, row in fights.iterrows():
        if row["result"] != "win":
            continue
        w_key = normalize_name(row["fighter_1"])
        l_key = normalize_name(row["fighter_2"])
        if w_key not in by_name or l_key not in by_name:
            continue
        w_row, l_row = by_name[w_key], by_name[l_key]
        if rng.random() < 0.5:
            a_row, b_row, label = w_row, l_row, 1
        else:
            a_row, b_row, label = l_row, w_row, 0
        X_list.append(features_to_vector(build_matchup_features(a_row, b_row)))
        y_list.append(label)

    if not X_list:
        return np.zeros((0, len(FEATURE_NAMES))), np.array([])
    return np.vstack(X_list), np.array(y_list, dtype=int)
