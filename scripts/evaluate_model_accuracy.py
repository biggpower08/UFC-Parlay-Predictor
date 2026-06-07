from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv
from ufc_predictor.training.deduping import stable_fight_key


FEATURE_NAMES = [
    "a_prior_fights",
    "b_prior_fights",
    "a_prior_wins",
    "b_prior_wins",
    "a_prior_finishes",
    "b_prior_finishes",
    "a_prior_decisions",
    "b_prior_decisions",
]

CLASSIFICATION_MODELS = {
    "finish_model": "finish_binary",
    "goes_distance_model": "goes_distance_binary",
    "method_model": "method_class",
    "round_phase_model": "round_phase_class",
    "strike_volume_model": "combined_strike_volume_bucket",
    "takedown_control_model": "grappling_heavy_binary",
}

REGRESSION_MODELS = {
    "strike_volume_regression": "combined_sig_strikes",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate UFC/MMA models on chronological held-out historical data.")
    parser.add_argument("--input-dir", default="data/imports")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--split", choices=["chronological"], default="chronological")
    parser.add_argument("--final-test-size", type=float, default=0.15)
    parser.add_argument("--validation-size", type=float, default=0.15)
    parser.add_argument("--calibrate", action="store_true")
    parser.add_argument("--by-segment", action="store_true")
    parser.add_argument("--force-rebuild", action="store_true", help="Require the current combined normalized import file instead of legacy training imports.")
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "model_accuracy_report.json"))
    parser.add_argument("--output-md", default="docs/model_accuracy_report.md")
    args = parser.parse_args()

    processed_dir = Path(args.processed_dir)
    input_path = processed_dir / "imports" / "normalized_fights_combined.csv"
    if not input_path.is_file() and not args.force_rebuild:
        input_path = processed_dir / "training_imports" / "normalized_fights.csv"
    if not input_path.is_file():
        print(json.dumps({"error": "normalized_training_data_missing", "expected": str(input_path), "hint": "Run scripts/preprocess_imported_datasets.py --input-root data\\imports --all --write-summary first."}, indent=2))
        return 2

    fights = load_fights_csv(input_path)
    dataset, audit = build_training_rows(fights, source="imported_csv")
    train, validation, test, split_report = chronological_train_validation_test_split(dataset, args.validation_size, args.final_test_size)
    models = {}
    for model_name, target in CLASSIFICATION_MODELS.items():
        models[model_name] = evaluate_classification_model(model_name, target, train, validation, test, by_segment=args.by_segment)
    for model_name, target in REGRESSION_MODELS.items():
        models[model_name] = evaluate_regression_model(model_name, target, train, validation, test, by_segment=args.by_segment)
    models["winner_model"] = blocked_model(
        "winner_model",
        "Winner labels exist in imported data, but known-winner sources are currently winner-oriented after normalization. A runtime winner model needs a safe fighter_1/fighter_2 orientation with mirrored rows kept together before it can be honestly evaluated.",
    )
    models["odds_calibration_model"] = blocked_model("odds_calibration_model", "Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps.")

    ranking = relative_ranking(models)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_data": str(input_path),
        "force_rebuild_requested": bool(args.force_rebuild),
        "audit": audit.to_dict(),
        "split": split_report,
        "source_contribution": source_contribution_report(dataset, train, validation, test),
        "models": models,
        "relative_ranking": ranking,
        "calibration": {"requested": args.calibrate, "status": "basic_probability_scores_only"},
    }
    write_json(Path(args.output_json), payload)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(markdown_report(payload), encoding="utf-8")
    update_registry_with_evaluation(models)
    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "ranking": ranking}, indent=2, default=str))
    return 0


