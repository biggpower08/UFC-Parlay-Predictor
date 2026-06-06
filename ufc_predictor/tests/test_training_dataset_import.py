import pandas as pd

from ufc_predictor.training.importers import import_training_csvs


def test_importer_detects_supported_csv_and_normalizes_labels(tmp_path):
    input_dir = tmp_path / "imports"
    input_dir.mkdir()
    path = input_dir / "ufc_fight_stats.csv"
    pd.DataFrame(
        [
            {
                "event_name": "UFC Test",
                "event_date": "2024-01-01",
                "r_fighter": "Winner One",
                "b_fighter": "Loser One",
                "winner": "Winner One",
                "method": "KO/TKO",
                "round": 2,
                "R_SIG_STR.": "55 of 100",
                "B_SIG_STR.": "20 of 60",
                "R_TD": "1 of 3",
                "B_TD": "0 of 1",
                "R_CTRL": "2:30",
                "B_CTRL": "0:20",
            }
        ]
    ).to_csv(path, index=False)

    normalized, report = import_training_csvs(input_dir, dry_run=True)

    assert report.rows_normalized == 1
    assert report.label_availability["finish_binary"] == 1
    assert report.label_availability["fighter_a_sig_strikes"] == 1
    assert report.label_availability["fighter_a_takedowns"] == 1
    assert normalized.iloc[0]["fighter_1"] == "Winner One"
    assert normalized.iloc[0]["fighter_a_sig_strikes"] == 55
    assert normalized.iloc[0]["combined_100plus_sig_strikes"] == 0


def test_importer_reports_unknown_files_cleanly(tmp_path):
    input_dir = tmp_path / "imports"
    input_dir.mkdir()
    (input_dir / "notes.csv").write_text("name,value\nx,1\n", encoding="utf-8")

    normalized, report = import_training_csvs(input_dir, dry_run=True)

    assert normalized.empty
    assert report.unknown_files
    assert report.rows_normalized == 0
    assert any("No supported fight rows" in warning for warning in report.warnings)
    assert report.file_types[str(input_dir / "notes.csv")] == "unknown"


def test_importer_handles_missing_optional_strike_and_takedown_columns(tmp_path):
    input_dir = tmp_path / "imports"
    input_dir.mkdir()
    path = input_dir / "ufc_fight_results.csv"
    pd.DataFrame(
        [
            {
                "event_name": "UFC Test",
                "event_date": "2024-01-01",
                "winner": "Winner One",
                "loser": "Loser One",
                "method": "Decision - Unanimous",
                "round": 3,
            }
        ]
    ).to_csv(path, index=False)

    normalized, report = import_training_csvs(input_dir, dry_run=True)

    assert report.rows_normalized == 1
    assert report.label_availability["finish_binary"] == 1
    assert report.label_availability["fighter_a_sig_strikes"] == 0
    assert report.label_availability["fighter_a_takedowns"] == 0
    assert normalized.iloc[0]["goes_distance_binary"] == 1


def test_importer_detects_odds_file_without_normalizing_fake_fights(tmp_path):
    input_dir = tmp_path / "imports"
    input_dir.mkdir()
    path = input_dir / "odds_snapshots.csv"
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-01",
                "fighter": "Winner One",
                "sportsbook": "Example",
                "closing_odds": -120,
                "snapshot_date": "2023-12-31",
            }
        ]
    ).to_csv(path, index=False)

    normalized, report = import_training_csvs(input_dir, dry_run=True)

    assert normalized.empty
    assert report.file_types[str(path)] == "odds"
    assert report.odds_availability["files"] == 1
    assert report.odds_availability["rows"] == 1


def test_importer_deduplicates_fights_and_adds_source_identity(tmp_path):
    input_dir = tmp_path / "imports"
    input_dir.mkdir()
    path = input_dir / "ufc_fight_results.csv"
    row = {
        "event_name": "UFC Test",
        "event_date": "2024-01-01",
        "winner": "Winner One",
        "loser": "Loser One",
        "method": "Submission",
        "round": 1,
    }
    pd.DataFrame([row, row]).to_csv(path, index=False)

    normalized, report = import_training_csvs(input_dir, dry_run=True)

    assert report.duplicate_fights == 1
    assert report.rows_normalized == 1
    assert normalized.iloc[0]["fighter_a_normalized_name"] == "winner one"
    assert normalized.iloc[0]["source_id"]
