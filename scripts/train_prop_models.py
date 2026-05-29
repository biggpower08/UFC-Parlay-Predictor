"""Train honest dedicated prop-model baselines when labels exist.

Current cached CSV data has fight result/method/round labels but no event dates
and no per-fight strike or takedown/control labels. Models trained from this
data are therefore marked experimental, not production-ready.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv
from ufc_predictor.training.metrics import classification_metrics, majority_class_baseline

MODEL_VERSION = "prop_baseline_v1"
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

MODEL_TARGETS = [
    ("finish_model", "finish_binary"),
    ("goes_distance_model", "goes_distance_binary"),
    ("method_model", "method_class"),
    ("round_model", "round_phase_class"),
]
BLOCKED_TARGETS = {
    "strike_volume_model": "Missing per-fight significant strike totals.",
    "takedown_control_model": "Missing per-fight takedown/control labels.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Train dedicated prop models from available labels.")
    parser.add_argument("--dry-run", action="store_true", help="Audit and print the training plan without writing artifacts.")
    parser.add_argument("--input", default=str(settings.FIGHTS_CSV), help="Input fights CSV for training.")
    parser.add_argument("--source", default="csv", choices=["csv", "ufcstats_cache", "manual_html"])
    parser.add_argument("--min-rows", type=int, default=500)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument(
        "--assume-reverse-chronological",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When event dates are missing, process cached CSV rows in reverse source order for an experimental split.",
    )
    args = parser.parse_args()

    fights = load_fights_csv(args.input)
    dataset, audit = build_training_rows(
        fights,
        source=args.source,
        assume_reverse_chronological=args.assume_reverse_chronological,
    )
    plan = training_plan(dataset, audit.to_dict(), args.min_rows)
    print(json.dumps({"audit": audit.to_dict(), "training_plan": plan}, indent=2, default=str))
    if args.dry_run:
        return 0

    settings.PROP_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    settings.DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results = {}
    for model_name, target in MODEL_TARGETS:
        if plan[model_name]["status"] not in {"experimental", "trained"}:
            results[model_name] = plan[model_name]
            continue
        artifact = train_model(
            model_name=model_name,
            target=target,
            dataset=dataset,
            audit=audit.to_dict(),
            test_size=args.test_size,
            data_source=args.source,
            input_path=args.input,
            status=plan[model_name]["status"],
        )
        artifact_path = settings.PROP_MODELS_DIR / f"{model_name}.json"
        artifact_path.write_text(json.dumps(artifact, indent=2, default=str), encoding="utf-8")
        results[model_name] = {
            "status": artifact["metadata"]["status"],
            "artifact_path": str(artifact_path),
            "metrics": artifact["metrics"],
            "class_distribution": artifact["metadata"]["class_distribution"],
        }

    metrics_path = settings.PROP_MODEL_METRICS_JSON
    metrics_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"trained": results, "metrics_path": str(metrics_path)}, indent=2, default=str))
    return 0


def training_plan(dataset, audit: dict, min_rows: int) -> dict:
    labels = audit.get("label_availability", {})
    has_dates = bool(audit.get("source_coverage", {}).get("has_event_date"))
    status = "trained" if has_dates else "experimental"
    plan = {}
    for model_name, target in MODEL_TARGETS:
        rows = int(labels.get(target, 0) or 0)
        distribution = audit.get("class_distributions", {}).get(target, {})
        if rows < min_rows:
            model_status = "insufficient_data"
            reason = f"Only {rows} rows available for {target}; minimum is {min_rows}."
        elif len(distribution) < 2:
            model_status = "insufficient_data"
            reason = f"Target {target} has fewer than two classes."
        else:
            model_status = status
            reason = "Event dates are available." if has_dates else "Event dates are missing; training is experimental using source-order split."
        plan[model_name] = {
            "target": target,
            "status": model_status,
            "rows": rows,
            "class_distribution": distribution,
            "reason": reason,
        }
    for model_name, reason in BLOCKED_TARGETS.items():
        plan[model_name] = {
            "status": "insufficient_data",
            "rows": 0,
            "class_distribution": {},
            "reason": reason,
        }
    return plan


def train_model(model_name: str, target: str, dataset, audit: dict, test_size: float, data_source: str, input_path: str, status: str) -> dict:
    rows = dataset.dropna(subset=FEATURE_NAMES + [target]).copy()
    rows = rows.reset_index(drop=True)
    split_at = max(1, int(len(rows) * (1 - test_size)))
    train_rows = rows.iloc[:split_at]
    validation_rows = rows.iloc[split_at:]
    if validation_rows.empty:
        raise RuntimeError(f"No validation rows for {model_name}.")

    X_train = train_rows[FEATURE_NAMES].astype(float).to_numpy()
    X_validation = validation_rows[FEATURE_NAMES].astype(float).to_numpy()
    y_train = [str(value) for value in train_rows[target].tolist()]
    y_validation = [str(value) for value in validation_rows[target].tolist()]
    classes = sorted(set(y_train) | set(y_validation))
    model = fit_nearest_centroid(X_train, y_train, classes)
    train_probs = predict_probabilities(model, X_train)
    validation_probs = predict_probabilities(model, X_validation)
    train_predictions = [classes[int(np.argmax(probs))] for probs in train_probs]
    validation_predictions = [classes[int(np.argmax(probs))] for probs in validation_probs]
    metrics = {
        "train": classification_metrics(y_train, train_predictions, train_probs.tolist(), classes),
        "validation": classification_metrics(y_validation, validation_predictions, validation_probs.tolist(), classes),
        "majority_class_baseline": majority_class_baseline(y_validation),
        "calibration_notes": "Baseline probabilities are centroid-distance softmax scores and are not calibrated.",
    }
    now = datetime.now(timezone.utc).isoformat()
    metadata = {
        "model_name": model_name,
        "model_type": "nearest_centroid_softmax_baseline",
        "target_label": target,
        "status": status,
        "training_rows": int(len(train_rows)),
        "validation_rows": int(len(validation_rows)),
        "date_range": audit.get("date_range"),
        "data_source": data_source,
        "input_path": input_path,
        "split_type": "chronological" if audit.get("source_coverage", {}).get("has_event_date") else "source_order_reversed_experimental",
        "feature_names": FEATURE_NAMES,
        "class_distribution": {str(key): int(value) for key, value in rows[target].value_counts().to_dict().items()},
        "trained_at": now,
        "data_cutoff_date": audit.get("date_range", {}).get("max") or f"source_order_{int(rows['source_order'].max())}",
        "training_source_status": "credible" if status == "trained" else "experimental",
        "leakage_checked": True,
        "limitations": limitations_for_status(status, audit),
        "model_version": MODEL_VERSION,
    }
    return {
        "model_name": model_name,
        "model_version": MODEL_VERSION,
        "model_type": metadata["model_type"],
        "feature_names": FEATURE_NAMES,
        "classes": classes,
        "centroids": model["centroids"].tolist(),
        "scales": model["scales"].tolist(),
        "metrics": metrics,
        "metadata": metadata,
    }


def fit_nearest_centroid(X, y, classes) -> dict:
    scales = X.std(axis=0)
    scales[scales == 0] = 1.0
    X_scaled = X / scales
    centroids = []
    for cls in classes:
        class_rows = X_scaled[[label == cls for label in y]]
        centroids.append(class_rows.mean(axis=0))
    return {"centroids": np.vstack(centroids), "scales": scales}


def predict_probabilities(model: dict, X) -> np.ndarray:
    X_scaled = X / model["scales"]
    distances = np.stack([np.linalg.norm(X_scaled - centroid, axis=1) for centroid in model["centroids"]], axis=1)
    scores = -distances
    scores = scores - scores.max(axis=1, keepdims=True)
    exp = np.exp(scores)
    return exp / exp.sum(axis=1, keepdims=True)


def limitations_for_status(status: str, audit: dict) -> list[str]:
    limitations = []
    if status == "experimental":
        limitations.append("Event dates are missing; split uses reversed source order and should not be treated as production-grade chronological validation.")
    limitations.extend(audit.get("warnings", []))
    limitations.append("Features are limited to pre-fight rolling win/finish/decision history from the available source order.")
    return limitations


if __name__ == "__main__":
    raise SystemExit(main())