def chronological_train_validation_test_split(dataset: pd.DataFrame, validation_size: float, test_size: float):
    rows = dataset.dropna(subset=["event_date"]).copy()
    rows["_event_date"] = pd.to_datetime(rows["event_date"], errors="coerce")
    rows = rows.dropna(subset=["_event_date"]).reset_index(drop=True)
    rows["_split_fight_key"] = rows.apply(canonical_split_key, axis=1)
    rows["_source_order_for_sort"] = rows["source_order"] if "source_order" in rows.columns else range(len(rows))
    group_order = (
        rows.groupby("_split_fight_key", dropna=False)
        .agg(_event_date=("_event_date", "min"), _source_order_for_sort=("_source_order_for_sort", "min"))
        .sort_values(["_event_date", "_source_order_for_sort"], kind="mergesort")
        .reset_index()
    )
    total_groups = len(group_order)
    test_count = max(1, int(total_groups * test_size))
    validation_count = max(1, int(total_groups * validation_size))
    train_end = max(1, total_groups - test_count - validation_count)
    validation_end = total_groups - test_count
    train_keys = set(group_order.iloc[:train_end]["_split_fight_key"])
    validation_keys = set(group_order.iloc[train_end:validation_end]["_split_fight_key"])
    test_keys = set(group_order.iloc[validation_end:]["_split_fight_key"])
    train = rows[rows["_split_fight_key"].isin(train_keys)].sort_values(["_event_date", "_source_order_for_sort"], kind="mergesort").copy()
    validation = rows[rows["_split_fight_key"].isin(validation_keys)].sort_values(["_event_date", "_source_order_for_sort"], kind="mergesort").copy()
    test = rows[rows["_split_fight_key"].isin(test_keys)].sort_values(["_event_date", "_source_order_for_sort"], kind="mergesort").copy()
    overlap = cross_split_keys(train, validation, test)
    return train, validation, test, {
        "split_type": "chronological",
        "train_rows": int(len(train)),
        "validation_rows": int(len(validation)),
        "test_rows": int(len(test)),
        "train_fight_groups": int(len(train_keys)),
        "validation_fight_groups": int(len(validation_keys)),
        "test_fight_groups": int(len(test_keys)),
        "canonical_group_key": "fight_key_or_stable_pair_key",
        "no_cross_split_fight_leakage": len(overlap) == 0,
        "cross_split_fight_keys": overlap[:20],
        "date_range_train": date_range(train),
        "date_range_validation": date_range(validation),
        "date_range_test": date_range(test),
        "final_test_held_out": True,
    }


def evaluate_classification_model(model_name: str, target: str, train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, by_segment: bool):
    rows_train = train.dropna(subset=FEATURE_NAMES + [target]).copy()
    rows_test = test.dropna(subset=FEATURE_NAMES + [target]).copy()
    if len(rows_train) < 500 or len(rows_test) < 100 or rows_train[target].nunique() < 2:
        return insufficient(model_name, target, len(rows_train), len(rows_test), rows_train, rows_test)
    classes = sorted(str(value) for value in set(rows_train[target].astype(str)) | set(rows_test[target].astype(str)))
    model = fit_nearest_centroid(rows_train[FEATURE_NAMES].astype(float).to_numpy(), rows_train[target].astype(str).tolist(), classes)
    probs = predict_probabilities(model, rows_test[FEATURE_NAMES].astype(float).to_numpy())
    preds = [classes[int(np.argmax(row))] for row in probs]
    y_true = rows_test[target].astype(str).tolist()
    majority = majority_baseline(y_true)
    metrics = classification_metrics(y_true, preds, probs, classes)
    main = metrics["accuracy"]
    baseline = majority["accuracy"]
    improvement = round(main - baseline, 4) if baseline is not None else None
    beats = bool(improvement is not None and improvement > 0)
    return {
        "model_name": model_name,
        "target": target,
        "status": "evaluated" if beats else "weak_or_failed_baseline",
        "test_rows": int(len(rows_test)),
        "train_rows": int(len(rows_train)),
        "validation_rows": int(len(validation.dropna(subset=[target]))),
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "source_contribution": source_contribution_report(pd.concat([rows_train, rows_test], ignore_index=True), rows_train, validation.dropna(subset=[target]).copy(), rows_test.iloc[0:0].copy(), rows_test),
        "feature_coverage": feature_coverage(pd.concat([rows_train, rows_test], ignore_index=True), FEATURE_NAMES + [target]),
        "final_test_metric_name": "accuracy",
        "final_test_metric": main,
        "baseline_metric": baseline,
        "relative_improvement": improvement,
        "beats_baseline": beats,
        "metrics": metrics,
        "majority_baseline": majority,
        "split_type": "chronological",
        "segment_metrics": segment_metrics(rows_test.assign(_pred=preds), target) if by_segment else {},
        "limitations": limitations(beats, metrics),
    }


