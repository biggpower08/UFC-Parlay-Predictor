from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.build_master_project_status import main as build_master_status
from ufc_predictor.training.dataset_builder import build_training_rows
from ufc_predictor.training.source_eligibility import (
    eligible_sources_for_model,
    filter_rows_for_model_source_eligibility,
    model_source_status,
    source_is_eligible_for_model,
)


ROOT = Path(__file__).resolve().parents[2]


def test_master_status_file_generated_and_contains_required_sections():
    assert build_master_status([]) == 0
    text = (ROOT / "docs" / "PROJECT_MASTER_STATUS.md").read_text(encoding="utf-8")

    required_sections = [
        "Plain-English Project Summary",
        "Current Production Readiness Status",
        "Current Model Status Table",
        "Current Dataset / Source Status",
        "Current Source-Eligibility Rules",
        "Current Source-Holdout / Source-Transfer Status",
        "Current Interaction Discovery Status",
        "Current Calibration Status",
        "Current UI / Product Status",
        "Current Backend/API Status",
        "Current Deployment / Render Status",
        "Current Supabase / Database Status",
        "Current Repo Hygiene Status",
        "What Is Safe To Show Publicly",
        "What Must Stay Experimental",
        "What Is Blocked",
        "Next 2-Week Build Plan",
        "Next 4-Week Production Plan",
        "Files/Folders Not To Commit",
    ]
    for section in required_sections:
        assert section in text

    assert "winner_model` is `high_confidence_only" in text
    assert "production_candidate" in text
    assert "weak_or_failed_baseline" in text
    assert "blocked" in text
    assert "ufc_stats_complete` should be treated primarily as a stat-rich source" in text
    assert "No model artifacts are packaged yet" in text


def test_master_status_generator_handles_missing_optional_reports(tmp_path):
    docs = tmp_path / "docs"
    processed = tmp_path / "processed"
    docs.mkdir()
    processed.mkdir()
    output = docs / "PROJECT_MASTER_STATUS.md"
    index = docs / "PROJECT_MASTER_INDEX.md"

    assert build_master_status(
        [
            "--docs-dir",
            str(docs),
            "--processed-dir",
            str(processed),
            "--output",
            str(output),
            "--index-output",
            str(index),
            "--source-eligibility-json",
            str(processed / "source_eligibility_rules.json"),
            "--source-eligibility-md",
            str(docs / "source_eligibility_rules.md"),
        ]
    ) == 0
    text = output.read_text(encoding="utf-8")
    assert "not available yet" in text
    assert "Current Model Status Table" in text


def test_source_eligibility_blocks_ufc_stats_complete_result_models_but_allows_stat_models():
    assert model_source_status("ufc_stats_complete", "fight_duration_model").startswith("ineligible")
    assert source_is_eligible_for_model("ufc_stats_complete", "strike_volume_model")
    assert source_is_eligible_for_model("ufc_stats_complete", "takedown_control_model")
    assert "ufc_stats_complete" not in eligible_sources_for_model("winner_model")

    rows = pd.DataFrame(
        {
            "source_dataset": ["ufc_stats_complete", "ufc_1994_2026"],
            "finish_binary": [1, 0],
            "combined_strike_volume_bucket": ["high", "low"],
        }
    )
    duration_rows = filter_rows_for_model_source_eligibility(rows, "fight_duration_model")
    strike_rows = filter_rows_for_model_source_eligibility(rows, "strike_volume_model")

    assert duration_rows["source_dataset"].tolist() == ["ufc_1994_2026"]
    assert "ufc_stats_complete" in strike_rows["source_dataset"].tolist()


def test_no_contest_draw_unknown_rows_do_not_create_fake_labels_for_source_eligibility():
    fights = pd.DataFrame(
        [
            {
                "event": "Test",
                "event_date": "2024-01-01",
                "fighter_1": "A",
                "fighter_2": "B",
                "result": "No Contest",
                "method": "No Contest",
                "round": 1,
                "source_dataset": "ufc_stats_complete",
            },
            {
                "event": "Test",
                "event_date": "2024-01-02",
                "fighter_1": "C",
                "fighter_2": "D",
                "result": "Draw",
                "method": "Decision - Majority",
                "round": 3,
                "source_dataset": "ufc_stats_complete",
            },
        ]
    )

    dataset, audit = build_training_rows(fights)

    assert audit.label_availability["finish_binary"] == 0
    assert dataset["finish_binary"].isna().all()
    assert dataset["method_class"].isna().all()
    assert dataset["round_phase_class"].isna().all()


def test_source_eligibility_json_exists_and_mentions_ufc_stats_complete_limitation():
    path = ROOT / "ufc_predictor" / "data" / "processed" / "source_eligibility_rules.json"
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert "ufc_stats_complete" in payload
    assert "universal duration labels" in payload["ufc_stats_complete"]["unsafe_uses"]
    assert payload["ufc_stats_complete"]["model_eligibility"]["strike_volume_model"] == "eligible_stat_labels"
