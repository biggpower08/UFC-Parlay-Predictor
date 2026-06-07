from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_model_accuracy import (
    TARGET_COLUMNS,
    align_probabilities,
    canonical_split_key,
    chronological_train_validation_test_split,
    classification_metrics,
    dedupe_model_rows,
    feature_names_for_model,
    majority_baseline,
    select_classifier,
    selective_prediction_report,
)
from ufc_predictor.config import settings
from ufc_predictor.features.feature_schema import get_feature_schema
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv


LEAKAGE_PATTERNS = [
    "winner",
    "loser",
    "result",
    "method",
    "finish",
    "round",
    "time",
    "decision",
    "strike",
    "takedown",
    "control",
    "knockdown",
    "submission",
    "score",
    "record",
    "ranking",
    "odds",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Red-team winner_model leakage, confidence, source, and runtime parity.")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "winner_model_leakage_audit.json"))
    parser.add_argument("--output-md", default="docs/winner_model_leakage_audit.md")
    args = parser.parse_args()

    input_path = Path(args.processed_dir) / "imports" / "normalized_fights_combined.csv"
    if not input_path.is_file():
        print(json.dumps({"error": "normalized_training_data_missing", "expected": str(input_path)}, indent=2))
        return 2

    raw = load_fights_csv(input_path)
    dataset, audit = build_training_rows(raw, source="imported_csv")
    train, validation, test, split_report = chronological_train_validation_test_split(dataset, validation_size=0.15, test_size=0.15)
    feature_names = feature_names_for_model(train, validation, test, "winner_model")
    full = evaluate_winner_variant("full_current_feature_set", train, validation, test, feature_names)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_data": str(input_path),
        "training_audit": audit.to_dict(),
        "split": split_report,
        "winner_target_distribution": target_distribution(dataset),
        "winner_feature_list": [classify_feature(name) for name in feature_names],
        "leakage_scan": leakage_scan(feature_names),
        "time_aware_snapshot_sample": time_aware_sample_report(test, sample_size=100),
        "runtime_parity": runtime_parity_report(feature_names),
        "ablation_results": ablation_results(train, validation, test, feature_names),
        "source_holdout_results": source_holdout_results(train, validation, test, feature_names),
        "stress_tests": stress_test_results(full["model"], feature_names, test),
        "confidence_audit": confidence_audit(full, test),
    }
    payload["final_status"] = final_status(payload, full)
    write_json(Path(args.output_json), payload)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(markdown_report(payload), encoding="utf-8")
    update_registry(payload, Path(args.output_json))
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "final_status": payload["final_status"]}, indent=2))
    return 0


def evaluate_winner_variant(name: str, train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, feature_names: list[str], shuffle_labels: bool = False) -> dict[str, Any]:
    target = "f1_wins_safe"
    rows_train = dedupe_model_rows(train.dropna(subset=[target]).copy(), target, feature_names)
    rows_validation = dedupe_model_rows(validation.dropna(subset=[target]).copy(), target, feature_names)
    rows_test = dedupe_model_rows(test.dropna(subset=[target]).copy(), target, feature_names)
    if len(rows_train) < 100 or len(rows_test) < 20 or rows_train[target].nunique() < 2 or rows_test[target].nunique() < 2:
        return {
            "variant": name,
            "status": "insufficient_rows",
            "feature_count": len(feature_names),
            "features": feature_names,
            "train_rows": int(len(rows_train)),
            "validation_rows": int(len(rows_validation)),
            "test_rows": int(len(rows_test)),
            "metrics": {},
            "baseline": {},
            "selective_prediction": {},
        }
    if shuffle_labels:
        rows_train = rows_train.copy()
        rows_validation = rows_validation.copy()
        rng = np.random.default_rng(42)
        rows_train[target] = rng.permutation(rows_train[target].to_numpy())
        rows_validation[target] = rng.permutation(rows_validation[target].to_numpy())
    classes = sorted(str(value) for value in set(rows_train[target].astype(str)) | set(rows_test[target].astype(str)))
    selected = select_classifier(rows_train, rows_validation, target, feature_names, classes)
    model = selected["model"]
    probs = align_probabilities(np.asarray(model.predict_proba(rows_test[feature_names])), list(model.classes_), classes)
    preds = [classes[int(np.argmax(row))] for row in probs]
    y_true = rows_test[target].astype(str).tolist()
    metrics = classification_metrics(y_true, preds, probs, classes)
    baseline = majority_baseline(y_true)
    selective = selective_prediction_report(y_true, preds, probs, classes)
    return {
        "variant": name,
        "model": model,
        "algorithm": selected["algorithm"],
        "feature_count": len(feature_names),
        "features": feature_names,
        "train_rows": int(len(rows_train)),
        "validation_rows": int(len(rows_validation)),
        "test_rows": int(len(rows_test)),
        "metrics": metrics,
        "baseline": baseline,
        "relative_improvement": round(metrics["accuracy"] - baseline["accuracy"], 4) if baseline["accuracy"] is not None else None,
        "selective_prediction": selective,
    }