def evaluate_regression_model(model_name: str, target: str, train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, by_segment: bool):
    rows_train = train.dropna(subset=[target]).copy()
    rows_test = test.dropna(subset=[target]).copy()
    if len(rows_train) < 500 or len(rows_test) < 100:
        return insufficient(model_name, target, len(rows_train), len(rows_test), rows_train, rows_test)
    prediction = float(rows_train[target].astype(float).median())
    y = rows_test[target].astype(float).to_numpy()
    preds = np.full(len(y), prediction)
    mae = float(np.mean(np.abs(y - preds)))
    rmse = float(np.sqrt(np.mean((y - preds) ** 2)))
    mean_prediction = float(rows_train[target].astype(float).mean())
    baseline_preds = np.full(len(y), mean_prediction)
    baseline_mae = float(np.mean(np.abs(y - baseline_preds)))
    improvement = (baseline_mae - mae) / baseline_mae if baseline_mae else None
    return {
        "model_name": model_name,
        "target": target,
        "status": "baseline_only",
        "test_rows": int(len(rows_test)),
        "train_rows": int(len(rows_train)),
        "validation_rows": int(len(validation.dropna(subset=[target]))),
        "feature_count": len(FEATURE_NAMES),
        "feature_names": FEATURE_NAMES,
        "source_contribution": source_contribution_report(pd.concat([rows_train, rows_test], ignore_index=True), rows_train, validation.dropna(subset=[target]).copy(), rows_test.iloc[0:0].copy(), rows_test),
        "feature_coverage": feature_coverage(pd.concat([rows_train, rows_test], ignore_index=True), FEATURE_NAMES + [target]),
        "final_test_metric_name": "mae",
        "final_test_metric": round(mae, 4),
        "baseline_metric": round(baseline_mae, 4),
        "relative_improvement": round(improvement, 4) if improvement is not None else None,
        "beats_baseline": bool(improvement is not None and improvement > 0),
        "metrics": {"mae": round(mae, 4), "rmse": round(rmse, 4), "median_absolute_error": round(float(np.median(np.abs(y - preds))), 4)},
        "split_type": "chronological",
        "segment_metrics": {},
        "limitations": ["Regression model is currently a simple baseline harness; add trained regressors before public use."],
    }


def fit_nearest_centroid(X, y, classes):
    scales = X.std(axis=0)
    scales[scales == 0] = 1.0
    X_scaled = X / scales
    centroids = []
    for cls in classes:
        rows = X_scaled[[label == cls for label in y]]
        centroids.append(rows.mean(axis=0))
    return {"classes": classes, "scales": scales, "centroids": np.vstack(centroids)}


def predict_probabilities(model, X):
    X_scaled = X / model["scales"]
    distances = np.stack([np.linalg.norm(X_scaled - centroid, axis=1) for centroid in model["centroids"]], axis=1)
    scores = -distances
    scores = scores - scores.max(axis=1, keepdims=True)
    exp = np.exp(scores)
    return exp / exp.sum(axis=1, keepdims=True)


def classification_metrics(y_true, y_pred, probs, classes):
    accuracy = sum(a == p for a, p in zip(y_true, y_pred)) / len(y_true)
    recalls = []
    matrix = {str(actual): {str(pred): 0 for pred in classes} for actual in classes}
    for actual, pred in zip(y_true, y_pred):
        matrix[str(actual)][str(pred)] += 1
    for cls in classes:
        total = sum(1 for actual in y_true if actual == cls)
        correct = sum(1 for actual, pred in zip(y_true, y_pred) if actual == cls and pred == cls)
        recalls.append(correct / total if total else 0)
    return {
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(sum(recalls) / len(recalls), 4),
        "f1_macro": round(macro_f1(y_true, y_pred, classes), 4),
        "roc_auc": round(binary_auc(y_true, probs, classes), 4) if len(classes) == 2 else None,
        "log_loss": round(log_loss(y_true, probs, classes), 4),
        "brier_score": round(brier_score(y_true, probs, classes), 4) if len(classes) == 2 else None,
        "confusion_matrix": matrix,
    }


def macro_f1(y_true, y_pred, classes):
    scores = []
    for cls in classes:
        tp = sum(1 for a, p in zip(y_true, y_pred) if a == cls and p == cls)
        fp = sum(1 for a, p in zip(y_true, y_pred) if a != cls and p == cls)
        fn = sum(1 for a, p in zip(y_true, y_pred) if a == cls and p != cls)
        precision = tp / (tp + fp) if (tp + fp) else 0
        recall = tp / (tp + fn) if (tp + fn) else 0
        scores.append(2 * precision * recall / (precision + recall) if precision + recall else 0)
    return sum(scores) / len(scores) if scores else 0


def majority_baseline(y_true):
    counts = pd.Series(y_true).value_counts()
    if counts.empty:
        return {"label": None, "accuracy": None, "class_counts": {}}
    return {"label": str(counts.index[0]), "accuracy": round(float(counts.iloc[0]) / len(y_true), 4), "class_counts": {str(k): int(v) for k, v in counts.items()}}


def log_loss(y_true, probs, classes):
    index = {label: i for i, label in enumerate(classes)}
    eps = 1e-15
    values = [-math.log(max(eps, min(1 - eps, row[index[actual]]))) for actual, row in zip(y_true, probs)]
    return sum(values) / len(values)


