"""Kaggle adapter facade for local raw dataset folders."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from ufc_predictor.training.importers.csv_importer import import_training_csvs
from ufc_predictor.training.targets import build_bettor_targets


def adapt_kaggle_dataset(dataset_key: str, folder: str | Path, dry_run: bool = True) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame, report = import_training_csvs(folder, dry_run=dry_run)
    normalized = normalize_common_columns(frame, dataset_key)
    if not normalized.empty:
        target_input = normalized.rename(columns={"fighter_1_name": "f_1_name", "fighter_2_name": "f_2_name"})
        target_input["winner"] = normalized.get("winner_name")
        targeted, target_report = build_bettor_targets(target_input)
        for column in targeted.columns:
            if column not in normalized.columns and column in {
                "f1_wins",
                "invalid_target_reason",
                "fighter_1_over_25_sig_strikes",
                "fighter_1_over_50_sig_strikes",
                "fighter_1_over_75_sig_strikes",
                "fighter_2_over_25_sig_strikes",
                "fighter_2_over_50_sig_strikes",
                "fighter_2_over_75_sig_strikes",
                "fighter_1_over_0_5_takedowns",
                "fighter_1_over_1_5_takedowns",
                "fighter_1_over_2_5_takedowns",
                "fighter_2_over_0_5_takedowns",
                "fighter_2_over_1_5_takedowns",
                "fighter_2_over_2_5_takedowns",
                "fighter_1_control_time_over_300_seconds",
                "fighter_2_control_time_over_300_seconds",
            }:
                normalized[column.replace("f1_wins", "f1_wins_safe")] = targeted[column]
    else:
        target_report = None
    adapter_report = {
        "dataset_key": dataset_key,
        "adapter": "kaggle_generic",
        "import_report": report.to_dict(),
        "target_report": target_report.to_dict() if target_report else None,
        "warnings": report.warnings,
    }
    return normalized, adapter_report


def normalize_common_columns(frame: pd.DataFrame, dataset_key: str) -> pd.DataFrame:
    if frame.empty:
        return pd.DataFrame()
    out = frame.copy()
    rename = {
        "source_id": "source_row_id",
        "fighter_1": "fighter_1_name",
        "fighter_2": "fighter_2_name",
        "fighter_a_sig_strikes": "fighter_1_sig_strikes_landed",
        "fighter_b_sig_strikes": "fighter_2_sig_strikes_landed",
        "fighter_a_sig_strikes_attempted": "fighter_1_sig_strikes_attempted",
        "fighter_b_sig_strikes_attempted": "fighter_2_sig_strikes_attempted",
        "fighter_a_takedowns": "fighter_1_takedowns_landed",
        "fighter_b_takedowns": "fighter_2_takedowns_landed",
        "fighter_a_takedowns_attempted": "fighter_1_takedowns_attempted",
        "fighter_b_takedowns_attempted": "fighter_2_takedowns_attempted",
        "fighter_a_control_time_seconds": "fighter_1_control_time_seconds",
        "fighter_b_control_time_seconds": "fighter_2_control_time_seconds",
        "round": "finish_round",
        "time": "finish_time",
    }
    out = out.rename(columns={old: new for old, new in rename.items() if old in out.columns})
    out["source_dataset"] = dataset_key
    out["method_class"] = out.get("method_group", out.get("method"))
    out["went_distance"] = out.get("goes_distance_binary")
    if "went_distance" in out.columns:
        out["fight_finished"] = out["went_distance"].map(lambda value: None if pd.isna(value) else int(not bool(value)))
    return out
