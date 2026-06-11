from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import yaml

import scripts.refresh_kaggle_datasets as refresh
from scripts.audit_kaggle_odds_timestamps import audit_odds_directory
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