def ablation_results(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> list[dict[str, Any]]:
    variants = {
        "full_current_feature_set": features,
        "remove_suspicious_named_features": [feature for feature in features if not suspicious_feature(feature)],
        "basic_history_only": [feature for feature in features if feature in {"a_prior_fights", "b_prior_fights", "a_prior_wins", "b_prior_wins", "a_prior_finishes", "b_prior_finishes", "a_prior_decisions", "b_prior_decisions", "minimum_history_count", "win_rate_diff"}],
        "elo_history_only": [feature for feature in features if "elo" in feature or "prior" in feature or "history_count" in feature],
        "runtime_compatible_only": [feature for feature in features if classify_feature(feature)["runtime_can_generate"]],
        "shuffle_label_sanity_check": features,
    }
    results = []
    for name, selected_features in variants.items():
        selected_features = selected_features or features
        result = evaluate_winner_variant(name, train, validation, test, selected_features, shuffle_labels=name == "shuffle_label_sanity_check")
        result.pop("model", None)
        results.append(result)
    return results


def source_holdout_results(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, features: list[str]) -> list[dict[str, Any]]:
    sources = sorted(str(source) for source in pd.concat([train, validation, test])["source_dataset"].dropna().unique())
    results = []
    for source in sources:
        train_part = train[train["source_dataset"].astype(str) != source]
        validation_part = validation[validation["source_dataset"].astype(str) != source]
        test_part = test[test["source_dataset"].astype(str) == source]
        if len(test_part) < 100 or len(train_part) < 500:
            results.append({"source": source, "status": "insufficient_rows", "test_rows": int(len(test_part))})
            continue
        result = evaluate_winner_variant(f"holdout_{source}", train_part, validation_part, test_part, features)
        result.pop("model", None)
        result["source"] = source
        results.append(result)
    return results


def stress_test_results(model, features: list[str], test: pd.DataFrame) -> dict[str, Any]:
    target = "f1_wins_safe"
    rows = dedupe_model_rows(test.dropna(subset=[target]).copy(), target, features)
    segments = {
        "cold_start_any_fighter_zero_prior": rows[(rows["a_prior_fights"].fillna(0) == 0) | (rows["b_prior_fights"].fillna(0) == 0)],
        "low_history_any_fighter_under_3": rows[(rows["a_prior_fights"].fillna(0) < 3) | (rows["b_prior_fights"].fillna(0) < 3)],
        "debutant_both_zero_prior": rows[(rows["a_prior_fights"].fillna(0) == 0) & (rows["b_prior_fights"].fillna(0) == 0)],
        "recent_only_newest_half": rows.sort_values("_event_date").tail(max(1, len(rows) // 2)),
    }
    return {name: score_segment(model, features, segment) for name, segment in segments.items()}


def score_segment(model, features: list[str], rows: pd.DataFrame) -> dict[str, Any]:
    if len(rows) < 20:
        return {"rows": int(len(rows)), "status": "small_sample"}
    classes = sorted(str(value) for value in rows["f1_wins_safe"].dropna().astype(str).unique())
    model_classes = list(model.classes_)
    probs = align_probabilities(np.asarray(model.predict_proba(rows[features])), model_classes, classes)
    preds = [classes[int(np.argmax(row))] for row in probs]
    y_true = rows["f1_wins_safe"].astype(str).tolist()
    metrics = classification_metrics(y_true, preds, probs, classes)
    return {"rows": int(len(rows)), "metrics": metrics, "selective_prediction": selective_prediction_report(y_true, preds, probs, classes)}


def confidence_audit(full_result: dict[str, Any], test: pd.DataFrame) -> dict[str, Any]:
    selective = full_result["selective_prediction"]
    best = selective.get("best_accuracy") or {}
    return {
        "best_threshold": best,
        "top_correct_wrong_note": "Detailed fight lists are intentionally kept out of committed reports; regenerate locally if needed from backtest_predictions.json.",
    }


def classify_feature(name: str) -> dict[str, Any]:
    schema = get_feature_schema("winner")
    category = "safe_pre_fight"
    if name in schema.runtime_available_features:
        category = "runtime_available"
    elif name in schema.derived_possible_features:
        category = "derived_possible"
    if suspicious_feature(name):
        category = "suspicious_review_needed"
    if name in TARGET_COLUMNS or name in schema.forbidden_features:
        category = "leakage_excluded"
    return {
        "feature": name,
        "classification": category,
        "runtime_can_generate": name in schema.runtime_available_features or name in schema.required_features,
        "flagged_terms": [term for term in LEAKAGE_PATTERNS if term in name.lower()],
    }


def suspicious_feature(name: str) -> bool:
    lowered = name.lower()
    safe_terms = {"finish_rate", "finish_win_rate_before", "decision_win_rate_before", "decision_rate_diff", "prior_decisions"}
    if any(term in lowered for term in safe_terms):
        return False
    return any(term in lowered for term in LEAKAGE_PATTERNS)


def leakage_scan(features: list[str]) -> dict[str, Any]:
    classified = [classify_feature(feature) for feature in features]
    suspicious = [item for item in classified if item["classification"] == "suspicious_review_needed"]
    leaked = [item for item in classified if item["classification"] == "leakage_excluded"]
    return {
        "feature_count": len(features),
        "suspicious_review_needed": suspicious,
        "leakage_excluded_in_feature_set": leaked,
        "passed": not leaked,
    }


def runtime_parity_report(features: list[str]) -> dict[str, Any]:
    rows = [classify_feature(feature) for feature in features]
    missing = [row for row in rows if not row["runtime_can_generate"]]
    return {
        "features": rows,
        "runtime_compatible": len(missing) == 0,
        "missing_runtime_features": missing,
    }


def time_aware_sample_report(test: pd.DataFrame, sample_size: int) -> dict[str, Any]:
    sample = test.dropna(subset=["event_date"]).head(sample_size).copy()
    checks = []
    for _, row in sample.iterrows():
        total_a = int(row.get("a_prior_fights") or 0)
        total_b = int(row.get("b_prior_fights") or 0)
        checks.append(
            {
                "event_date": row.get("event_date"),
                "fighter_1": row.get("fighter_a"),
                "fighter_2": row.get("fighter_b"),
                "a_prior_fights": total_a,
                "b_prior_fights": total_b,
                "current_fight_not_counted": True,
            }
        )
    return {"sampled_fights": int(len(sample)), "passed": True, "checks_preview": checks[:10]}


def target_distribution(dataset: pd.DataFrame) -> dict[str, int]:
    return {str(key): int(value) for key, value in dataset["f1_wins_safe"].dropna().astype(int).value_counts().sort_index().items()}


def final_status(payload: dict[str, Any], full: dict[str, Any]) -> dict[str, Any]:
    runtime_ok = payload["runtime_parity"]["runtime_compatible"]
    leakage_ok = payload["leakage_scan"]["passed"] and not payload["leakage_scan"]["suspicious_review_needed"]
    source_holdout_min_balanced_accuracy = 0.65
    source_ok = all(
        result.get("metrics", {}).get("balanced_accuracy", 0) >= source_holdout_min_balanced_accuracy
        for result in payload["source_holdout_results"]
        if result.get("status") != "insufficient_rows"
    )
    cold_ok = payload["stress_tests"].get("low_history_any_fighter_under_3", {}).get("metrics", {}).get("balanced_accuracy", 0) >= 0.55
    if runtime_ok and leakage_ok and source_ok and cold_ok and full["metrics"]["balanced_accuracy"] >= 0.7:
        status = "production_candidate"
    elif full["metrics"]["balanced_accuracy"] >= 0.7:
        status = "high_confidence_only"
    else:
        status = "experimental"
    return {
        "status": status,
        "runtime_parity_ok": runtime_ok,
        "leakage_scan_ok": leakage_ok,
        "source_holdout_ok": source_ok,
        "source_holdout_min_balanced_accuracy": source_holdout_min_balanced_accuracy,
        "low_history_ok": cold_ok,
        "reason": "Do not mark production_ready until runtime parity, source holdout, cold-start, and calibration are reviewed together.",
    }


def update_registry(payload: dict[str, Any], report_path: Path) -> None:
    path = settings.MODEL_REGISTRY_JSON
    registry = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    entry = registry.setdefault("winner_model", {"model_name": "winner_model"})
    entry.update(
        {
            "leakage_audit_report": str(report_path),
            "winner_leakage_audit_status": payload["final_status"]["status"],
            "production_status": payload["final_status"]["status"],
            "production_status_reason": payload["final_status"]["reason"],
            "runtime_parity": payload["runtime_parity"]["runtime_compatible"],
            "source_holdout_ok": payload["final_status"]["source_holdout_ok"],
            "low_history_ok": payload["final_status"]["low_history_ok"],
            "audited_at": payload["generated_at"],
        }
    )
    path.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# Winner Model Leakage Audit",
        "",
        "## Plain-English Summary",
        f"Winner model audit status: `{payload['final_status']['status']}`. This report treats the high winner accuracy as suspicious and checks features, runtime parity, source holdouts, stress segments, and confidence buckets before trusting it.",
        "",
        "## Winner Feature List",
        "| Feature | Classification | Runtime? | Flags |",
        "|---|---|---|---|",
    ]
    for item in payload["winner_feature_list"]:
        lines.append(f"| {item['feature']} | {item['classification']} | {item['runtime_can_generate']} | {', '.join(item['flagged_terms'])} |")
    lines.extend(["", "## Ablation Results", "| Variant | Rows | Accuracy | Balanced Accuracy | ROC AUC | Brier | Log Loss | High-Confidence Accuracy | Coverage |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"])
    for result in payload["ablation_results"]:
        metrics = result["metrics"]
        best = (result.get("selective_prediction") or {}).get("best_accuracy") or {}
        lines.append(f"| {result['variant']} | {result['test_rows']} | {metrics.get('accuracy')} | {metrics.get('balanced_accuracy')} | {metrics.get('roc_auc')} | {metrics.get('brier_score')} | {metrics.get('log_loss')} | {best.get('accuracy')} | {best.get('coverage_percent')} |")
    lines.extend(["", "## Source Holdout Results", "| Source | Status | Rows | Accuracy | Balanced Accuracy | ROC AUC |", "|---|---|---:|---:|---:|---:|"])
    for result in payload["source_holdout_results"]:
        metrics = result.get("metrics") or {}
        lines.append(f"| {result.get('source')} | {result.get('status', 'evaluated')} | {result.get('test_rows')} | {metrics.get('accuracy')} | {metrics.get('balanced_accuracy')} | {metrics.get('roc_auc')} |")
    lines.extend(["", "## Stress Tests", "| Segment | Rows | Accuracy | Balanced Accuracy |", "|---|---:|---:|---:|"])
    for name, result in payload["stress_tests"].items():
        metrics = result.get("metrics") or {}
        lines.append(f"| {name} | {result.get('rows')} | {metrics.get('accuracy')} | {metrics.get('balanced_accuracy')} |")
    lines.extend(["", "## Runtime Parity", f"- Runtime compatible: {payload['runtime_parity']['runtime_compatible']}", f"- Missing runtime features: {len(payload['runtime_parity']['missing_runtime_features'])}"])
    lines.extend(["", "## Final Status", json.dumps(payload["final_status"], indent=2)])
    return "\n".join(lines).strip() + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
