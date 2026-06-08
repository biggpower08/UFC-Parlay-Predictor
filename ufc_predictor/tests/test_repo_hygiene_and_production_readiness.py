from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd
import yaml
from packaging.requirements import Requirement

from scripts.evaluate_model_accuracy import feature_names_for_model, production_gate_result


ROOT = Path(__file__).resolve().parents[2]


def test_gitignore_protects_secret_raw_and_generated_files():
    protected = [
        "kaggle.json",
        "data/imports/test.csv",
        "ufc_predictor/data/processed/fighters.db",
        "ufc_predictor/data/processed/imports/normalized_fights_combined.csv",
        "ufc_predictor/data/processed/backtest_predictions.json",
    ]

    for path in protected:
        result = subprocess.run(
            ["git", "check-ignore", "--no-index", "-v", path],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        assert result.returncode == 0, f"{path} is not protected by .gitignore: {result.stderr}"


def test_requirements_file_has_one_parseable_requirement_per_line():
    lines = Path("requirements.txt").read_text(encoding="utf-8").splitlines()

    requirements = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]

    assert len(requirements) >= 5
    for line in requirements:
        assert "\n" not in line
        Requirement(line)


def test_render_yaml_parses_and_keeps_fastapi_web_service():
    data = yaml.safe_load(Path("render.yaml").read_text(encoding="utf-8"))

    services = data.get("services") or []
    assert services
    service = services[0]
    assert service["type"] == "web"
    assert service["runtime"] == "python"
    assert "uvicorn ufc_predictor.api.app:app" in service["startCommand"]
    assert service["healthCheckPath"] == "/health"


def test_feature_selection_does_not_use_final_test_only_columns():
    train = pd.DataFrame(
        [
            {
                "a_prior_fights": 1,
                "b_prior_fights": 1,
                "a_prior_wins": 1,
                "b_prior_wins": 0,
                "a_prior_finishes": 1,
                "b_prior_finishes": 0,
                "a_prior_decisions": 0,
                "b_prior_decisions": 0,
            }
        ]
    )
    validation = train.copy()
    test = train.copy()
    test["fighter_1_age"] = 30

    features = feature_names_for_model(train, validation, test, "fight_duration_model")

    assert "fighter_1_age" not in features


def test_production_gates_block_weak_winner_and_odds_models():
    weak = production_gate_result(
        "round_phase_model",
        {
            "status": "weak_or_failed_baseline",
            "beats_baseline": False,
            "feature_names": ["a_prior_fights"],
            "metrics": {"balanced_accuracy": 0.3, "log_loss": 1.2},
            "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
        },
        {"no_cross_split_fight_leakage": True},
        {},
    )
    winner = production_gate_result(
        "winner_model",
        {
            "status": "evaluated",
            "beats_baseline": True,
            "feature_names": ["a_prior_fights"],
            "test_rows": 1000,
            "metrics": {"balanced_accuracy": 0.9, "brier_score": 0.1},
            "selective_prediction": {"best_accuracy": {"sample_count": 200, "coverage_percent": 20}},
        },
        {"no_cross_split_fight_leakage": True},
        {"final_status": {"runtime_parity_ok": True, "source_holdout_ok": False, "leakage_scan_ok": True, "low_history_ok": True}},
    )
    odds = production_gate_result(
        "odds_calibration_model",
        {"status": "blocked", "limitations": ["Pre-fight odds timestamps are not trusted."]},
        {"no_cross_split_fight_leakage": True},
        {},
    )

    assert weak["production_status"] != "production_ready"
    assert winner["production_status"] == "high_confidence_only"
    assert "source_holdout_stable" in winner["failed_gates"]
    assert odds["production_status"] == "blocked"


def test_registry_keeps_odds_blocked_without_trusted_prefight_timestamps():
    registry_path = Path("ufc_predictor/data/processed/model_registry.json")
    if not registry_path.is_file():
        return
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    odds = registry.get("odds_calibration_model", {})

    assert odds.get("production_status") == "blocked"
    assert "model_blocked" in odds.get("failed_gates", [])