def brier_score(y_true, probs, classes):
    positive = classes[-1]
    pos_index = len(classes) - 1
    return sum((float(actual == positive) - row[pos_index]) ** 2 for actual, row in zip(y_true, probs)) / len(y_true)


def binary_auc(y_true, probs, classes):
    positive = classes[-1]
    pos_index = len(classes) - 1
    scores = sorted((row[pos_index], actual == positive) for actual, row in zip(y_true, probs))
    positives = sum(1 for _, is_pos in scores if is_pos)
    negatives = len(scores) - positives
    if positives == 0 or negatives == 0:
        return None
    rank_sum = sum(rank for rank, (_, is_pos) in enumerate(scores, 1) if is_pos)
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)


def segment_metrics(rows: pd.DataFrame, target: str):
    segments = {}
    if "weight_class" in rows.columns:
        for weight_class, group in rows.groupby("weight_class"):
            if len(group) >= 50:
                segments[f"weight_class:{weight_class}"] = segment_accuracy(group, target)
    if "minimum_history_count" in rows.columns:
        enough = rows[rows["minimum_history_count"] >= 3]
        low = rows[rows["minimum_history_count"] < 3]
        if len(enough) >= 50:
            segments["enough_fighter_history"] = segment_accuracy(enough, target)
        if len(low) >= 50:
            segments["low_fighter_history"] = segment_accuracy(low, target)
    return segments


def segment_accuracy(group, target):
    return {"rows": int(len(group)), "accuracy": round(float((group[target].astype(str) == group["_pred"].astype(str)).mean()), 4)}


def insufficient(model_name, target, train_rows, test_rows, rows_train=None, rows_test=None):
    rows_train = rows_train if rows_train is not None else pd.DataFrame()
    rows_test = rows_test if rows_test is not None else pd.DataFrame()
    return {
        "model_name": model_name,
        "target": target,
        "status": "insufficient_data",
        "train_rows": int(train_rows),
        "test_rows": int(test_rows),
        "feature_count": len(FEATURE_NAMES),
        "source_contribution": source_contribution_report(pd.concat([rows_train, rows_test], ignore_index=True), rows_train, pd.DataFrame(), pd.DataFrame(), rows_test),
        "beats_baseline": False,
        "limitations": ["Not enough held-out rows/classes for honest evaluation."],
    }


def blocked_model(model_name, reason):
    return {"model_name": model_name, "target": None, "status": "blocked", "test_rows": 0, "feature_count": 0, "source_contribution": {}, "beats_baseline": False, "limitations": [reason]}


def limitations(beats, metrics):
    notes = []
    if not beats:
        notes.append("Does not beat majority-class baseline on final chronological test set.")
    if metrics.get("balanced_accuracy", 0) < 0.45:
        notes.append("Balanced accuracy is weak; keep as experimental context.")
    return notes


def relative_ranking(models):
    rows = []
    for name, model in models.items():
        improvement = model.get("relative_improvement")
        rows.append({"model": name, "status": model.get("status"), "relative_improvement": improvement, "beats_baseline": model.get("beats_baseline", False)})
    return sorted(rows, key=lambda item: (item["relative_improvement"] is not None, item["relative_improvement"] or -999), reverse=True)


def date_range(frame):
    if frame.empty:
        return {"min": None, "max": None}
    return {"min": str(frame["_event_date"].min().date()), "max": str(frame["_event_date"].max().date())}


def canonical_split_key(row: pd.Series) -> str:
    for column in ("fight_key", "canonical_fight_id"):
        value = row.get(column)
        if value is not None and not pd.isna(value) and str(value).strip():
            return str(value)
    return stable_fight_key(
        {
            "event_date": row.get("event_date"),
            "event": row.get("event"),
            "fighter_1": row.get("fighter_a"),
            "fighter_2": row.get("fighter_b"),
            "weight_class": row.get("weight_class"),
        }
    )


def cross_split_keys(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame) -> list[str]:
    train_keys = set(train.get("_split_fight_key", pd.Series(dtype=str)).dropna().astype(str))
    validation_keys = set(validation.get("_split_fight_key", pd.Series(dtype=str)).dropna().astype(str))
    test_keys = set(test.get("_split_fight_key", pd.Series(dtype=str)).dropna().astype(str))
    return sorted((train_keys & validation_keys) | (train_keys & test_keys) | (validation_keys & test_keys))


