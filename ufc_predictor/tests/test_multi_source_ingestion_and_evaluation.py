import json
from pathlib import Path

import pandas as pd

from scripts.download_kaggle_datasets import main as download_main
from scripts.evaluate_model_accuracy import (
    chronological_train_validation_test_split,
    majority_baseline,
    relative_ranking,
)
from scripts.preprocess_imported_datasets import main as preprocess_main
from ufc_predictor.training.dataset_manifest import DATASET_MANIFEST
from ufc_predictor.training.deduping import add_deduping_columns, dedupe_summary
from ufc_predictor.training.importers.kaggle_adapter import adapt_kaggle_dataset
from ufc_predictor.training.targets import build_bettor_targets, safe_f1_wins


def test_dataset_manifest_includes_all_six_sources():
    expected = {
        "ufc_fight_forecast",
        "ufc_stats_complete",
        "ufc_1994_2026",
        "ufc_1994_2025",
        "mdabbert_ultimate",
        "mdabbert_2010_2020_odds",
        "ufc_datalab",
    }
    assert expected <= set(DATASET_MANIFEST)


def test_kaggle_download_script_list_and_dry_run(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["download_kaggle_datasets.py", "--list"])
    assert download_main() == 0
    listed = json.loads(capsys.readouterr().out)
    assert any(item["key"] == "ufc_stats_complete" for item in listed["datasets"])

    monkeypatch.setattr("sys.argv", ["download_kaggle_datasets.py", "--all", "--dry-run"])
    assert download_main() == 0
    dry_run = json.loads(capsys.readouterr().out)
    assert dry_run["dry_run"] is True


def test_adapter_detection_and_common_schema_normalization(tmp_path):
    source = tmp_path / "ufc_stats_complete"
    source.mkdir()
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-01",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "winner": "Alpha",
                "method": "KO/TKO",
                "round": 1,
                "result": "win",
                "fighter_a_sig_strikes_landed": 80,
                "fighter_b_sig_strikes_landed": 20,
            }
        ]
    ).to_csv(source / "fights.csv", index=False)

    frame, report = adapt_kaggle_dataset("ufc_stats_complete", source)

    assert report["dataset_key"] == "ufc_stats_complete"
    assert frame.iloc[0]["fighter_1_name"] == "Alpha"
    assert frame.iloc[0]["method_class"] == "KO/TKO"
    assert "f1_wins_safe" in frame.columns


def test_safe_target_creation_and_independent_prop_targets():
    row = pd.Series({"f_1_name": "Alpha", "f_2_name": "Beta", "winner": "Beta"})
    assert safe_f1_wins(row, "f_1_name", "f_2_name", "winner") == (0, None)

    frame = pd.DataFrame(
        [
            {
                "f_1_name": "Alpha",
                "f_2_name": "Beta",
                "winner": "Beta",
                "result": "Decision",
                "finish_round": 3,
                "f_1_sig_strikes_succ": 90,
                "f_2_sig_strikes_succ": 20,
                "f_1_takedown_succ": 2,
                "f_2_takedown_succ": 0,
            }
        ]
    )
    targeted, _report = build_bettor_targets(frame)

    assert targeted.iloc[0]["f1_wins"] == 0
    assert targeted.iloc[0]["fighter_1_over_75_sig_strikes"] == 1
    assert targeted.iloc[0]["fighter_1_over_1_5_takedowns"] == 1


def test_duplicate_and_mirrored_fight_detection():
    frame = pd.DataFrame(
        [
            {"event_date": "2024-01-01", "event_name": "Event", "fighter_1_name": "Alpha", "fighter_2_name": "Beta"},
            {"event_date": "2024-01-01", "event_name": "Event", "fighter_1_name": "Beta", "fighter_2_name": "Alpha"},
        ]
    )
    keyed = add_deduping_columns(frame)
    summary = dedupe_summary(frame)

    assert keyed["mirrored_row_candidate"].all()
    assert summary["duplicate_fight_rows"] == 2


def test_chronological_evaluation_split_holds_out_newest_rows():
    frame = pd.DataFrame(
        [
            {"event_date": f"2024-01-{day:02d}", "source_order": day, "finish_binary": day % 2}
            for day in range(1, 21)
        ]
    )
    train, validation, test, report = chronological_train_validation_test_split(frame, validation_size=0.2, test_size=0.2)

    assert report["final_test_held_out"] is True
    assert train["_event_date"].max() < validation["_event_date"].min()
    assert validation["_event_date"].max() < test["_event_date"].min()


def test_relative_ranking_and_baseline_helpers():
    baseline = majority_baseline(["1", "1", "0"])
    assert baseline["accuracy"] == 0.6667

    ranking = relative_ranking(
        {
            "strong": {"status": "evaluated", "relative_improvement": 0.2, "beats_baseline": True},
            "weak": {"status": "weak", "relative_improvement": -0.1, "beats_baseline": False},
        }
    )
    assert ranking[0]["model"] == "strong"


def test_preprocessing_dry_run_writes_summary_reports(tmp_path, monkeypatch):
    imports = tmp_path / "imports"
    dataset = imports / "kaggle" / "ufc_stats_complete"
    dataset.mkdir(parents=True)
    pd.DataFrame(
        [
            {
                "event_date": "2024-01-01",
                "fighter_1": "Alpha",
                "fighter_2": "Beta",
                "winner": "Alpha",
                "method": "Decision",
                "round": 3,
                "result": "win",
            }
        ]
    ).to_csv(dataset / "fights.csv", index=False)
    output = tmp_path / "processed"
    monkeypatch.chdir(Path.cwd())
    monkeypatch.setattr(
        "sys.argv",
        [
            "preprocess_imported_datasets.py",
            "--input-root",
            str(imports),
            "--only",
            "ufc_stats_complete",
            "--dry-run",
            "--output-dir",
            str(output),
        ],
    )

    assert preprocess_main() == 0
    assert (output / "import_summary.json").is_file()
