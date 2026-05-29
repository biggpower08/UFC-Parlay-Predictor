import json
from pathlib import Path

import pandas as pd

from scripts.train_prop_models import train_model, training_plan
from ufc_predictor.config import settings
from ufc_predictor.models.props.predictor import load_prop_model, predict_prop_model
from ufc_predictor.training.dataset_builder import build_training_rows


def sample_dataset():
    fights = []
    methods = ["KO/TKO", "SUB", "U-DEC", "KO/TKO", "S-DEC", "SUB"] * 20
    for index, method in enumerate(methods):
        fights.append(
            {
                "event": f"Event {index}",
                "fighter_1": f"Winner {index % 8}",
                "fighter_2": f"Loser {index % 9}",
                "result": "win",
                "method": method,
                "round": 3 if "DEC" in method else (index % 3) + 1,
                "time": "5:00",
            }
        )
    return build_training_rows(pd.DataFrame(fights), assume_reverse_chronological=True)


def test_training_plan_marks_missing_strike_and_control_labels_insufficient():
    dataset, audit = sample_dataset()

    plan = training_plan(dataset, audit.to_dict(), min_rows=20)

    assert plan["finish_model"]["status"] == "experimental"
    assert plan["goes_distance_model"]["status"] == "experimental"
    assert plan["strike_volume_model"]["status"] == "insufficient_data"
    assert plan["takedown_control_model"]["status"] == "insufficient_data"


def test_train_model_creates_metadata_and_metrics(tmp_path: Path):
    dataset, audit = sample_dataset()

    artifact = train_model(
        model_name="finish_model",
        target="finish_binary",
        dataset=dataset,
        audit=audit.to_dict(),
        test_size=0.2,
        data_source="test",
        input_path="fixture",
        status="experimental",
    )

    assert artifact["metadata"]["status"] == "experimental"
    assert artifact["metadata"]["leakage_checked"] is True
    assert artifact["metrics"]["validation"]["balanced_accuracy"] is not None
    path = tmp_path / "finish_model.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    assert path.is_file()


def test_prop_predictor_refuses_missing_training_features(tmp_path: Path):
    dataset, audit = sample_dataset()
    artifact = train_model(
        model_name="finish_model",
        target="finish_binary",
        dataset=dataset,
        audit=audit.to_dict(),
        test_size=0.2,
        data_source="test",
        input_path="fixture",
        status="experimental",
    )
    artifacts_dir = tmp_path / "artifacts"
    artifacts_dir.mkdir()
    (artifacts_dir / "finish_model.json").write_text(json.dumps(artifact), encoding="utf-8")

    original_dir = settings.PROP_MODELS_DIR
    try:
        settings.PROP_MODELS_DIR = artifacts_dir
        load_prop_model.cache_clear()
        prediction = predict_prop_model("finish_model", {"delta_elo": 50})
    finally:
        settings.PROP_MODELS_DIR = original_dir
        load_prop_model.cache_clear()

    assert prediction["status"] == "experimental"
    assert prediction["support_level"] == "not_available"
    assert prediction["label"] is None
    assert "a_prior_fights" in prediction["missing_features"]
