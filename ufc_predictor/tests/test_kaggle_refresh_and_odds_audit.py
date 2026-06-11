from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import yaml

import scripts.refresh_kaggle_datasets as refresh
from scripts.audit_kaggle_odds_timestamps import audit_odds_directory
from scripts.normalize_kaggle_odds_snapshots import (
    normalize_odds_file,
    parse_odds,
    prediction_modes,
    write_outputs,
)
from scripts.refresh_kaggle_datasets import load_dataset_manifest


ROOT = Path(__file__).resolve().parents[2]


def test_kaggle_dataset_manifest_parses_and_has_required_fields():
    datasets = load_dataset_manifest(Path("config/kaggle_datasets.yaml"))

    assert datasets
    required = {"id", "kaggle_ref", "category", "enabled", "train_usage"}
    for entry in datasets:
        assert required.issubset(entry), entry
    assert any(entry["id"] == "ufc_betting_odds_daily" for entry in datasets)


def test_manifest_yaml_has_timestamped_odds_candidate():
    data = yaml.safe_load(Path("config/kaggle_datasets.yaml").read_text(encoding="utf-8"))
    odds = {entry["id"]: entry for entry in data["datasets"]}["ufc_betting_odds_daily"]

    assert odds["kaggle_ref"] == "jerzyszocik/ufc-betting-odds-daily-dataset"
    assert odds["requires_timestamp_audit"] is True
    assert odds["train_usage"] == "blocked_until_timestamp_audit_passes"


def test_refresh_script_dry_run_does_not_require_credentials():
    result = subprocess.run(
        [
            "C:\\venvs\\mma-ai\\Scripts\\python.exe",
            "scripts\\refresh_kaggle_datasets.py",
            "--dataset-id",
            "ufc_betting_odds_daily",
            "--dry-run",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0
    payload = json.loads(result.stdout)
    assert payload["dry_run"] is True
    assert payload["datasets"][0]["dataset_id"] == "ufc_betting_odds_daily"


def test_missing_kaggle_credentials_message_is_clear(monkeypatch, tmp_path):
    monkeypatch.delenv("KAGGLE_USERNAME", raising=False)
    monkeypatch.delenv("KAGGLE_KEY", raising=False)
    monkeypatch.setenv("KAGGLE_CONFIG_DIR", str(tmp_path / "missing_kaggle_config"))
    monkeypatch.setattr(refresh.Path, "home", lambda: tmp_path / "fake_home")

    assert refresh.kaggle_credentials_present() is False


def test_odds_timestamp_audit_rejects_missing_timestamps(tmp_path):
    odds_dir = tmp_path / "odds"
    odds_dir.mkdir()
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-10T00:00:00Z",
                "fighter": "Alpha",
                "bookmaker": "Example",
                "market": "moneyline",
                "american_odds": -120,
            }
        ]
    ).to_csv(odds_dir / "odds.csv", index=False)

    report = audit_odds_directory(odds_dir)

    assert report["status"] == "blocked_missing_snapshot_timestamps"
    assert report["odds_calibration_model_status"] == "blocked"


def test_odds_timestamp_audit_rejects_post_event_snapshots(tmp_path):
    odds_dir = tmp_path / "odds"
    odds_dir.mkdir()
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-10T00:00:00Z",
                "snapshot_timestamp": "2024-01-11T00:00:00Z",
                "fighter": "Alpha",
                "bookmaker": "Example",
                "market": "moneyline",
                "american_odds": -120,
            }
        ]
    ).to_csv(odds_dir / "odds.csv", index=False)

    report = audit_odds_directory(odds_dir)

    assert report["status"] == "blocked_post_event_snapshots"
    assert report["totals"]["snapshot_after_event_rows"] == 1


def test_odds_timestamp_audit_keeps_ambiguous_timezone_research_only(tmp_path):
    odds_dir = tmp_path / "odds"
    odds_dir.mkdir()
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-10T00:00:00Z",
                "snapshot_timestamp": "2024-01-09 12:00:00",
                "fighter": "Alpha",
                "bookmaker": "Example",
                "market": "method ko tko",
                "american_odds": 200,
            }
        ]
    ).to_csv(odds_dir / "odds.csv", index=False)

    report = audit_odds_directory(odds_dir)

    assert report["status"] == "research_only_timezone_ambiguous"
    assert report["safe_for"]["production_odds_model"] == "blocked"