def source_contribution_report(dataset: pd.DataFrame, train: pd.DataFrame, validation: pd.DataFrame, _unused: pd.DataFrame | None = None, test: pd.DataFrame | None = None) -> dict:
    if test is None:
        test = _unused if _unused is not None else pd.DataFrame()
    return {
        "all_rows_by_dataset": source_counts(dataset),
        "train_rows_by_dataset": source_counts(train),
        "validation_rows_by_dataset": source_counts(validation),
        "test_rows_by_dataset": source_counts(test),
        "unique_fight_groups_by_dataset": unique_group_counts(dataset),
    }


def source_counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty:
        return {}
    if "source_dataset" not in frame.columns:
        return {"unknown": int(len(frame))}
    counts = frame["source_dataset"].fillna("unknown").astype(str).value_counts().sort_index()
    return {str(key): int(value) for key, value in counts.items()}


def unique_group_counts(frame: pd.DataFrame) -> dict[str, int]:
    if frame.empty:
        return {}
    rows = frame.copy()
    if "_split_fight_key" not in rows.columns:
        rows["_split_fight_key"] = rows.apply(canonical_split_key, axis=1)
    if "source_dataset" not in rows.columns:
        return {"unknown": int(rows["_split_fight_key"].nunique())}
    return {
        str(dataset): int(group["_split_fight_key"].nunique())
        for dataset, group in rows.groupby(rows["source_dataset"].fillna("unknown").astype(str))
    }


def feature_coverage(frame: pd.DataFrame, columns: list[str]) -> dict[str, float]:
    rows = len(frame)
    if rows == 0:
        return {column: 0.0 for column in columns}
    return {column: round(float(frame[column].notna().sum()) / rows, 4) if column in frame.columns else 0.0 for column in columns}


def update_registry_with_evaluation(models):
    path = settings.MODEL_REGISTRY_JSON
    registry = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    now = datetime.now(timezone.utc).isoformat()
    for name, result in models.items():
        entry = registry.setdefault(name, {"model_name": name})
        entry.update(
            {
                "final_test_metric": result.get("final_test_metric"),
                "final_test_metric_name": result.get("final_test_metric_name"),
                "baseline_metric": result.get("baseline_metric"),
                "relative_improvement": result.get("relative_improvement"),
                "beats_baseline": result.get("beats_baseline", False),
                "test_rows": result.get("test_rows", 0),
                "split_type": result.get("split_type", "chronological"),
                "calibration_status": "basic_probability_scores_only",
                "segment_metrics_available": bool(result.get("segment_metrics")),
                "evaluated_at": now,
            }
        )
        if not result.get("beats_baseline", False) and entry.get("status") == "trained":
            entry["status"] = "experimental"
            entry.setdefault("limitations", []).append("Final held-out evaluation did not clearly support production-ready status.")
    path.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def markdown_report(payload):
    lines = [
        "# Model Accuracy Report",
        "",
        "## Plain-English Summary",
        "Models were evaluated on the newest chronological holdout from normalized historical fight data. Metrics are approximate final-test results, not guarantees.",
        "",
        "## Split",
        f"- Train: {payload['split']['train_rows']} rows, {payload['split']['date_range_train']}",
        f"- Validation: {payload['split']['validation_rows']} rows, {payload['split']['date_range_validation']}",
        f"- Final test: {payload['split']['test_rows']} rows, {payload['split']['date_range_test']}",
        f"- Fight-group leakage check: {payload['split'].get('no_cross_split_fight_leakage')}",
        "",
        "## Source Contributions",
        f"- All rows by dataset: {payload['source_contribution']['all_rows_by_dataset']}",
        f"- Train rows by dataset: {payload['source_contribution']['train_rows_by_dataset']}",
        f"- Validation rows by dataset: {payload['source_contribution']['validation_rows_by_dataset']}",
        f"- Final test rows by dataset: {payload['source_contribution']['test_rows_by_dataset']}",
        "",
        "## Model Ranking",
        "| Model | Status | Test Rows | Main Metric | Baseline | Improvement | Beats Baseline | Notes |",
        "|---|---|---:|---:|---:|---:|---|---|",
    ]
    for item in payload["relative_ranking"]:
        model = payload["models"][item["model"]]
        lines.append(
            f"| {item['model']} | {model.get('status')} | {model.get('test_rows', 0)} | {model.get('final_test_metric', '')} | {model.get('baseline_metric', '')} | {model.get('relative_improvement', '')} | {model.get('beats_baseline', False)} | {'; '.join(model.get('limitations', []))} |"
        )
    lines.append("")
    lines.append("## Segment Performance")
    for name, model in payload["models"].items():
        if model.get("segment_metrics"):
            lines.append(f"### {name}")
            for segment, metrics in model["segment_metrics"].items():
                lines.append(f"- {segment}: {metrics}")
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
