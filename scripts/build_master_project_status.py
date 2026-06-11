from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.source_eligibility import source_rules_as_dict


MODEL_ORDER = [
    "winner_model",
    "fight_duration_model",
    "finish_model",
    "goes_distance_model",
    "over_1_5_model",
    "over_2_5_model",
    "ends_before_round_3_model",
    "finish_in_round_1_model",
    "finish_type_model",
    "method_umbrella_model",
    "method_model",
    "strike_volume_model",
    "takedown_control_model",
    "odds_calibration_model",
]

REPORT_LINKS = [
    "PROJECT_MASTER_STATUS.md",
    "model_accuracy_report.md",
    "backtest_report.md",
    "interaction_discovery_report.md",
    "production_readiness_audit.md",
    "model_strengthening_plan.md",
    "model_training_code_review.md",
    "source_transfer_diagnostics.md",
    "source_feature_label_drift_report.md",
    "source_strategy_ablation_report.md",
    "source_normalization_rules.md",
    "source_eligibility_rules.md",
    "model_data_source_plan.md",
    "prediction_output_policy.md",
    "final_prediction_ensemble_plan.md",
    "model_artifact_packaging_plan.md",
    "calibration_plan.md",
    "dataset_recovery_plan.md",
    "neural_network_experiment_plan.md",
    "development_run_modes.md",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the master project status document from current reports.")
    parser.add_argument("--docs-dir", default="docs")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--output", default="docs/PROJECT_MASTER_STATUS.md")
    parser.add_argument("--index-output", default="docs/PROJECT_MASTER_INDEX.md")
    parser.add_argument("--source-eligibility-json", default=str(settings.DATA_PROCESSED_DIR / "source_eligibility_rules.json"))
    parser.add_argument("--source-eligibility-md", default="docs/source_eligibility_rules.md")
    args = parser.parse_args(argv)

    docs_dir = Path(args.docs_dir)
    processed_dir = Path(args.processed_dir)
    reports = load_reports(processed_dir)
    source_rules = source_rules_as_dict()

    write_json(Path(args.source_eligibility_json), source_rules)
    write_text(Path(args.source_eligibility_md), source_eligibility_markdown(source_rules))
    write_text(Path(args.output), master_markdown(reports, source_rules))
    write_text(Path(args.index_output), index_markdown(docs_dir))
    print(json.dumps({"status": args.output, "index": args.index_output, "source_eligibility": args.source_eligibility_json}, indent=2))
    return 0


def load_reports(processed_dir: Path) -> dict[str, Any]:
    return {
        "registry": read_json(processed_dir / "model_registry.json"),
        "accuracy": read_json(processed_dir / "model_accuracy_report.json"),
        "backtest": read_json(processed_dir / "backtest_report.json"),
        "interactions": read_json(processed_dir / "interaction_discovery_report.json"),
        "source_transfer": read_json(processed_dir / "source_transfer_diagnostics.json"),
        "source_drift": read_json(processed_dir / "source_feature_label_drift_report.json"),
        "source_strategy": read_json(processed_dir / "source_strategy_ablation_report.json"),
        "feature_availability": read_json(processed_dir / "feature_availability_report.json"),
        "training_summary": read_json(processed_dir / "training_dataset_summary.json"),
    }


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {"_missing": True, "path": str(path)}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"_missing": True, "path": str(path), "error": "invalid json"}


