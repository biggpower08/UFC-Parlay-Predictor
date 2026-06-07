"""Train honest dedicated prop-model baselines when labels exist.

Imported Kaggle/local CSV data can provide event dates, method/round labels,
and fight-stat labels. Artifacts are marked trained only when the data is
chronological and validation clears a simple majority-class baseline; weak
but usable baselines are saved as experimental.
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
from ufc_predictor.features.feature_schema import get_feature_schema, normalize_model_family
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv
from ufc_predictor.training.metrics import classification_metrics, majority_class_baseline

MODEL_VERSION = "prop_baseline_v1"
FEATURE_NAMES = get_feature_schema("finish").required_features

MODEL_TARGETS = [
    ("finish_model", "finish_binary"),
    ("goes_distance_model", "goes_distance_binary"),
    ("method_model", "method_class"),
    ("round_model", "round_phase_class"),
    ("strike_volume_model", "combined_strike_volume_bucket"),
    ("takedown_control_model", "grappling_heavy_binary"),
]
ALL_MODEL_NAMES = [
    "winner_model",
    "finish_model",
    "goes_distance_model",
    "method_model",
    "round_model",
    "strike_volume_model",
    "takedown_control_model",
    "odds_calibration_model",
]
BLOCKED_TARGETS = {
    "winner_model": "Winner prediction already uses the existing sklearn/Elo pipeline; this pass does not retrain it.",
    "odds_calibration_model": "Historical odds snapshots are not available, so odds calibration/value modeling is blocked.",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Train dedicated prop models from available labels.")
    parser.add_argument("--dry-run", action="store_true", help="Audit and print the training plan without writing artifacts.")
    parser.add_argument("--input", default=str(settings.FIGHTS_CSV), help="Input fights CSV for training.")
    parser.add_argument("--source", default="csv", choices=["csv", "imported_csv", "ufcstats_cache", "manual_html"])
    parser.add_argument("--min-rows", type=int, default=500)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument(
        "--assume-reverse-chronological",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When event dates are missing, process cached CSV rows in reverse source order for an experimental split.",
    )
    args = parser.parse_args()

    default_import = settings.DATA_PROCESSED_DIR / "training_imports" / "normalized_fights.csv"
    input_path = args.input
    if args.source == "imported_csv" and args.input == str(settings.FIGHTS_CSV) and default_import.is_file():
        input_path = str(default_import)
    fights = load_fights_csv(input_path)
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
    registry = {}
    for model_name, target in MODEL_TARGETS:
        if plan[model_name]["status"] not in {"experimental", "trained"}:
            results[model_name] = plan[model_name]
            registry[model_name] = registry_entry_from_plan(model_name, plan[model_name], audit.to_dict())
            continue
        artifact = train_model(
            model_name=model_name,
            target=target,
            dataset=dataset,
            audit=audit.to_dict(),
            test_size=args.test_size,
            data_source=args.source,
            input_path=input_path,
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
        registry[model_name] = registry_entry_from_artifact(artifact, artifact_path)

    for model_name, reason in BLOCKED_TARGETS.items():
        registry[model_name] = blocked_registry_entry(model_name, reason, audit.to_dict())
        results.setdefault(model_name, {"status": "blocked", "reason": reason})

    metrics_path = settings.PROP_MODEL_METRICS_JSON
    metrics_path.write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    registry_path = settings.MODEL_REGISTRY_JSON
    registry_path.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")
    print(json.dumps({"trained": results, "metrics_path": str(metrics_path), "registry_path": str(registry_path)}, indent=2, default=str))
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
            "target": None,
            "status": "blocked",
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
    final_status, status_notes = final_status_from_metrics(status, metrics)
    metadata = {
        "model_name": model_name,
        "model_type": "nearest_centroid_softmax_baseline",
        "target_label": target,
        "status": final_status,
        "training_rows": int(len(train_rows)),
        "validation_rows": int(len(validation_rows)),
        "date_range": audit.get("date_range"),
        "data_source": data_source,
        "input_path": input_path,
        "split_type": "chronological" if audit.get("source_coverage", {}).get("has_event_date") else "source_order_reversed_experimental",
        "feature_names": FEATURE_NAMES,
        "class_distribution": {str(key): int(value) for key, value in rows[target].value_counts().to_dict().items()},
        "baseline_metrics": metrics["majority_class_baseline"],
        "source_datasets": [data_source],
        "source_files": [input_path],
        "trained_at": now,
        "data_cutoff_date": audit.get("date_range", {}).get("max") or f"source_order_{int(rows['source_order'].max())}",
        "training_source_status": "credible" if final_status == "trained" else "experimental",
        "leakage_checked": True,
        "limitations": limitations_for_status(final_status, audit, status_notes),
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


def final_status_from_metrics(planned_status: str, metrics: dict) -> tuple[str, list[str]]:
    if planned_status != "trained":
        return planned_status, []
    validation = metrics.get("validation", {})
    baseline = metrics.get("majority_class_baseline", {})
    validation_accuracy = float(validation.get("accuracy") or 0.0)
    baseline_accuracy = float(baseline.get("accuracy") or 0.0)
    balanced_accuracy = float(validation.get("balanced_accuracy") or 0.0)
    notes = []
    if validation_accuracy <= baseline_accuracy:
        notes.append(
            "Validation accuracy does not beat the majority-class baseline; keep this as an experimental read."
        )
    if balanced_accuracy < 0.45:
        notes.append(
            "Balanced accuracy is weak, so this model should not drive confident public wording yet."
        )
    if notes:
        return "experimental", notes
    return "trained", []


def registry_entry_from_artifact(artifact: dict, artifact_path: Path) -> dict:
    metadata = artifact["metadata"]
    metrics = artifact.get("metrics", {})
    rows_used = int(metadata["training_rows"]) + int(metadata["validation_rows"])
    schema = get_feature_schema(normalize_model_family(metadata["model_name"]))
    required_missing = [name for name in schema.required_features if name not in metadata["feature_names"]]
    optional_present = [name for name in schema.optional_features if name in metadata["feature_names"]]
    return {
        "model_name": metadata["model_name"],
        "target_label": metadata["target_label"],
        "model_family": "bettor_prop_read",
        "model_type": metadata.get("model_type"),
        "status": metadata["status"],
        "source_datasets": metadata.get("source_datasets", []),
        "source_files": metadata.get("source_files", []),
        "headline_metric_source": "chronological_validation" if metadata.get("split_type") == "chronological" else metadata.get("split_type"),
        "rows_used": rows_used,
        "artifact_path": str(artifact_path),
        "training_rows": metadata["training_rows"],
        "validation_rows": metadata["validation_rows"],
        "date_range": metadata["date_range"],
        "split_type": metadata["split_type"],
        "leakage_risk": "low" if metadata.get("leakage_checked") else "unknown_review_needed",
        "runtime_compatible": True,
        "feature_set_name": "prior_history_baseline_v1",
        "feature_schema_name": schema.schema_name,
        "feature_schema_version": schema.schema_version,
        "required_features_available": not required_missing,
        "optional_feature_coverage": round(len(optional_present) / max(1, len(schema.optional_features)), 4),
        "missing_runtime_features": required_missing,
        "feature_factory_supported": True,
        "odds_used": False,
        "segment_metrics_available": False,
        "calibration_metrics_available": bool((metrics.get("validation") or {}).get("log_loss") is not None),
        "metrics": metrics.get("validation", {}),
        "baseline_metrics": metrics.get("majority_class_baseline", {}),
        "feature_names": metadata["feature_names"],
        "class_distribution": metadata["class_distribution"],
        "limitations": metadata["limitations"],
        "trained_at": metadata["trained_at"],
    }


def registry_entry_from_plan(model_name: str, plan_entry: dict, audit: dict) -> dict:
    schema = get_feature_schema(normalize_model_family(model_name))
    return {
        "model_name": model_name,
        "target_label": plan_entry.get("target"),
        "model_family": "bettor_prop_read",
        "model_type": None,
        "status": plan_entry["status"],
        "source_datasets": [audit.get("source")],
        "source_files": [],
        "headline_metric_source": "unavailable",
        "rows_used": 0,
        "artifact_path": None,
        "training_rows": 0,
        "validation_rows": 0,
        "date_range": audit.get("date_range"),
        "split_type": "chronological" if audit.get("source_coverage", {}).get("has_event_date") else "unavailable",
        "leakage_risk": "unknown_review_needed",
        "runtime_compatible": False,
        "feature_set_name": None,
        "feature_schema_name": schema.schema_name,
        "feature_schema_version": schema.schema_version,
        "required_features_available": False,
        "optional_feature_coverage": 0.0,
        "missing_runtime_features": schema.required_features,
        "feature_factory_supported": True,
        "odds_used": False,
        "segment_metrics_available": False,
        "calibration_metrics_available": False,
        "metrics": {},
        "baseline_metrics": {},
        "feature_names": FEATURE_NAMES,
        "class_distribution": plan_entry.get("class_distribution", {}),
        "limitations": [plan_entry.get("reason", "Training data is not sufficient.")],
        "trained_at": None,
    }


def blocked_registry_entry(model_name: str, reason: str, audit: dict) -> dict:
    schema = get_feature_schema(normalize_model_family(model_name))
    return {
        "model_name": model_name,
        "target_label": None,
        "model_family": "winner" if model_name == "winner_model" else "odds_calibration",
        "model_type": None,
        "status": "blocked",
        "source_datasets": [audit.get("source")],
        "source_files": [],
        "headline_metric_source": "unavailable",
        "rows_used": 0,
        "artifact_path": None,
        "training_rows": 0,
        "validation_rows": 0,
        "date_range": audit.get("date_range"),
        "split_type": "unavailable",
        "leakage_risk": "unknown_review_needed",
        "runtime_compatible": False,
        "feature_set_name": None,
        "feature_schema_name": schema.schema_name,
        "feature_schema_version": schema.schema_version,
        "required_features_available": False,
        "optional_feature_coverage": 0.0,
        "missing_runtime_features": schema.required_features,
        "feature_factory_supported": model_name != "odds_calibration_model",
        "odds_used": model_name == "odds_calibration_model",
        "segment_metrics_available": False,
        "calibration_metrics_available": False,
        "metrics": {},
        "baseline_metrics": {},
        "feature_names": [],
        "class_distribution": {},
        "limitations": [reason],
        "trained_at": None,
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


def limitations_for_status(status: str, audit: dict, extra_notes: list[str] | None = None) -> list[str]:
    limitations = []
    if status == "experimental":
        if audit.get("source_coverage", {}).get("has_event_date"):
            limitations.append("Validation is weak; treat this as an experimental model-supported read, not a confident prop projection.")
        else:
            limitations.append("Event dates are missing; split uses reversed source order and should not be treated as production-grade chronological validation.")
    limitations.extend(extra_notes or [])
    limitations.extend(audit.get("warnings", []))
    limitations.append("Features are limited to pre-fight rolling win/finish/decision history from the available source order.")
    return limitations


if __name__ == "__main__":
    raise SystemExit(main())