def test_odds_timestamp_audit_detects_daily_odds_columns(tmp_path):
    odds_dir = tmp_path / "odds"
    odds_dir.mkdir()
    pd.DataFrame(
        [
            {
                "fight_url": "http://ufcstats.com/fight-details/test",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "odds_1": 1.8,
                "odds_2": 2.1,
                "f1_ko_odds": 4.0,
                "f2_sub_odds": 5.5,
                "event_date": "2026-01-10",
                "adding_date": "2026-01-09T12:00:00Z",
                "source": "ExampleBook",
                "region": "us",
            }
        ]
    ).to_csv(odds_dir / "UFC_betting_odds.csv", index=False)

    report = audit_odds_directory(odds_dir)
    file_report = report["files"][0]

    assert file_report["selected_event_date_column"] == "event_date"
    assert file_report["selected_snapshot_timestamp_column"] == "adding_date"
    assert "source" in file_report["bookmaker_columns"]
    assert file_report["moneyline_rows"] == 1
    assert file_report["method_prop_rows"] == 1
    assert report["totals"]["snapshot_before_or_equal_event_rows"] == 1


def test_downloaded_daily_odds_file_audits_if_present():
    path = Path("data/imports/kaggle/ufc_betting_odds_daily/UFC_betting_odds.csv")
    if not path.is_file():
        return

    report = audit_odds_directory(path.parent)
    file_report = next(item for item in report["files"] if item["source_file"].endswith("UFC_betting_odds.csv"))

    assert file_report["rows"] > 1000
    assert file_report["selected_event_date_column"] == "event_date"
    assert file_report["selected_snapshot_timestamp_column"] == "adding_date"
    assert report["status"] != "timestamp_audit_passed_research_only"
    assert report["odds_calibration_model_status"] == "blocked"


def test_weekly_powershell_script_exists():
    assert Path("scripts/run_weekly_kaggle_refresh.ps1").is_file()


def test_master_status_records_current_odds_audit_status():
    text = Path("docs/PROJECT_MASTER_STATUS.md").read_text(encoding="utf-8")

    assert "blocked_missing_snapshot_timestamps" in text
    assert "UFC_betting_odds.csv" in text


def test_raw_kaggle_data_paths_are_ignored():
    protected = [
        "data/imports/kaggle/ufc_betting_odds_daily/raw.csv",
        "data/imports/kaggle/_download_manifest.json",
        "kaggle.json",
    ]
    for path in protected:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", path],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, f"{path} is not protected by .gitignore"


def test_odds_normalizer_converts_decimal_and_american_odds():
    decimal = parse_odds(2.5)
    positive_american = parse_odds(150)
    negative_american = parse_odds(-120)

    assert decimal == {"american_odds": None, "decimal_odds": 2.5, "implied_probability": 0.4}
    assert positive_american == {"american_odds": 150.0, "decimal_odds": 2.5, "implied_probability": 0.4}
    assert negative_american == {"american_odds": -120.0, "decimal_odds": 1.833333, "implied_probability": 0.54545455}
    assert parse_odds(0) is None
    assert parse_odds(1) is None
    assert parse_odds("not odds") is None