def master_markdown(reports: dict[str, Any], source_rules: dict[str, Any]) -> str:
    registry = reports.get("registry", {})
    accuracy = reports.get("accuracy", {})
    backtest = reports.get("backtest", {})
    interactions = reports.get("interactions", {})
    source_transfer = reports.get("source_transfer", {})
    source_drift = reports.get("source_drift", {})
    training_summary = reports.get("training_summary", {})
    lines = [
        "# UFC/MMA AI Predictor Master Project Status",
        "",
        f"_Generated: {datetime.now(timezone.utc).isoformat()}_",
        "",
        "## 1. Plain-English Project Summary",
        "The app has working winner predictions, Elo support, analysis pages, betting-read scaffolding, and a growing model audit system. The current priority is production readiness: source eligibility, label quality, source-transfer stability, calibration, and safe runtime output. No model is currently marked production-ready, and no model artifacts are packaged yet.",
        "",
        "## 2. Current Production Readiness Status",
        "- `winner_model` is `high_confidence_only`, not `production_ready`.",
        "- Duration and round binary models are `production_candidate`, not `production_ready`.",
        "- `method_umbrella_model` and `method_model` are `weak_or_failed_baseline`.",
        "- `finish_type_model`, `strike_volume_model`, and `takedown_control_model` are experimental/context-only.",
        "- `odds_calibration_model` is blocked until trusted pre-fight odds timestamps exist.",
        "- No model artifacts are packaged yet.",
        "",
        "## 3. Current Model Status Table",
        "| Model | Production Status | Main Metric | Baseline | Source Holdout | Public Use |",
        "|---|---|---:|---:|---|---|",
    ]
    for model in MODEL_ORDER:
        entry = registry.get(model, {})
        lines.append(
            "| {model} | {status} | {metric} | {baseline} | {holdout} | {use} |".format(
                model=model,
                status=value(entry.get("production_status")),
                metric=value(entry.get("final_test_metric")),
                baseline=value(entry.get("baseline_metric")),
                holdout=value(entry.get("source_holdout_status")),
                use=value(entry.get("recommended_use")),
            )
        )
    lines += [
        "",
        "## 4. Current Dataset / Source Status",
        source_summary_table(source_transfer),
        "",
        "## 5. Current Source-Eligibility Rules",
        "- `ufc_stats_complete` should be treated primarily as a stat-rich source, not a universal result-label source.",
        "- No-contest, draw, unknown, or missing-result rows must not create fake winner, finish, method, or round labels.",
        "- Result models require safe winner/result labels.",
        "- Round models require safe finish round/time and scheduled-round parsing.",
        "- Strike/takedown models require reliable stat coverage.",
        source_eligibility_table(source_rules),
        "",
        "## 6. Current Source-Holdout / Source-Transfer Status",
        "- Stable source-holdout can restore `production_candidate` status.",
        "- Severe source-holdout regression blocks candidate/ready status.",
        "- `ufc_stats_complete` remains the main stat-source risk for strike/takedown models.",
        "- `ufc_1994_2026` is currently the weakest holdout source for several duration/round candidates.",
        "",
        "## 7. Current Interaction Discovery Status",
        interaction_summary(interactions),
        "",
        "## 8. Current Calibration Status",
        "- Current `--calibrate` behavior is basic probability scoring/reporting, not a full validation-only calibration refactor.",
        "- First calibration targets: winner high-confidence output, fight duration, over 2.5, and ends-before-round-3.",
        "- Weak method models, blocked odds, and unstable experimental models are not worth calibrating yet.",
        "",
        "## 9. Current UI / Product Status",
        "- Home, Analysis, Stats, and Odds pages exist as product surfaces.",
        "- Odds page remains model-informed/read-only; no fake sportsbook odds or bet placement.",
        "- Public output should show model status badges and source/data-quality warnings before strong claims.",
        "",
        "## 10. Current Backend/API Status",
        "- FastAPI serves the static Next.js frontend.",
        "- Prediction endpoints should include model statuses, unavailable models, unstable models, public warning text, and data-quality fields as this moves toward release.",
        "- App startup must not require local Kaggle/import files.",
        "",
        "## 11. Current Deployment / Render Status",
        "- Single Render-hosted FastAPI app remains the deployment target.",
        "- Do not split frontend/backend deployment.",
        "- Render config should keep `/health` available.",
        "",
        "## 12. Current Supabase / Database Status",
        "- Supabase remains the production database.",
        "- Kaggle/local CSVs are raw training inputs only and are not required at runtime.",
        "- Normalized production data should live in Supabase/backend when needed by the deployed app.",
        "",
        "## 13. Current Repo Hygiene Status",
        "- `fighters.db`, raw imports, normalized combined CSVs, backtest predictions, `.env`, `kaggle.json`, virtual environments, frontend build output, and pytest temp/cache folders must not be committed.",
        "- Recent hygiene checks confirmed generated database files are ignored and not tracked.",
        "",
        "## 14. What Is Safe To Show Publicly",
        "- Winner model evidence only in high-confidence/selective mode.",
        "- Candidate duration/round reads as cautious model-candidate context after runtime review.",
        "- Elo, peak Elo, fights counted, status labels, and simple data-quality warnings.",
        "- Informational prop-style reads only, not guaranteed outcomes or sportsbook lines.",
        "",
        "## 15. What Must Stay Experimental",
        "- `finish_type_model`.",
        "- `strike_volume_model`.",
        "- `takedown_control_model`.",
        "- Any source-transfer unstable or weak model.",
        "- Any model using source ID as a production shortcut.",
        "",
        "## 16. What Is Blocked",
        "- `odds_calibration_model` until trusted pre-fight odds timestamps exist.",
        "- Production-ready model claims.",
        "- Artifact packaging without manual review and gate confirmation.",
        "- Public method-model confidence until method models beat baseline.",
        "",
        "## 17. Biggest Technical Risks",
        "- Runtime feature parity for candidate artifacts.",
        "- Probability calibration is not yet full validation-only calibration.",
        "- Backtest/evaluation scripts are still computationally heavy.",
        "- Model statuses can drift if reports are not regenerated together.",
        "",
        "## 18. Biggest Data Risks",
        "- Source label definitions differ across datasets.",
        "- `ufc_stats_complete` is stat-rich but not a universal result-label source.",
        "- Method labels and finish-type classes remain noisy.",
        "- Odds data is not trusted without pre-fight timestamps.",
        "",
        "## 19. Biggest Product Risks",
        "- Overstating experimental prop reads.",
        "- Showing probability-style outputs without calibration/source-transfer support.",
        "- Making betting-help language sound like guaranteed financial advice.",
        "- Shipping a paywall before trust/warnings/status handling is ready.",
        "",
        "## 20. Next 2-Week Build Plan",
        "1. Keep this master status and index current.",
        "2. Enforce source eligibility in model/retraining workflows.",
        "3. Add model-status and data-quality fields to API responses.",
        "4. Add public-safe model/status badges in the UI.",
        "5. Draft validation-only calibration implementation for strongest candidates.",
        "6. Keep odds blocked until trusted timestamps exist.",
        "",
        "## 21. Next 4-Week Production Plan",
        "1. Review candidate winner/duration/round artifacts manually.",
        "2. Implement true validation-only calibration for stable candidate models.",
        "3. Integrate `ensemble_breakdown` into API/UI with unavailable/unstable model lists.",
        "4. Add limited-release/high-confidence research mode.",
        "5. Keep method/stat models context-only until source transfer improves.",
        "6. Consider neural-network benchmark only after source/data issues improve.",
        "",
        "## 22. Exact Next Tasks For Codex",
        "- Add model registry health endpoint and prediction response model-status fields.",
        "- Add source eligibility filtering to the next training/evaluation pass.",
        "- Implement validation-only calibration report for candidate models.",
        "- Add UI badges for model status and data quality.",
        "- Keep reports synchronized with this master status.",
        "",
        "## 23. Commands To Run",
        "```powershell",
        "cd C:\\dev\\mma-ai",
        "$env:MMA_AI_PYTHON=\"C:\\venvs\\mma-ai\\Scripts\\python.exe\"",
        "& $env:MMA_AI_PYTHON scripts\\build_master_project_status.py",
        "& $env:MMA_AI_PYTHON scripts\\source_transfer_diagnostics.py",
        "$TempTestDir = \"$env:TEMP\\mma_ai_pytest_$([guid]::NewGuid().ToString())\"",
        "& $env:MMA_AI_PYTHON -m pytest ufc_predictor\\tests -q --basetemp $TempTestDir",
        "```",
        "",
        "## 24. Files/Folders Not To Commit",
        "- `data/imports/`",
        "- `ufc_predictor/data/processed/fighters.db`",
        "- `ufc_predictor/data/processed/imports/normalized_fights_combined.csv`",
        "- `ufc_predictor/data/processed/backtest_predictions.json`",
        "- `ufc_predictor/data/processed/training_imports/`",
        "- `.env`, `kaggle.json`, `.venv`, `C:\\venvs`, `node_modules`, `.next`, pytest temp/cache folders",
        "",
        "## Source Report Pointers",
        "- Model accuracy: `docs/model_accuracy_report.md`",
        "- Backtest: `docs/backtest_report.md`",
        "- Source transfer diagnostics: `docs/source_transfer_diagnostics.md`",
        "- Drift report: `docs/source_feature_label_drift_report.md`",
        "- Source strategy ablation: `docs/source_strategy_ablation_report.md`",
        "- Source normalization rules: `docs/source_normalization_rules.md`",
        "- Artifact packaging plan: `docs/model_artifact_packaging_plan.md`",
    ]
    return "\n".join(lines) + "\n"


