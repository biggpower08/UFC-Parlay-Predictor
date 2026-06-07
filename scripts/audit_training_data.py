from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.importers import import_training_csvs
from ufc_predictor.training.leakage import scan_dataframe
from ufc_predictor.training.size_context import build_size_context
from ufc_predictor.training.targets import build_bettor_targets


MENTOR_FILES = ("preprocess_ufc_winner.py", "reproduce_silver_run.py", "audit.jsonl", "client.log")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit available UFC/MMA training data and mentor Silver files.")
    parser.add_argument("--input-dir", default="data/imports/kaggle")
    parser.add_argument("--include-mentor-silver", action="store_true")
    parser.add_argument("--mentor-dir", default="data/mentor_silver_run")
    parser.add_argument("--mentor-zip", default="")
    parser.add_argument("--output", default=str(settings.DATA_PROCESSED_DIR / "data_audit_report.json"))
    parser.add_argument("--markdown-output", default="docs/data_audit_report.md")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    normalized, import_report = import_training_csvs(input_dir, dry_run=True)
    leakage_reports = _scan_csvs(input_dir)
    target_report = None
    target_rows = 0
    if not normalized.empty:
        targeted, target_report_obj = build_bettor_targets(_for_target_orientation(normalized))
        target_report = target_report_obj.to_dict()
        target_rows = int(len(targeted))
    if args.include_mentor_silver and args.mentor_zip:
        mentor = review_mentor_silver_zip(Path(args.mentor_zip))
    elif args.include_mentor_silver:
        mentor = review_mentor_silver(Path(args.mentor_dir))
    else:
        mentor = {"checked": False}
    size_summary = _size_summary(normalized)
    readiness = _model_readiness(import_report.to_dict(), target_report or {})
    payload = {
        "input_dir": str(input_dir),
        "import_report": import_report.to_dict(),
        "target_rows": target_rows,
        "target_report": target_report,
        "leakage_summary": _compact_leakage(leakage_reports),
        "size_context_summary": size_summary,
        "mentor_silver_review": mentor,
        "model_readiness": readiness,
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    markdown = _markdown(payload)
    markdown_path = Path(args.markdown_output)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(markdown, encoding="utf-8")
    print(json.dumps({"output": str(output), "markdown_output": str(markdown_path), "model_readiness": readiness}, indent=2))
    return 0


def review_mentor_silver(mentor_dir: Path) -> dict:
    found = {}
    for name in MENTOR_FILES:
        path = mentor_dir / name
        if not path.is_file():
            found[name] = {"present": False}
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        found[name] = _mentor_file_review(name, text)
    return {
        "checked": True,
        "mentor_dir": str(mentor_dir),
        "files": found,
        "overall_decision": "offline_benchmark_until_chronological_split_low_leakage_and_runtime_features_are_proven",
    }


def review_mentor_silver_zip(zip_path: Path) -> dict:
    if not zip_path.is_file():
        return {"checked": True, "mentor_zip": str(zip_path), "error": "zip_not_found"}
    found = {}
    with zipfile.ZipFile(zip_path) as archive:
        names = set(archive.namelist())
        for name in MENTOR_FILES:
            if name not in names:
                found[name] = {"present": False}
                continue
            with archive.open(name) as handle:
                text = handle.read().decode("utf-8", errors="replace")
            found[name] = _mentor_file_review(name, text)
    return {
        "checked": True,
        "mentor_zip": str(zip_path),
        "files": found,
        "overall_decision": "offline_benchmark_until_chronological_split_low_leakage_and_runtime_features_are_proven",
    }


def _mentor_file_review(name: str, text: str) -> dict:
    base = {
        "present": True,
        "purpose": _purpose_for(name),
        "inputs": _grep(text, r"(UFC_full_data_silver\.csv|read_csv\([^)]+)"),
        "outputs": _grep(text, r"(to_csv\([^)]+|dump\([^)]+|write_text\([^)]+|\.json|\.pkl|\.txt)"),
        "dependencies": _grep(text, r"^(?:import|from)\s+([A-Za-z0-9_\.]+)", multiline=True),
        "hardcoded_paths": _grep(text, r"([A-Za-z]:\\[^\n'\"]+|data/[^\n'\"]+)"),
        "metrics": _grep(text, r"(accuracy|balanced|roc_auc|auc|f1)[^0-9\n]{0,40}[0-9]\.[0-9]+", flags=re.IGNORECASE),
        "leakage_risks": _mentor_leakage_risks(text),
        "decision": "review_only_do_not_execute",
    }
    if name == "preprocess_ufc_winner.py":
        base["target_logic"] = _grep(text, r"f1_wins[^\n]+")
        base["safe_rewrite"] = "Use ufc_predictor.training.targets.safe_f1_wins and drop invalid target rows."
    if name == "reproduce_silver_run.py":
        base.update(_reproduce_silver_details(text))
    if name in {"audit.jsonl", "client.log"}:
        base.update(_mentor_log_summary(text))
    return base


def _scan_csvs(input_dir: Path) -> list[dict]:
    reports = []
    for path in sorted(input_dir.rglob("*.csv")) if input_dir.exists() else []:
        try:
            frame = pd.read_csv(path, nrows=1000)
            report = scan_dataframe(frame)
            report["file"] = str(path)
            reports.append(report)
        except Exception as exc:  # noqa: BLE001
            reports.append({"file": str(path), "error": str(exc)})
    return reports


def _for_target_orientation(normalized: pd.DataFrame) -> pd.DataFrame:
    rows = normalized.copy()
    rows["f_1_name"] = rows.get("fighter_1")
    rows["f_2_name"] = rows.get("fighter_2")
    rows["winner"] = rows["winner_name"] if "winner_name" in rows.columns else rows.get("fighter_1")
    return rows


def _size_summary(normalized: pd.DataFrame) -> dict:
    if normalized.empty or "weight_class" not in normalized.columns:
        return {"available": False}
    same = 0
    unknown = 0
    examples = []
    for _, row in normalized.head(1000).iterrows():
        context = build_size_context({"weight_class": row.get("weight_class")}, {"weight_class": row.get("weight_class")})
        same += int(context["same_division"])
        unknown += int(context["unknown_size_context"])
        if len(examples) < 3:
            examples.append(context)
    return {"available": True, "sampled_rows": min(1000, len(normalized)), "same_division_sample": same, "unknown_sample": unknown, "examples": examples}


def _model_readiness(import_report: dict, target_report: dict) -> dict:
    labels = import_report.get("label_availability", {})
    targets = target_report.get("label_availability", {})
    has_dates = bool(import_report.get("date_range", {}).get("min"))
    return {
        "winner_model": _status(target_report.get("valid_winner_targets", 0), has_dates, runtime_compatible=False, reason="Winner target exists, but normalized winner/loser rows are not enough for runtime-compatible f1/f2 prediction."),
        "finish_model": _status(labels.get("finish_binary", 0), has_dates),
        "goes_distance_model": _status(labels.get("goes_distance_binary", 0), has_dates),
        "method_model": _status(labels.get("method_group", 0), has_dates, reason="Multiclass method remains harder and must beat baseline before production use."),
        "round_phase_model": _status(labels.get("round_phase_class", 0), has_dates, reason="Round-phase label exists; exact round props remain future work."),
        "strike_volume_model": _status(targets.get("fighter_1_over_50_sig_strikes", 0), has_dates, reason="Strike props are independent of winner and need segment calibration."),
        "takedown_control_model": _status(targets.get("fighter_1_over_1_5_takedowns", 0), has_dates, reason="Takedown/control props are independent of winner and need segment calibration."),
        "odds_calibration_model": {
            "status": "blocked",
            "reason": "Odds rows were detected separately, but are not yet safely matched to fight outcomes and timestamps.",
        },
        "expert_signal_model": {
            "status": "blocked",
            "reason": "No verified pre-fight expert timestamped signal dataset is available.",
        },
    }


def _status(rows: int, has_dates: bool, runtime_compatible: bool = True, reason: str = "") -> dict:
    if rows < 500:
        status = "insufficient_data"
    elif not has_dates:
        status = "experimental"
    elif not runtime_compatible:
        status = "offline_benchmark"
    else:
        status = "training_data_ready"
    return {"status": status, "rows": int(rows or 0), "reason": reason}


def _compact_leakage(reports: list[dict]) -> dict:
    combined: dict[str, int] = {}
    blocked = {}
    for report in reports:
        for key, count in report.get("summary", {}).items():
            combined[key] = combined.get(key, 0) + int(count)
        if report.get("blocked_feature_columns"):
            blocked[report["file"]] = report["blocked_feature_columns"][:30]
    return {"files_scanned": len(reports), "classification_counts": combined, "blocked_columns_preview": blocked}


def _markdown(payload: dict) -> str:
    readiness = payload["model_readiness"]
    lines = [
        "# Training Data Audit Report",
        "",
        f"Input folder: `{payload['input_dir']}`",
        f"Normalized fight rows: {payload['import_report'].get('rows_normalized', 0)}",
        f"Target rows inspected: {payload.get('target_rows', 0)}",
        "",
        "## Model Readiness",
    ]
    for model, status in readiness.items():
        lines.append(f"- `{model}`: {status.get('status')} ({status.get('rows', 0)} rows). {status.get('reason', '')}")
    lines.extend(
        [
            "",
            "## Leakage Summary",
            f"`{json.dumps(payload['leakage_summary'].get('classification_counts', {}), sort_keys=True)}`",
            "",
            "## Mentor Silver Review",
            f"Decision: `{payload['mentor_silver_review'].get('overall_decision', 'not_checked')}`",
        ]
    )
    return "\n".join(lines).strip() + "\n"


def _purpose_for(name: str) -> str:
    return {
        "preprocess_ufc_winner.py": "Likely creates the f1_wins winner target from Silver CSV.",
        "reproduce_silver_run.py": "Likely reproduces the mentor winner-model evaluation run.",
        "audit.jsonl": "Line-oriented audit log from the mentor run.",
        "client.log": "Execution log from the mentor run.",
    }.get(name, "Mentor file")


def _grep(text: str, pattern: str, flags: int = 0, multiline: bool = False) -> list[str]:
    if multiline:
        flags |= re.MULTILINE
    return sorted(set(match.group(0) for match in re.finditer(pattern, text, flags)))[:20]


def _mentor_leakage_risks(text: str) -> list[str]:
    risks = []
    lowered = text.lower()
    if "train_test_split" in lowered:
        risks.append("Uses random split unless code overrides it with chronological grouping.")
    for term in ("winner", "result", "method", "finish_round", "finish_time", "sig_strikes", "takedown", "ctrl_time"):
        if term in lowered:
            risks.append(f"References {term}; verify it is label-only or pre-fight-safe before training.")
    if "f1_wins" in lowered and "winner == f_1_name" in lowered:
        risks.append("f1_wins may mark missing/unmatched winners as fighter 2 wins unless guarded.")
    return risks


def _reproduce_silver_details(text: str) -> dict:
    feature_columns = _list_literal(text, "FEATURE_COLUMNS")
    return {
        "model_type": "LightGBM LGBMClassifier" if "LGBMClassifier" in text else "unknown_review_needed",
        "target_column": "f1_wins" if "TARGET_COL = \"f1_wins\"" in text else "unknown_review_needed",
        "input_file_expectations": _grep(text, r"data/ufc/silver/[A-Za-z0-9_\.]+"),
        "feature_count": len(feature_columns),
        "feature_columns_preview": feature_columns[:40],
        "feature_classification_summary": _classify_feature_preview(feature_columns),
        "drop_columns": {
            "fight_outcome": _list_literal(text, "DROP_FIGHT_OUTCOME"),
            "string_context": _list_literal(text, "DROP_STRING_CONTEXT"),
            "low_importance": _list_literal(text, "DROP_LOW_IMPORTANCE"),
            "in_fight_preview": _list_literal(text, "DROP_IN_FIGHT")[:30],
        },
        "preprocessing_steps": _preprocessing_steps(text),
        "imputation_steps": _grep(text, r"(KNN|knn|median|mode|constant|impute)[^\n]{0,120}", flags=re.IGNORECASE),
        "encoding_steps": _grep(text, r"(TargetEncoder|target_encode|one-hot|stance|categorical)[^\n]{0,120}", flags=re.IGNORECASE),
        "train_test_split_method": "sklearn train_test_split with stratify" if "train_test_split" in text and "stratify" in text else "unknown_review_needed",
        "hyperparameters": _dict_literal_keys(text, "LGBM_PARAMS"),
        "artifact_paths": _grep(text, r"model_silver\.pkl|joblib\.dump\([^)]+"),
        "prediction_mode_behavior": "Loads saved joblib bundle, preprocesses new fights with saved fit_state, then predicts f1_wins.",
        "runtime_feature_requirements": "Runtime must reproduce the same Silver feature row, preprocessing state, encoders, imputation, odds fields, and f1/f2 orientation.",
        "leakage_risk": "moderate_risk",
        "app_status": "offline_benchmark",
    }


def _mentor_log_summary(text: str) -> dict:
    return {
        "dataset_shape_mentions": _grep(text, r"[0-9,]+ rows x [0-9,]+ cols|[0-9,]+ rows × [0-9,]+ columns"),
        "model_search_steps": _grep(text, r"(fit_lightgbm|fit_xgboost|fit_catboost|fit_logistic_regression|fit_mlp|optuna_search|grid_search|stack_models)[^\n]{0,180}", flags=re.IGNORECASE),
        "metrics_reported": _grep(text, r"(accuracy|balanced_accuracy|f1|roc_auc|ROC-AUC)[^0-9\n]{0,60}[0-9]\.[0-9]+", flags=re.IGNORECASE),
        "leakage_warnings": _grep(text, r"(leakage|post-fight|target encoding|future|held-out|chronological)[^\n]{0,220}", flags=re.IGNORECASE),
        "errors_or_failures": _grep(text, r"(Error:|refused|failed|below_threshold)[^\n]{0,220}", flags=re.IGNORECASE),
        "final_conclusions": _grep(text, r"(Best individual|ROC-AUC|accuracy ceiling|FeatureEngineering needs|model has strong)[^\n]{0,220}", flags=re.IGNORECASE),
    }


def _list_literal(text: str, name: str) -> list[str]:
    match = re.search(rf"{name}\s*=\s*\[(.*?)\]\s*(?:\+|#|\n\n)", text, re.DOTALL)
    if not match:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", match.group(1))


def _dict_literal_keys(text: str, name: str) -> dict:
    match = re.search(rf"{name}\s*=\s*\{{(.*?)\n\}}", text, re.DOTALL)
    if not match:
        return {}
    pairs = re.findall(r"['\"]([^'\"]+)['\"]\s*:\s*([^,\n]+)", match.group(1))
    return {key: value.strip() for key, value in pairs}


def _preprocessing_steps(text: str) -> list[str]:
    steps = []
    for marker, label in (
        ("DROP_IN_FIGHT", "Drop whole-fight and per-round post-fight stats."),
        ("DROP_FIGHT_OUTCOME", "Drop outcome and URL columns."),
        ("add_missing_indicator", "Add missingness indicators."),
        ("knn_impute", "KNN-impute selected physical/stat fields."),
        ("winsorize", "Winsorize outliers."),
        ("TargetEncoder", "Target-encode categorical fields."),
        ("RandomOverSampler", "Oversample the training split."),
    ):
        if marker in text:
            steps.append(label)
    return steps


def _classify_feature_preview(features: list[str]) -> dict:
    from ufc_predictor.training.leakage import scan_columns

    rows = scan_columns(features)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    return counts


if __name__ == "__main__":
    raise SystemExit(main())