def test_odds_normalizer_filters_timestamp_unsafe_rows_and_maps_markets(tmp_path):
    odds_file = tmp_path / "UFC_betting_odds.csv"
    pd.DataFrame(
        [
            {
                "fight_url": "http://ufcstats.com/fight-details/safe",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "odds_1": 1.8,
                "odds_2": 2.1,
                "f1_ko_odds": 4.0,
                "f2_ko_odds": None,
                "f1_sub_odds": 8.0,
                "f2_sub_odds": None,
                "f1_dec_odds": 3.5,
                "f2_dec_odds": None,
                "event_date": "2026-01-10T00:00:00Z",
                "adding_date": "2026-01-02T00:00:00Z",
                "source": "ExampleBook",
                "region": "us",
            },
            {
                "fight_url": "http://ufcstats.com/fight-details/missing-snapshot",
                "fighter_1": "Gamma",
                "fighter_2": "Delta",
                "odds_1": 1.9,
                "odds_2": 2.0,
                "event_date": "2026-01-10T00:00:00Z",
                "adding_date": None,
                "source": "ExampleBook",
                "region": "us",
            },
            {
                "fight_url": "http://ufcstats.com/fight-details/post-event",
                "fighter_1": "Epsilon",
                "fighter_2": "Zeta",
                "odds_1": 1.9,
                "odds_2": 2.0,
                "event_date": "2026-01-10T00:00:00Z",
                "adding_date": "2026-01-11T00:00:00Z",
                "source": "ExampleBook",
                "region": "us",
            },
        ]
    ).to_csv(odds_file, index=False)

    result = normalize_odds_file(odds_file)
    summary = result["summary"]
    snapshots = result["snapshots"]

    assert summary["accepted_raw_rows"] == 1
    assert summary["rejected_raw_rows"] == 2
    assert summary["rejected_snapshots_by_reason"]["missing_snapshot_timestamp"] == 1
    assert summary["rejected_snapshots_by_reason"]["snapshot_after_event"] == 1
    assert summary["normalized_market_counts"] == {
        "moneyline": 2,
        "ko_tko_prop": 1,
        "submission_prop": 1,
        "decision_prop": 1,
    }
    assert {snapshot["selection_side"] for snapshot in snapshots} == {"fighter_1", "fighter_2"}
    assert any(snapshot["market_type"] == "moneyline" and snapshot["selection"] == "Beta" for snapshot in snapshots)
    assert any(snapshot["prop_type"] == "ko_tko" and snapshot["selection"] == "Alpha" for snapshot in snapshots)
    assert all(snapshot["timestamp_audit_status"] == "timestamp_safe_prefight_candidate" for snapshot in snapshots)
    assert all("research_only" in snapshot["prediction_modes_allowed"] for snapshot in snapshots)
    assert summary["odds_calibration_model_status"] == "blocked"
    assert summary["odds_snapshots_preview_status"] == "research_only"


def test_odds_prediction_mode_tagging():
    event_date = pd.Timestamp("2026-01-10T00:00:00Z")

    assert "early_prefight_candidate" in prediction_modes(8, event_date)
    assert "day_before_candidate" in prediction_modes(1, event_date)
    assert "closing_line_candidate" in prediction_modes(0.5, event_date)
    assert "production_odds_model" not in prediction_modes(8, event_date)


def test_odds_normalizer_writes_small_preview_and_ignored_full_csv(tmp_path):
    odds_file = tmp_path / "UFC_betting_odds.csv"
    pd.DataFrame(
        [
            {
                "fight_url": "http://ufcstats.com/fight-details/safe",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "odds_1": 2.0,
                "odds_2": 2.0,
                "event_date": "2026-01-10T00:00:00Z",
                "adding_date": "2026-01-09T00:00:00Z",
                "source": "ExampleBook",
                "region": "us",
            }
        ]
    ).to_csv(odds_file, index=False)
    result = normalize_odds_file(odds_file)
    preview_json = tmp_path / "odds_snapshots_preview.json"
    summary_json = tmp_path / "odds_snapshots_preview_summary.json"
    full_csv = ROOT / "ufc_predictor" / "data" / "processed" / "training_imports" / "test_odds_snapshots_preview.csv"
    report_md = tmp_path / "odds_snapshot_normalization_report.md"

    try:
        write_outputs(result, preview_json, summary_json, full_csv, report_md, preview_limit=1)

        preview = json.loads(preview_json.read_text(encoding="utf-8"))
        summary = json.loads(summary_json.read_text(encoding="utf-8"))

        assert len(preview["snapshots"]) == 1
        assert summary["accepted_snapshots"] == 2
        assert "research-only" in report_md.read_text(encoding="utf-8")

        ignore_result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", str(full_csv.relative_to(ROOT))],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert ignore_result.returncode == 0
    finally:
        full_csv.unlink(missing_ok=True)


def test_odds_calibration_model_remains_blocked_after_odds_preview_status():
    registry = json.loads(Path("ufc_predictor/data/processed/model_registry.json").read_text(encoding="utf-8"))
    odds_model = registry["odds_calibration_model"]

    assert odds_model["status"] == "blocked"
    assert odds_model["production_status"] == "blocked"
    assert "trusted_prefight_odds_timestamps_missing" in odds_model["failed_gates"]