def source_summary_table(source_transfer: dict[str, Any]) -> str:
    reports = source_transfer.get("source_reports") or {}
    if not reports:
        return "Source transfer diagnostics not available yet."
    lines = ["| Source | Rows | Date Range | Final-Test Rows | Drift Grade |", "|---|---:|---|---:|---|"]
    for source, report in reports.items():
        date = report.get("date_range") or {}
        lines.append(f"| {source} | {report.get('row_count')} | {date.get('min')} to {date.get('max')} | {report.get('final_test_row_count')} | {report.get('drift_grade')} |")
    return "\n".join(lines)


def source_eligibility_table(source_rules: dict[str, Any]) -> str:
    lines = ["| Source | Safe Uses | Unsafe Uses |", "|---|---|---|"]
    for source, rule in source_rules.items():
        lines.append(f"| {source} | {', '.join(rule.get('safe_uses', []))} | {', '.join(rule.get('unsafe_uses', []))} |")
    return "\n".join(lines)


def interaction_summary(interactions: dict[str, Any]) -> str:
    models = interactions.get("models") or {}
    if not models:
        return "Interaction discovery report not available yet."
    family_names = [
        "striking_x_opponent_weakness",
        "grappling_x_opponent_weakness",
        "finishing_x_durability",
        "pace_x_age_activity",
        "scheduled_rounds_x_pace_duration",
        "fighter_strength_x_opponent_weakness",
        "physical_x_style",
        "physical_x_division",
    ]
    lines = [
        "- Interaction selection uses validation only; final test is not used for selection.",
        "- Selected interactions must be runtime-computable and cannot include target/current-fight columns.",
        "| Model | Candidates | Selected | Selection Status | MMA Family Coverage |",
        "|---|---:|---:|---|---|",
    ]
    for model, report in models.items():
        counts = report.get("candidate_count_by_feature_group_pair") or {}
        coverage = ", ".join(family for family in family_names if counts.get(family, 0))
        lines.append(f"| {model} | {report.get('candidate_count', 0)} | {report.get('selected_count', 0)} | {report.get('selection_status')} | {coverage or 'limited/zero'} |")
    return "\n".join(lines)


def source_eligibility_markdown(source_rules: dict[str, Any]) -> str:
    lines = [
        "# Source Eligibility Rules",
        "",
        "## Plain-English Summary",
        "Each data source should only support the model targets it can safely label. This prevents stat-rich but result-label-weak sources from creating fake winner, duration, method, or round labels.",
        "",
    ]
    for source, rule in source_rules.items():
        lines += [
            f"## {source}",
            f"- Safe uses: {', '.join(rule.get('safe_uses', []))}",
            f"- Unsafe uses: {', '.join(rule.get('unsafe_uses', []))}",
            f"- Notes: {'; '.join(rule.get('notes', []))}",
            "",
            "| Model | Eligibility |",
            "|---|---|",
        ]
        for model, status in rule.get("model_eligibility", {}).items():
            lines.append(f"| {model} | {status} |")
        lines.append("")
    return "\n".join(lines)


def index_markdown(docs_dir: Path) -> str:
    lines = [
        "# Project Master Index",
        "",
        "Use `PROJECT_MASTER_STATUS.md` as the main source of truth. The files below are detailed supporting reports.",
        "",
    ]
    for name in REPORT_LINKS:
        path = docs_dir / name
        status = "available" if path.is_file() else "not available yet"
        lines.append(f"- [{name}]({name}) - {status}")
    return "\n".join(lines) + "\n"


def value(item: Any) -> str:
    if item is None or item == "":
        return "not available yet"
    if isinstance(item, float):
        return str(round(item, 4))
    return str(item)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
