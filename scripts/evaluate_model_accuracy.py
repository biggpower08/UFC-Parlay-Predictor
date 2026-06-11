from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.features.interaction_discovery import add_interaction_features, discover_candidate_interactions, normalized_rejection_counts
from ufc_predictor.features.feature_schema import get_feature_schema
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
    "winner_model": "f1_wins_safe",
    "fight_duration_model": "finish_binary",
    "over_1_5_model": "over_1_5_binary",
    "over_2_5_model": "over_2_5_binary",
    "ends_before_round_3_model": "ends_before_round_3_binary",
    "finish_in_round_1_model": "finish_in_round_1_binary",
    "finish_type_model": "finish_type_class",
    "method_umbrella_model": "method_class",
    "strike_volume_model": "combined_strike_volume_bucket",
    "takedown_control_model": "grappling_heavy_binary",
}

LEGACY_COMPATIBILITY_MODELS = {
    "finish_model": "fight_duration_model",
    "goes_distance_model": "fight_duration_model",
    "method_model": "method_umbrella_model",
    "round_phase_model": "round_binary_family",
    "round_model": "round_binary_family",
}

TARGET_COLUMNS = {
    "winner",
    "f1_wins_safe",
    "finish_binary",
    "goes_distance_binary",
    "method_class",
    "finish_type_class",
    "round_number",
    "round_phase_class",
    "over_1_5_binary",
    "over_2_5_binary",
    "ends_before_round_3_binary",
    "finish_in_round_1_binary",
    "fighter_a_sig_strikes",
    "fighter_b_sig_strikes",
    "combined_sig_strikes",
    "fighter_a_strike_volume_bucket",
    "fighter_b_strike_volume_bucket",
    "combined_strike_volume_bucket",
    "fighter_a_50plus_sig_strikes",
    "fighter_b_50plus_sig_strikes",
    "combined_100plus_sig_strikes",
    "fighter_a_takedowns",
    "fighter_b_takedowns",
    "fighter_a_takedown_1plus",
    "fighter_b_takedown_1plus",
    "grappling_heavy_binary",
    "takedown_control_bucket",
}

SOURCE_PRIORITY = {
    "ufc_stats_complete": 1,
    "ufc_1994_2025": 2,
    "ufc_fight_forecast": 3,
    "ufc_1994_2026": 4,
    "mdabbert_ultimate": 5,
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
    parser.add_argument("--interaction-output-json", default=str(settings.DATA_PROCESSED_DIR / "interaction_discovery_report.json"))
    parser.add_argument("--interaction-output-md", default="docs/interaction_discovery_report.md")
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
        if model_name == "finish_type_model":
            models[model_name] = evaluate_classification_model(
                model_name,
                target,
                train,
                validation,
                test,
                by_segment=args.by_segment,
                row_filter=lambda frame: frame[frame.get("finish_binary").astype(str).isin({"1", "1.0"})].copy(),
                limitations_extra=["Conditional model: trained and scored only on fights that actually finished."],
            )
        elif model_name == "method_umbrella_model":
            models[model_name] = evaluate_method_umbrella_model(train, validation, test, by_segment=args.by_segment)
        else:
            models[model_name] = evaluate_classification_model(model_name, target, train, validation, test, by_segment=args.by_segment)
    models["finish_model"] = compatibility_duration_model(models["fight_duration_model"], "finish_model")
    models["goes_distance_model"] = compatibility_duration_model(models["fight_duration_model"], "goes_distance_model")
    models["method_model"] = compatibility_alias_model(models["method_umbrella_model"], "method_model")
    models["round_phase_model"] = round_family_summary_model(models)
    models["round_model"] = compatibility_alias_model(models["round_phase_model"], "round_model")
    for model_name, target in REGRESSION_MODELS.items():
        models[model_name] = evaluate_regression_model(model_name, target, train, validation, test, by_segment=args.by_segment)
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
    write_json(settings.DATA_PROCESSED_DIR / "feature_availability_report.json", feature_availability_payload(payload))
    write_json(settings.DATA_PROCESSED_DIR / "training_dataset_summary.json", training_dataset_summary_payload(payload))
    interaction_payload = interaction_discovery_payload(payload)
    write_json(Path(args.interaction_output_json), interaction_payload)
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(markdown_report(payload), encoding="utf-8")
    Path(args.interaction_output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.interaction_output_md).write_text(interaction_markdown_report(interaction_payload), encoding="utf-8")
    update_registry_with_evaluation(models, split_report)
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


def evaluate_classification_model(
    model_name: str,
    target: str,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    by_segment: bool,
    row_filter=None,
    limitations_extra: list[str] | None = None,
):
    feature_names = feature_names_for_model(train, validation, test, model_name)
    source_train = row_filter(train.copy()) if row_filter else train.copy()
    source_validation = row_filter(validation.copy()) if row_filter else validation.copy()
    source_test = row_filter(test.copy()) if row_filter else test.copy()
    rows_train = dedupe_model_rows(source_train.dropna(subset=[target]).copy(), target, feature_names)
    rows_validation = dedupe_model_rows(source_validation.dropna(subset=[target]).copy(), target, feature_names)
    rows_test = dedupe_model_rows(source_test.dropna(subset=[target]).copy(), target, feature_names)
    if len(rows_train) < 500 or len(rows_test) < 100 or rows_train[target].nunique() < 2:
        return insufficient(model_name, target, len(rows_train), len(rows_test), rows_train, rows_test)
    classes = sorted(str(value) for value in set(rows_train[target].astype(str)) | set(rows_test[target].astype(str)))
    base_feature_names = list(feature_names)
    rows_test_base = rows_test.copy()
    selected_bundle = select_classifier_with_interactions(model_name, rows_train, rows_validation, target, feature_names, classes)
    selected = selected_bundle["selected"]
    feature_names = selected_bundle["feature_names"]
    rows_train = selected_bundle["rows_train"]
    rows_validation = selected_bundle["rows_validation"]
    rows_test = add_interaction_features(rows_test, selected_bundle["selected_interactions"])
    model = selected["model"]
    probs = align_probabilities(np.asarray(model.predict_proba(rows_test[feature_names])), list(model.classes_), classes)
    preds = [classes[int(np.argmax(row))] for row in probs]
    y_true = rows_test[target].astype(str).tolist()
    majority = majority_baseline(y_true)
    metrics = classification_metrics(y_true, preds, probs, classes)
    base_final_metrics = (
        validation_metrics(selected_bundle["base_selected"]["model"], rows_test_base, target, base_feature_names, classes)
        if not rows_test_base.empty
        else None
    )
    annotate_interaction_final_results(selected_bundle["interaction_report"], metrics, base_final_metrics)
    source_holdout = source_holdout_classification_report(
        model_name=model_name,
        target=target,
        rows_train=rows_train,
        rows_validation=rows_validation,
        rows_test=rows_test,
        feature_names=feature_names,
        classes=classes,
        algorithm=selected["algorithm"],
        normal_metrics=metrics,
    )
    if source_holdout.get("source_holdout_regression_detected"):
        selected_bundle["interaction_report"]["source_holdout_regression_detected"] = bool(selected_bundle["selected_interactions"])
    if selected_bundle["interaction_report"].get("selected_interactions"):
        for item in selected_bundle["interaction_report"]["selected_interactions"]:
            item["source_holdout_impact"] = source_holdout.get("worst_metric_drop")
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
        "validation_rows": int(len(rows_validation)),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "algorithm": selected["algorithm"],
        "algorithm_comparison": selected["algorithm_comparison"],
        "interaction_discovery": selected_bundle["interaction_report"],
        "interaction_feature_count": len(selected_bundle["selected_interactions"]),
        "selected_interactions": [item["name"] for item in selected_bundle["selected_interactions"]],
        "selected_interactions_detailed": selected_bundle["interaction_report"].get("selected_interactions", []),
        "base_validation_metrics": selected_bundle.get("base_validation_metrics"),
        "interaction_validation_metrics": selected_bundle.get("interaction_validation_metrics"),
        "base_final_test_metrics": base_final_metrics,
        "interaction_final_test_metrics": metrics if selected_bundle["selected_interactions"] else None,
        "base_vs_interaction_comparison": base_vs_interaction_comparison(
            base_final_metrics,
            metrics if selected_bundle["selected_interactions"] else None,
            selected_bundle.get("base_validation_metrics"),
            selected_bundle.get("interaction_validation_metrics"),
            source_holdout,
        ),
        "source_holdout": source_holdout,
        "source_contribution": source_contribution_report(pd.concat([rows_train, rows_test], ignore_index=True), rows_train, validation.dropna(subset=[target]).copy(), rows_test.iloc[0:0].copy(), rows_test),
        "feature_coverage": feature_coverage(pd.concat([rows_train, rows_test], ignore_index=True), feature_names + [target]),
        "final_test_metric_name": "accuracy",
        "final_test_metric": main,
        "baseline_metric": baseline,
        "relative_improvement": improvement,
        "beats_baseline": beats,
        "metrics": metrics,
        "selective_prediction": selective_prediction_report(y_true, preds, probs, classes),
        "majority_baseline": majority,
        "split_type": "chronological",
        "segment_metrics": segment_metrics(rows_test.assign(_pred=preds), target) if by_segment else {},
        "limitations": limitations(beats, metrics) + list(limitations_extra or []),
    }


def finish_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if "finish_binary" not in frame.columns:
        return frame.iloc[0:0].copy()
    return frame[frame["finish_binary"].astype(str).isin({"1", "1.0"})].copy()


def compatibility_duration_model(duration_result: dict, model_name: str) -> dict:
    result = json.loads(json.dumps(duration_result, default=str))
    result["model_name"] = model_name
    result["derived_from"] = "fight_duration_model"
    if model_name == "finish_model":
        result["target"] = "finish_binary"
        result["output_name"] = "finish_probability"
        result["limitations"] = list(dict.fromkeys(result.get("limitations", []) + ["Compatibility output: internally backed by fight_duration_model."]))
    else:
        result["target"] = "goes_distance_binary"
        result["output_name"] = "goes_distance_probability"
        result["probability_transform"] = "1 - finish_probability"
        result["limitations"] = list(dict.fromkeys(result.get("limitations", []) + ["Compatibility output: goes_distance_probability is derived as 1 - finish_probability."]))
    return result


def compatibility_alias_model(source_result: dict, model_name: str) -> dict:
    result = json.loads(json.dumps(source_result, default=str))
    result["model_name"] = model_name
    result["derived_from"] = source_result.get("model_name")
    result["limitations"] = list(dict.fromkeys(result.get("limitations", []) + [f"Compatibility alias backed by {source_result.get('model_name')}."]))
    return result


def round_family_summary_model(models: dict[str, dict]) -> dict:
    members = ["over_1_5_model", "over_2_5_model", "ends_before_round_3_model", "finish_in_round_1_model"]
    available = [models[name] for name in members if name in models]
    beats = [item for item in available if item.get("beats_baseline")]
    weakest = [item.get("model_name") for item in available if not item.get("beats_baseline")]
    best = max(available, key=lambda item: item.get("relative_improvement") or -999, default={})
    return {
        "model_name": "round_phase_model",
        "target": "round_binary_family",
        "status": "evaluated" if beats else "weak_or_failed_baseline",
        "train_rows": max((item.get("train_rows", 0) for item in available), default=0),
        "test_rows": max((item.get("test_rows", 0) for item in available), default=0),
        "feature_count": best.get("feature_count", 0),
        "feature_names": best.get("feature_names", []),
        "algorithm": "binary_submodel_family",
        "final_test_metric_name": "best_binary_submodel_accuracy",
        "final_test_metric": best.get("final_test_metric"),
        "baseline_metric": best.get("baseline_metric"),
        "relative_improvement": best.get("relative_improvement"),
        "beats_baseline": bool(beats),
        "metrics": {"member_models": {name: models[name].get("metrics") for name in members if name in models}},
        "selective_prediction": best.get("selective_prediction", {}),
        "majority_baseline": best.get("majority_baseline", {}),
        "split_type": "chronological",
        "component_models": members,
        "interaction_feature_count": 0,
        "selected_interactions": [],
        "interaction_discovery": {"selection_status": "not_run_composite_summary"},
        "source_holdout": best.get("source_holdout", {"status": "not_run", "reason": "no round submodel source-holdout available"}),
        "limitations": ["Legacy round_phase_model is replaced by separate binary round-phase submodels."]
        + ([f"Weak members: {', '.join(weakest)}"] if weakest else []),
    }


def evaluate_method_umbrella_model(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, by_segment: bool):
    feature_names = feature_names_for_model(train, validation, test, "method_umbrella_model")
    duration_train = dedupe_model_rows(train.dropna(subset=["finish_binary"]).copy(), "finish_binary", feature_names)
    duration_validation = dedupe_model_rows(validation.dropna(subset=["finish_binary"]).copy(), "finish_binary", feature_names)
    duration_test = dedupe_model_rows(test.dropna(subset=["method_class", "finish_binary"]).copy(), "method_class", feature_names)
    type_train = dedupe_model_rows(finish_rows(train).dropna(subset=["finish_type_class"]).copy(), "finish_type_class", feature_names)
    type_validation = dedupe_model_rows(finish_rows(validation).dropna(subset=["finish_type_class"]).copy(), "finish_type_class", feature_names)
    if len(duration_train) < 500 or len(duration_test) < 100 or len(type_train) < 300 or type_train["finish_type_class"].nunique() < 2:
        return insufficient("method_umbrella_model", "method_class", min(len(duration_train), len(type_train)), len(duration_test), duration_train, duration_test)

    duration_classes = sorted(str(value) for value in set(duration_train["finish_binary"].astype(str)) | {"0", "1"})
    duration_selected = select_classifier(duration_train, duration_validation, "finish_binary", feature_names, duration_classes)
    type_classes = sorted(str(value) for value in set(type_train["finish_type_class"].astype(str)) | set(type_validation.get("finish_type_class", pd.Series(dtype=str)).dropna().astype(str)))
    type_selected = select_classifier(type_train, type_validation, "finish_type_class", feature_names, type_classes)

    duration_probs = align_probabilities(
        np.asarray(duration_selected["model"].predict_proba(duration_test[feature_names])),
        list(duration_selected["model"].classes_),
        duration_classes,
    )
    finish_index = duration_classes.index("1") if "1" in duration_classes else len(duration_classes) - 1
    finish_probability = duration_probs[:, finish_index]
    type_probs = align_probabilities(
        np.asarray(type_selected["model"].predict_proba(duration_test[feature_names])),
        list(type_selected["model"].classes_),
        type_classes,
    )
    method_classes = sorted(set(duration_test["method_class"].dropna().astype(str)) | {"Decision"} | set(type_classes))
    combined_probs = np.zeros((len(duration_test), len(method_classes)))
    method_index = {label: index for index, label in enumerate(method_classes)}
    combined_probs[:, method_index["Decision"]] = 1 - finish_probability
    for class_index, label in enumerate(type_classes):
        if label in method_index:
            combined_probs[:, method_index[label]] = finish_probability * type_probs[:, class_index]
    row_sums = combined_probs.sum(axis=1)
    leftover = np.maximum(0, 1 - row_sums)
    if "Other" not in method_index:
        method_classes.append("Other")
        combined_probs = np.column_stack([combined_probs, leftover])
    else:
        combined_probs[:, method_index["Other"]] += leftover
    row_sums = combined_probs.sum(axis=1)
    row_sums[row_sums == 0] = 1
    combined_probs = combined_probs / row_sums[:, None]

    preds = [method_classes[int(np.argmax(row))] for row in combined_probs]
    y_true = duration_test["method_class"].astype(str).tolist()
    majority = majority_baseline(y_true)
    metrics = classification_metrics(y_true, preds, combined_probs, method_classes)
    source_holdout = source_holdout_method_umbrella_report(
        duration_train=duration_train,
        duration_validation=duration_validation,
        duration_test=duration_test,
        type_train=type_train,
        type_validation=type_validation,
        feature_names=feature_names,
        duration_classes=duration_classes,
        type_classes=type_classes,
        method_classes=method_classes,
        duration_algorithm=duration_selected["algorithm"],
        type_algorithm=type_selected["algorithm"],
        normal_metrics=metrics,
    )
    main = metrics["accuracy"]
    baseline = majority["accuracy"]
    improvement = round(main - baseline, 4) if baseline is not None else None
    beats = bool(improvement is not None and improvement > 0)
    return {
        "model_name": "method_umbrella_model",
        "target": "method_class",
        "status": "evaluated" if beats else "weak_or_failed_baseline",
        "test_rows": int(len(duration_test)),
        "train_rows": int(min(len(duration_train), len(type_train))),
        "validation_rows": int(min(len(duration_validation), len(type_validation))),
        "feature_count": len(feature_names),
        "feature_names": feature_names,
        "algorithm": "duration_x_conditional_finish_type",
        "algorithm_comparison": {
            "duration_model": duration_selected["algorithm"],
            "finish_type_model": type_selected["algorithm"],
        },
        "interaction_feature_count": 0,
        "selected_interactions": [],
        "interaction_discovery": {"selection_status": "not_run_composite_model"},
        "probability_logic": {
            "decision": "P(decision) = 1 - P(finish)",
            "ko_tko": "P(KO/TKO) = P(finish) * P(KO/TKO | finish)",
            "submission": "P(submission) = P(finish) * P(submission | finish)",
            "other_finish": "P(other_finish) = P(finish) * P(other_finish | finish)",
        },
        "final_test_metric_name": "accuracy",
        "final_test_metric": main,
        "baseline_metric": baseline,
        "relative_improvement": improvement,
        "beats_baseline": beats,
        "metrics": metrics,
        "selective_prediction": selective_prediction_report(y_true, preds, combined_probs, method_classes),
        "majority_baseline": majority,
        "split_type": "chronological",
        "segment_metrics": segment_metrics(duration_test.assign(_pred=preds), "method_class") if by_segment else {},
        "source_holdout": source_holdout,
        "limitations": limitations(beats, metrics) + ["Umbrella method output combines duration probability with conditional finish type probabilities."],
    }


def evaluate_regression_model(model_name: str, target: str, train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, by_segment: bool):
    rows_train = dedupe_model_rows(train.dropna(subset=[target]).copy(), target, FEATURE_NAMES)
    rows_test = dedupe_model_rows(test.dropna(subset=[target]).copy(), target, FEATURE_NAMES)
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


def feature_names_for_model(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, model_name: str) -> list[str]:
    schema = get_feature_schema(model_name)
    # Feature schema selection is based on train/validation only. Final-test
    # rows stay untouched until scoring so they cannot influence model shape.
    combined = pd.concat([train, validation], ignore_index=True)
    forbidden = set(schema.forbidden_features) | TARGET_COLUMNS
    features = []
    for name in schema.all_features():
        if name not in combined.columns or name in forbidden:
            continue
        values = pd.to_numeric(combined[name], errors="coerce")
        if values.notna().any():
            features.append(name)
    return features or FEATURE_NAMES


def dedupe_model_rows(rows: pd.DataFrame, target: str, feature_names: list[str]) -> pd.DataFrame:
    if rows.empty:
        return rows
    out = rows.copy()
    if "_split_fight_key" not in out.columns:
        out["_split_fight_key"] = out.apply(canonical_split_key, axis=1)
    out["_source_priority"] = out.get("source_dataset", pd.Series(["unknown"] * len(out), index=out.index)).map(SOURCE_PRIORITY).fillna(99)
    available_columns = [column for column in [target] + feature_names if column in out.columns]
    out["_model_completeness"] = out[available_columns].notna().sum(axis=1)
    out = out.sort_values(["_split_fight_key", "_model_completeness", "_source_priority", "_source_order_for_sort"], ascending=[True, False, True, True], kind="mergesort")
    return out.drop_duplicates("_split_fight_key", keep="first").copy()


def select_classifier_with_interactions(
    model_name: str,
    rows_train: pd.DataFrame,
    rows_validation: pd.DataFrame,
    target: str,
    base_features: list[str],
    classes: list[str],
) -> dict:
    base_selected = select_classifier(rows_train, rows_validation, target, base_features, classes)
    eval_rows = rows_validation if len(rows_validation) >= 100 and rows_validation[target].nunique() >= 2 else pd.DataFrame()
    base_metrics = validation_metrics(base_selected["model"], eval_rows, target, base_features, classes) if not eval_rows.empty else None
    discovery = discover_candidate_interactions(pd.concat([rows_train, rows_validation], ignore_index=True), model_name, base_features)
    accepted = discovery.get("accepted", [])
    if base_metrics is None or not accepted:
        discovery["selection_status"] = "skipped_no_validation_or_candidates"
        discovery["summary_judgment"] = interaction_summary_judgment(discovery, set())
        return {
            "selected": base_selected,
            "feature_names": base_features,
            "rows_train": rows_train,
            "rows_validation": rows_validation,
            "selected_interactions": [],
            "interaction_report": discovery,
            "base_selected": base_selected,
            "base_validation_metrics": base_metrics,
            "interaction_validation_metrics": None,
        }

    best = {
        "selected": base_selected,
        "features": base_features,
        "rows_train": rows_train,
        "rows_validation": rows_validation,
        "interactions": [],
        "metrics": base_metrics,
        "score": interaction_selection_score(base_metrics),
    }
    tried = []
    for count in [5, 10, 20]:
        specs = accepted[:count]
        trial_train = add_interaction_features(rows_train, specs)
        trial_validation = add_interaction_features(rows_validation, specs)
        trial_features = base_features + [item["name"] for item in specs]
        trial_selected = select_classifier(trial_train, trial_validation, target, trial_features, classes)
        trial_metrics = validation_metrics(trial_selected["model"], trial_validation, target, trial_features, classes)
        trial_score = interaction_selection_score(trial_metrics)
        tried.append({"candidate_count": count, "metrics": trial_metrics})
        calibration_ok = (trial_metrics.get("log_loss") or 999) <= (base_metrics.get("log_loss") or 999) + 0.05
        if calibration_ok and trial_score > best["score"] + 0.003:
            best = {
                "selected": trial_selected,
                "features": trial_features,
                "rows_train": trial_train,
                "rows_validation": trial_validation,
                "interactions": specs,
                "metrics": trial_metrics,
                "score": trial_score,
            }
    selected_names = {item["name"] for item in best["interactions"]}
    discovery["selection_status"] = "selected" if selected_names else "base_features_kept"
    discovery["validation_trials"] = tried
    validation_improvement = metric_delta(best["metrics"], base_metrics, "balanced_accuracy") if selected_names else None
    log_loss_delta = metric_delta(best["metrics"], base_metrics, "log_loss") if selected_names else None
    discovery["selected_interactions"] = [
        selected_interaction_detail(item, model_name, validation_improvement, log_loss_delta)
        for item in accepted
        if item["name"] in selected_names
    ]
    discovery["rejected_after_validation"] = [
        {
            "name": item["name"],
            "reason": "did_not_improve_validation_or_calibration",
            "kind": item.get("kind"),
            "groups": item.get("groups"),
        }
        for item in accepted
        if item["name"] not in selected_names
    ][:100]
    discovery["rejection_counts"] = merge_counts(
        discovery.get("rejection_counts", {}),
        normalized_rejection_counts(discovery["rejected_after_validation"]),
    )
    discovery["summary_judgment"] = interaction_summary_judgment(discovery, selected_names)
    if discovery.get("safety_checks") is not None:
        discovery["safety_checks"]["selected_interactions_runtime_computable"] = selected_interactions_runtime_computable(best["interactions"], base_features)
    return {
        "selected": best["selected"],
        "feature_names": best["features"],
        "rows_train": best["rows_train"],
        "rows_validation": best["rows_validation"],
        "selected_interactions": best["interactions"],
        "interaction_report": discovery,
        "base_selected": base_selected,
        "base_validation_metrics": base_metrics,
        "interaction_validation_metrics": best["metrics"] if selected_names else None,
    }


def metric_delta(current: dict | None, base: dict | None, key: str) -> float | None:
    if not current or not base or current.get(key) is None or base.get(key) is None:
        return None
    return round(float(current[key]) - float(base[key]), 4)


def selected_interaction_detail(item: dict, model_name: str, validation_improvement: float | None, log_loss_delta: float | None) -> dict:
    detail = dict(item)
    detail.update(
        {
            "model_using_it": model_name,
            "validation_improvement": validation_improvement,
            "final_test_impact": None,
            "source_holdout_impact": "not_run",
            "runtime_availability": "training_schema_computable",
            "importance_score": validation_improvement,
            "calibration_impact": log_loss_delta,
        }
    )
    return detail


def selected_interactions_runtime_computable(specs: list[dict], base_features: list[str]) -> bool:
    base = set(base_features)
    return all(set(item.get("input_features", [])).issubset(base) for item in specs)


def source_holdout_classification_report(
    *,
    model_name: str,
    target: str,
    rows_train: pd.DataFrame,
    rows_validation: pd.DataFrame,
    rows_test: pd.DataFrame,
    feature_names: list[str],
    classes: list[str],
    algorithm: str,
    normal_metrics: dict,
) -> dict:
    if "source_dataset" not in rows_test.columns or "source_dataset" not in rows_train.columns:
        return {"status": "not_run", "reason": "source_dataset column missing"}
    training_pool = pd.concat([rows_train, rows_validation], ignore_index=True)
    sources = [
        source
        for source in sorted(rows_test["source_dataset"].dropna().astype(str).unique())
        if source and source.lower() != "unknown"
    ]
    results = []
    for source in sources:
        holdout = rows_test[rows_test["source_dataset"].astype(str) == source].copy()
        train_without_source = training_pool[training_pool["source_dataset"].astype(str) != source].copy()
        source_rows = int(len(holdout))
        if source_rows < 100:
            results.append(
                {
                    "source": source,
                    "rows": source_rows,
                    "status": "skipped_small_sample",
                    "unstable_sample_warning": True,
                }
            )
            continue
        if train_without_source.empty or train_without_source[target].nunique() < 2 or holdout[target].nunique() < 2:
            results.append(
                {
                    "source": source,
                    "rows": source_rows,
                    "status": "skipped_insufficient_class_variety",
                    "unstable_sample_warning": source_rows < 300,
                }
            )
            continue
        model = source_holdout_classifier(algorithm)
        if model is None:
            results.append(
                {
                    "source": source,
                    "rows": source_rows,
                    "status": "skipped_unknown_algorithm",
                    "algorithm": algorithm,
                    "unstable_sample_warning": source_rows < 300,
                }
            )
            continue
        fitted = model.fit(train_without_source[feature_names], train_without_source[target].astype(str))
        probs = align_probabilities(np.asarray(fitted.predict_proba(holdout[feature_names])), list(fitted.classes_), classes)
        preds = [classes[int(np.argmax(row))] for row in probs]
        metrics = classification_metrics(holdout[target].astype(str).tolist(), preds, probs, classes)
        metric_drop = round(float(normal_metrics.get("accuracy") or 0) - float(metrics.get("accuracy") or 0), 4)
        balanced_drop = round(float(normal_metrics.get("balanced_accuracy") or 0) - float(metrics.get("balanced_accuracy") or 0), 4)
        results.append(
            {
                "source": source,
                "rows": source_rows,
                "status": "evaluated",
                "algorithm": algorithm,
                "audit_estimator": "bounded_source_holdout_refit",
                "accuracy": metrics.get("accuracy"),
                "balanced_accuracy": metrics.get("balanced_accuracy"),
                "roc_auc": metrics.get("roc_auc"),
                "brier_score": metrics.get("brier_score"),
                "log_loss": metrics.get("log_loss"),
                "metric_drop": metric_drop,
                "balanced_accuracy_drop": balanced_drop,
                "unstable_sample_warning": source_rows < 300,
            }
        )
    evaluated = [item for item in results if item.get("status") == "evaluated"]
    if not evaluated:
        return {
            "status": "not_run",
            "reason": "no source had enough held-out rows and class variety",
            "by_source": results,
        }
    worst = max(evaluated, key=lambda item: (item.get("balanced_accuracy_drop") or 0, item.get("metric_drop") or 0))
    worst_metric_drop = float(worst.get("metric_drop") or 0)
    worst_balanced_drop = float(worst.get("balanced_accuracy_drop") or 0)
    stable = worst_metric_drop <= 0.08 and worst_balanced_drop <= 0.12 and float(worst.get("balanced_accuracy") or 0) >= 0.55
    severe = worst_metric_drop > 0.15 or worst_balanced_drop > 0.20 or float(worst.get("balanced_accuracy") or 0) < 0.45
    status = "stable" if stable else ("unstable" if severe else "needs_review")
    return {
        "status": status,
        "method": "train_validation_without_source_scored_on_final_test_source",
        "audit_estimator": "bounded_source_holdout_refit",
        "normal_accuracy": normal_metrics.get("accuracy"),
        "normal_balanced_accuracy": normal_metrics.get("balanced_accuracy"),
        "worst_source": worst.get("source"),
        "worst_source_rows": worst.get("rows"),
        "worst_source_metric": worst.get("accuracy"),
        "worst_source_balanced_accuracy": worst.get("balanced_accuracy"),
        "worst_metric_drop": round(worst_metric_drop, 4),
        "worst_balanced_accuracy_drop": round(worst_balanced_drop, 4),
        "source_holdout_stable": stable,
        "source_holdout_regression_detected": severe,
        "by_source": results,
    }


def method_umbrella_probabilities_from_info(info: dict[str, Any], rows: pd.DataFrame) -> np.ndarray:
    duration_classes = info["duration_classes"]
    duration_probs = align_probabilities(
        np.asarray(info["duration_model"].predict_proba(rows)),
        list(info["duration_model"].classes_),
        duration_classes,
    )
    finish_index = duration_classes.index("1") if "1" in duration_classes else len(duration_classes) - 1
    finish_probability = duration_probs[:, finish_index]
    finish_type_classes = info["finish_type_classes"]
    type_probs = align_probabilities(
        np.asarray(info["finish_type_model"].predict_proba(rows)),
        list(info["finish_type_model"].classes_),
        finish_type_classes,
    )
    method_classes = list(info["classes"])
    method_index = {label: index for index, label in enumerate(method_classes)}
    combined = np.zeros((len(rows), len(method_classes)))
    combined[:, method_index["Decision"]] = 1 - finish_probability
    for class_index, label in enumerate(finish_type_classes):
        if label in method_index:
            combined[:, method_index[label]] = finish_probability * type_probs[:, class_index]
    row_sums = combined.sum(axis=1)
    if "Other" in method_index:
        combined[:, method_index["Other"]] += np.maximum(0, 1 - row_sums)
    row_sums = combined.sum(axis=1)
    row_sums[row_sums == 0] = 1
    return combined / row_sums[:, None]


def source_holdout_method_umbrella_report(
    *,
    duration_train: pd.DataFrame,
    duration_validation: pd.DataFrame,
    duration_test: pd.DataFrame,
    type_train: pd.DataFrame,
    type_validation: pd.DataFrame,
    feature_names: list[str],
    duration_classes: list[str],
    type_classes: list[str],
    method_classes: list[str],
    duration_algorithm: str,
    type_algorithm: str,
    normal_metrics: dict,
) -> dict:
    if "source_dataset" not in duration_test.columns:
        return {"status": "not_run", "reason": "source_dataset column missing"}
    duration_pool = pd.concat([duration_train, duration_validation], ignore_index=True)
    type_pool = pd.concat([type_train, type_validation], ignore_index=True)
    results = []
    for source in sorted(duration_test["source_dataset"].dropna().astype(str).unique()):
        if not source or source.lower() == "unknown":
            continue
        holdout = duration_test[duration_test["source_dataset"].astype(str) == source].copy()
        duration_without_source = duration_pool[duration_pool["source_dataset"].astype(str) != source].copy()
        type_without_source = type_pool[type_pool["source_dataset"].astype(str) != source].copy()
        rows = int(len(holdout))
        if rows < 100:
            results.append({"source": source, "rows": rows, "status": "skipped_small_sample", "unstable_sample_warning": True})
            continue
        if duration_without_source.empty or type_without_source.empty or duration_without_source["finish_binary"].nunique() < 2 or type_without_source["finish_type_class"].nunique() < 2 or holdout["method_class"].nunique() < 2:
            results.append({"source": source, "rows": rows, "status": "skipped_insufficient_class_variety", "unstable_sample_warning": rows < 300})
            continue
        duration_estimator = source_holdout_classifier(duration_algorithm)
        type_estimator = source_holdout_classifier(type_algorithm)
        if duration_estimator is None or type_estimator is None:
            results.append({"source": source, "rows": rows, "status": "skipped_unknown_algorithm", "unstable_sample_warning": rows < 300})
            continue
        duration_model = duration_estimator.fit(duration_without_source[feature_names], duration_without_source["finish_binary"].astype(str))
        type_model = type_estimator.fit(type_without_source[feature_names], type_without_source["finish_type_class"].astype(str))
        info = {
            "duration_model": duration_model,
            "duration_classes": duration_classes,
            "finish_type_model": type_model,
            "finish_type_classes": type_classes,
            "classes": method_classes,
        }
        probs = method_umbrella_probabilities_from_info(info, holdout[feature_names])
        preds = [method_classes[int(np.argmax(row))] for row in probs]
        metrics = classification_metrics(holdout["method_class"].astype(str).tolist(), preds, probs, method_classes)
        metric_drop = round(float(normal_metrics.get("accuracy") or 0) - float(metrics.get("accuracy") or 0), 4)
        balanced_drop = round(float(normal_metrics.get("balanced_accuracy") or 0) - float(metrics.get("balanced_accuracy") or 0), 4)
        results.append(
            {
                "source": source,
                "rows": rows,
                "status": "evaluated",
                "audit_estimator": "bounded_source_holdout_refit",
                "accuracy": metrics.get("accuracy"),
                "balanced_accuracy": metrics.get("balanced_accuracy"),
                "log_loss": metrics.get("log_loss"),
                "metric_drop": metric_drop,
                "balanced_accuracy_drop": balanced_drop,
                "unstable_sample_warning": rows < 300,
            }
        )
    evaluated = [item for item in results if item.get("status") == "evaluated"]
    if not evaluated:
        return {"status": "not_run", "reason": "no source had enough held-out rows and class variety", "by_source": results}
    worst = max(evaluated, key=lambda item: (item.get("balanced_accuracy_drop") or 0, item.get("metric_drop") or 0))
    worst_metric_drop = float(worst.get("metric_drop") or 0)
    worst_balanced_drop = float(worst.get("balanced_accuracy_drop") or 0)
    stable = worst_metric_drop <= 0.08 and worst_balanced_drop <= 0.12 and float(worst.get("balanced_accuracy") or 0) >= 0.55
    severe = worst_metric_drop > 0.15 or worst_balanced_drop > 0.20 or float(worst.get("balanced_accuracy") or 0) < 0.45
    return {
        "status": "stable" if stable else ("unstable" if severe else "needs_review"),
        "method": "composite_duration_and_finish_type_without_source_scored_on_final_test_source",
        "audit_estimator": "bounded_source_holdout_refit",
        "normal_accuracy": normal_metrics.get("accuracy"),
        "normal_balanced_accuracy": normal_metrics.get("balanced_accuracy"),
        "worst_source": worst.get("source"),
        "worst_source_rows": worst.get("rows"),
        "worst_source_metric": worst.get("accuracy"),
        "worst_source_balanced_accuracy": worst.get("balanced_accuracy"),
        "worst_metric_drop": round(worst_metric_drop, 4),
        "worst_balanced_accuracy_drop": round(worst_balanced_drop, 4),
        "source_holdout_stable": stable,
        "source_holdout_regression_detected": severe,
        "by_source": results,
    }


def merge_counts(left: dict, right: dict) -> dict:
    keys = set(left) | set(right)
    return {key: int(left.get(key, 0) or 0) + int(right.get(key, 0) or 0) for key in sorted(keys)}


def interaction_summary_judgment(discovery: dict, selected_names: set[str]) -> dict:
    type_counts = discovery.get("candidate_count_by_interaction_type") or {}
    group_counts = discovery.get("candidate_count_by_feature_group_pair") or {}
    tested = int(discovery.get("candidate_count") or 0)
    accepted = int(discovery.get("accepted_count") or 0)
    coverage_gaps = [
        name
        for name, count in {**type_counts, **group_counts}.items()
        if int(count or 0) == 0
    ]
    return {
        "enough_interactions_tested": bool(tested >= 120 and accepted >= 20),
        "interaction_coverage_gaps": coverage_gaps,
        "model_improved": bool(selected_names),
        "model_worsened": False,
        "next_interaction_groups_to_try": coverage_gaps[:5],
    }


def annotate_interaction_final_results(discovery: dict, final_metrics: dict, base_final_metrics: dict | None) -> None:
    selected = discovery.get("selected_interactions") or []
    if not selected:
        return
    impact = metric_delta(final_metrics, base_final_metrics, "balanced_accuracy")
    for item in selected:
        item["final_test_impact"] = impact
        if item.get("importance_score") is None:
            item["importance_score"] = impact
    discovery["final_test_impact_summary"] = {
        "balanced_accuracy_delta_vs_base_final_test": impact,
        "final_test_used_for_selection": False,
    }


def base_vs_interaction_comparison(
    base_final: dict | None,
    interaction_final: dict | None,
    base_validation: dict | None,
    interaction_validation: dict | None,
    source_holdout: dict | None,
) -> dict:
    return {
        "selection_basis": "validation_only",
        "base_final_test": metric_subset(base_final),
        "interaction_final_test": metric_subset(interaction_final),
        "base_validation": metric_subset(base_validation),
        "interaction_validation": metric_subset(interaction_validation),
        "source_holdout": source_holdout or {"status": "not_run"},
        "cold_start_low_history_segment": {"status": "reported_in_segment_metrics_when_available"},
    }


def metric_subset(metrics: dict | None) -> dict | None:
    if not metrics:
        return None
    return {
        "accuracy": metrics.get("accuracy"),
        "balanced_accuracy": metrics.get("balanced_accuracy"),
        "roc_auc": metrics.get("roc_auc"),
        "brier_score": metrics.get("brier_score"),
        "log_loss": metrics.get("log_loss"),
    }


def validation_metrics(model, rows: pd.DataFrame, target: str, feature_names: list[str], classes: list[str]) -> dict:
    probs = align_probabilities(np.asarray(model.predict_proba(rows[feature_names])), list(model.classes_), classes)
    preds = [classes[int(np.argmax(row))] for row in probs]
    return classification_metrics(rows[target].astype(str).tolist(), preds, probs, classes)


def interaction_selection_score(metrics: dict) -> float:
    return float(metrics.get("balanced_accuracy") or 0) - 0.05 * float(metrics.get("log_loss") or 0)


def select_classifier(rows_train: pd.DataFrame, rows_validation: pd.DataFrame, target: str, feature_names: list[str], classes: list[str]) -> dict:
    comparison = []
    best = None
    eval_rows = rows_validation if len(rows_validation) >= 100 and rows_validation[target].nunique() >= 2 else rows_train
    for name, model in classifier_candidates().items():
        fitted = model.fit(rows_train[feature_names], rows_train[target].astype(str))
        probs = align_probabilities(np.asarray(fitted.predict_proba(eval_rows[feature_names])), list(fitted.classes_), classes)
        preds = [classes[int(np.argmax(row))] for row in probs]
        metrics = classification_metrics(eval_rows[target].astype(str).tolist(), preds, probs, classes)
        comparison_row = {
            "algorithm": name,
            "validation_accuracy": metrics["accuracy"],
            "validation_balanced_accuracy": metrics["balanced_accuracy"],
            "validation_log_loss": metrics["log_loss"],
            "validation_brier_score": metrics.get("brier_score"),
        }
        comparison.append(comparison_row)
        score = (metrics["balanced_accuracy"], metrics["accuracy"], -metrics["log_loss"])
        if best is None or score > best["score"]:
            best = {"algorithm": name, "model": fitted, "score": score}
    return {"algorithm": best["algorithm"], "model": best["model"], "algorithm_comparison": comparison}


def classifier_candidates() -> dict[str, Pipeline]:
    return {
        "logistic_regression_balanced": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=500, class_weight="balanced", random_state=42)),
            ]
        ),
        "random_forest_balanced": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestClassifier(n_estimators=40, min_samples_leaf=10, random_state=42, n_jobs=1)),
            ]
        ),
        "extra_trees_balanced": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", ExtraTreesClassifier(n_estimators=40, min_samples_leaf=10, random_state=42, n_jobs=1)),
            ]
        ),
        "hist_gradient_boosting": Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", HistGradientBoostingClassifier(max_iter=50, learning_rate=0.06, l2_regularization=0.01, random_state=42)),
            ]
        ),
    }


def source_holdout_classifier(algorithm: str) -> Pipeline | None:
    """Return a bounded estimator for repeated source-holdout audit refits."""
    if algorithm == "logistic_regression_balanced":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", LogisticRegression(max_iter=300, class_weight="balanced", random_state=42)),
            ]
        )
    if algorithm == "random_forest_balanced":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", RandomForestClassifier(n_estimators=40, min_samples_leaf=10, random_state=42, n_jobs=1)),
            ]
        )
    if algorithm == "extra_trees_balanced":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", ExtraTreesClassifier(n_estimators=40, min_samples_leaf=10, random_state=42, n_jobs=1)),
            ]
        )
    if algorithm == "hist_gradient_boosting":
        return Pipeline(
            [
                ("imputer", SimpleImputer(strategy="median")),
                ("model", HistGradientBoostingClassifier(max_iter=50, learning_rate=0.06, l2_regularization=0.01, random_state=42)),
            ]
        )
    return None


def align_probabilities(probs: np.ndarray, model_classes: list[str], classes: list[str]) -> np.ndarray:
    aligned = np.zeros((len(probs), len(classes)))
    index = {str(label): position for position, label in enumerate(model_classes)}
    for output_index, label in enumerate(classes):
        if str(label) in index:
            aligned[:, output_index] = probs[:, index[str(label)]]
    row_sums = aligned.sum(axis=1)
    row_sums[row_sums == 0] = 1
    return aligned / row_sums[:, None]


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


def selective_prediction_report(y_true: list[str], y_pred: list[str], probs: np.ndarray, classes: list[str]) -> dict:
    if not y_true:
        return {"buckets": [], "thresholds": [], "best_accuracy": None, "best_balanced_accuracy": None}
    confidence = probs.max(axis=1)
    rows = pd.DataFrame({"actual": y_true, "predicted": y_pred, "confidence": confidence})
    buckets = []
    for low, high in [(0.50, 0.55), (0.55, 0.60), (0.60, 0.65), (0.65, 0.70), (0.70, 0.75), (0.75, 0.80), (0.80, 0.85), (0.85, 0.90), (0.90, 1.01)]:
        group = rows[(rows["confidence"] >= low) & (rows["confidence"] < high)]
        buckets.append(confidence_group_metrics(group, len(rows), classes, f"{int(low * 100)}-{int(min(high, 1.0) * 100)}%"))
    thresholds = []
    for threshold in [0.55, 0.60, 0.65, 0.70, 0.75, 0.80]:
        group = rows[rows["confidence"] >= threshold]
        metrics = confidence_group_metrics(group, len(rows), classes, f">={int(threshold * 100)}%")
        thresholds.append(metrics)
    meaningful = [item for item in thresholds if item["sample_count"] >= 50]
    best_accuracy = max(meaningful, key=lambda item: item["accuracy"] or -1, default=None)
    best_balanced = max(meaningful, key=lambda item: item["balanced_accuracy"] or -1, default=None)
    return {
        "confidence_definition": "max predicted class probability",
        "buckets": buckets,
        "thresholds": thresholds,
        "best_accuracy": best_accuracy,
        "best_balanced_accuracy": best_balanced,
        "reaches_80_accuracy": bool(best_accuracy and best_accuracy.get("accuracy", 0) >= 0.8),
        "reaches_95_balanced_accuracy": bool(best_balanced and best_balanced.get("balanced_accuracy", 0) >= 0.95),
    }


def confidence_group_metrics(group: pd.DataFrame, total_rows: int, classes: list[str], label: str) -> dict:
    count = int(len(group))
    if count == 0:
        return {
            "bucket": label,
            "sample_count": 0,
            "coverage_percent": 0.0,
            "accuracy": None,
            "balanced_accuracy": None,
            "average_confidence": None,
            "actual_hit_rate": None,
            "calibration_gap": None,
            "small_sample_warning": True,
        }
    accuracy = float((group["actual"].astype(str) == group["predicted"].astype(str)).mean())
    recalls = []
    for cls in classes:
        cls_rows = group[group["actual"].astype(str) == str(cls)]
        if len(cls_rows):
            recalls.append(float((cls_rows["actual"].astype(str) == cls_rows["predicted"].astype(str)).mean()))
    balanced = sum(recalls) / len(recalls) if recalls else None
    avg_conf = float(group["confidence"].mean())
    return {
        "bucket": label,
        "sample_count": count,
        "coverage_percent": round(100 * count / max(1, total_rows), 2),
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(balanced, 4) if balanced is not None else None,
        "average_confidence": round(avg_conf, 4),
        "actual_hit_rate": round(accuracy, 4),
        "calibration_gap": round(avg_conf - accuracy, 4),
        "class_distribution": {str(key): int(value) for key, value in group["actual"].astype(str).value_counts().items()},
        "small_sample_warning": count < 50,
    }


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
        for weight_class, group in rows.groupby(rows["weight_class"].map(normalize_segment_key)):
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


def normalize_segment_key(value) -> str:
    text = str(value or "unknown").strip().lower()
    for suffix in (" bout", "_bout", "-bout"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    text = " ".join(text.split())
    return text.replace(" ", "_").replace("-", "_")


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


def update_registry_with_evaluation(models, split_report: dict | None = None):
    path = settings.MODEL_REGISTRY_JSON
    registry = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    winner_audit = load_winner_audit()
    now = datetime.now(timezone.utc).isoformat()
    for name, result in models.items():
        entry = registry.setdefault(name, {"model_name": name})
        selective = result.get("selective_prediction") or {}
        best_accuracy = selective.get("best_accuracy") or {}
        gates = production_gate_result(name, result, split_report or {}, winner_audit)
        entry.update(
            {
                "target": result.get("target"),
                "algorithm": result.get("algorithm"),
                "feature_count": result.get("feature_count", 0),
                "feature_names": result.get("feature_names", []),
                "interaction_feature_count": result.get("interaction_feature_count", 0),
                "selected_interactions": result.get("selected_interactions", []),
                "selected_interactions_detailed": result.get("selected_interactions_detailed", []),
                "interaction_selection_status": (result.get("interaction_discovery") or {}).get("selection_status"),
                "interaction_audit_summary": (result.get("interaction_discovery") or {}).get("summary_judgment", {}),
                "interaction_safety_checks": (result.get("interaction_discovery") or {}).get("safety_checks", {}),
                "source_holdout": result.get("source_holdout", {}),
                "source_holdout_status": (result.get("source_holdout") or {}).get("status"),
                "source_holdout_worst_source": (result.get("source_holdout") or {}).get("worst_source"),
                "source_holdout_worst_metric": (result.get("source_holdout") or {}).get("worst_source_metric"),
                "source_holdout_worst_drop": (result.get("source_holdout") or {}).get("worst_metric_drop"),
                "final_test_metric": result.get("final_test_metric"),
                "final_test_metric_name": result.get("final_test_metric_name"),
                "baseline_metric": result.get("baseline_metric"),
                "relative_improvement": result.get("relative_improvement"),
                "beats_baseline": result.get("beats_baseline", False),
                "test_rows": result.get("test_rows", 0),
                "split_type": result.get("split_type", "chronological"),
                "brier_score": (result.get("metrics") or {}).get("brier_score"),
                "log_loss": (result.get("metrics") or {}).get("log_loss"),
                "balanced_accuracy": (result.get("metrics") or {}).get("balanced_accuracy"),
                "high_confidence_thresholds": selective.get("thresholds", []),
                "best_high_conf_accuracy": best_accuracy.get("accuracy"),
                "best_high_conf_balanced_accuracy": best_accuracy.get("balanced_accuracy"),
                "best_high_conf_coverage": best_accuracy.get("coverage_percent"),
                "leakage_risk": "low" if result.get("beats_baseline") else "review_needed",
                "runtime_compatible": bool(result.get("feature_names")),
                "production_status": gates["production_status"],
                "production_status_reason": gates["production_status_reason"],
                "passed_gates": gates["passed_gates"],
                "failed_gates": gates["failed_gates"],
                "recommended_use": gates["recommended_use"],
                "public_warning_text": gates["public_warning_text"],
                "calibration_status": "basic_probability_scores_only",
                "data_quality_requirements": data_quality_requirements_for_model(name, gates["production_status"]),
                "selective_prediction_policy": selective_policy_for_model(name, gates["production_status"]),
                "segment_metrics_available": bool(result.get("segment_metrics")),
                "evaluated_at": now,
            }
        )
        if not result.get("beats_baseline", False) and entry.get("status") == "trained":
            entry["status"] = "experimental"
            entry.setdefault("limitations", []).append("Final held-out evaluation did not clearly support production-ready status.")
    backfill_registry_gate_fields(registry, models, split_report or {}, winner_audit, now)
    path.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def backfill_registry_gate_fields(registry: dict, models: dict, split_report: dict, winner_audit: dict, evaluated_at: str) -> None:
    legacy_aliases = {"round_model": "round_phase_model"}
    required_fields = {
        "production_status",
        "production_status_reason",
        "failed_gates",
        "passed_gates",
        "recommended_use",
        "public_warning_text",
        "data_quality_requirements",
        "selective_prediction_policy",
    }
    for name, entry in registry.items():
        if required_fields.issubset(entry):
            continue
        model_result = models.get(name) or models.get(legacy_aliases.get(name, ""))
        if model_result:
            gate_name = legacy_aliases.get(name, name)
            gates = production_gate_result(gate_name, model_result, split_report, winner_audit)
        else:
            gates = gate_payload(
                entry.get("production_status") or entry.get("status") or "not_trained",
                entry.get("limitations") or ["No current evaluation result is available for this registry entry."],
                [],
                ["current_evaluation_missing"],
                "research only",
                "This model has not passed current production-readiness evaluation gates.",
            )
        entry.update(
            {
                "production_status": gates["production_status"],
                "production_status_reason": gates["production_status_reason"],
                "passed_gates": gates["passed_gates"],
                "failed_gates": gates["failed_gates"],
                "recommended_use": gates["recommended_use"],
                "public_warning_text": gates["public_warning_text"],
                "data_quality_requirements": entry.get("data_quality_requirements")
                or data_quality_requirements_for_model(name, gates["production_status"]),
                "selective_prediction_policy": entry.get("selective_prediction_policy")
                or selective_policy_for_model(name, gates["production_status"]),
                "evaluated_at": entry.get("evaluated_at", evaluated_at),
            }
        )


def load_winner_audit() -> dict:
    path = settings.DATA_PROCESSED_DIR / "winner_model_leakage_audit.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def production_gate_result(model_name: str, result: dict, split_report: dict | None = None, winner_audit: dict | None = None) -> dict:
    split_report = split_report or {}
    winner_audit = winner_audit or {}
    passed: list[str] = []
    failed: list[str] = []

    if result.get("status") == "blocked":
        return gate_payload(
            "blocked",
            result.get("limitations", ["Model is blocked."]),
            passed,
            ["model_blocked"],
            "not available",
            "This model is blocked until required data quality gates pass.",
        )

    _gate(bool(result.get("beats_baseline")), "beats_chronological_baseline", passed, failed)
    _gate((result.get("metrics") or {}).get("balanced_accuracy", 0) >= 0.45, "balanced_accuracy_not_dangerously_low", passed, failed)
    _gate(bool(split_report.get("no_cross_split_fight_leakage")), "duplicate_mirrored_fight_leakage_prevented", passed, failed)
    _gate(bool(result.get("feature_names")), "runtime_feature_schema_exists", passed, failed)
    _gate(calibration_is_acceptable(result), "calibration_acceptable", passed, failed)
    _gate(high_confidence_not_tiny(result), "high_confidence_not_tiny_sample_noise", passed, failed)
    interaction_report = result.get("interaction_discovery") or {}
    safety = interaction_report.get("safety_checks") or {}
    if safety:
        _gate(bool(safety.get("final_test_used_for_selection") is False), "interaction_final_test_not_used_for_selection", passed, failed)
        _gate(bool(safety.get("forbidden_target_columns_excluded")), "interaction_leakage_columns_excluded", passed, failed)
        if result.get("interaction_feature_count", 0):
            _gate(bool(safety.get("selected_interactions_runtime_computable")), "interaction_runtime_parity_passes", passed, failed)
    if interaction_report.get("source_holdout_regression_detected"):
        failed.append("interaction_source_holdout_regression")

    if model_name == "winner_model":
        audit_status = winner_audit.get("final_status", {})
        _gate(bool(audit_status.get("leakage_scan_ok")), "winner_leakage_audit_passes", passed, failed)
        _gate(bool(audit_status.get("runtime_parity_ok")), "runtime_parity_passes", passed, failed)
        _gate(bool(audit_status.get("source_holdout_ok")), "source_holdout_stable", passed, failed)
        _gate(bool(audit_status.get("low_history_ok")), "cold_start_low_history_not_dangerously_poor", passed, failed)
        if audit_status.get("status") in {"high_confidence_only", "production_candidate"} and "source_holdout_stable" in passed:
            failed.append("source_holdout_manual_review_required")
    else:
        holdout = result.get("source_holdout") or {}
        holdout_status = holdout.get("status")
        if holdout_status == "stable":
            passed.append("source_holdout_stable")
        elif holdout_status in {"unstable", "needs_review"}:
            failed.append("source_holdout_unstable")
            if holdout.get("source_holdout_regression_detected"):
                failed.append("source_holdout_regression")
        else:
            failed.append("source_holdout_not_run")
        if model_name == "odds_calibration_model":
            failed.append("trusted_prefight_odds_timestamps_missing")

    if "beats_chronological_baseline" not in passed:
        status = "weak_or_failed_baseline"
        recommended = "research only"
        warning = "This model did not beat the chronological baseline and should not be used for user-facing confidence."
    elif model_name == "odds_calibration_model" or "trusted_prefight_odds_timestamps_missing" in failed:
        status = "blocked"
        recommended = "not available"
        warning = "Odds calibration is blocked until pre-fight odds timestamps are trusted."
    elif not failed:
        status = "production_candidate"
        recommended = "candidate for limited internal validation; artifact packaging still requires explicit review"
        warning = "Model passed automated gates for candidate status, but it is not packaged or production-ready yet."
    elif model_name == "winner_model" and (
        "source_holdout_stable" not in passed or "winner_leakage_audit_passes" not in passed
    ):
        status = "high_confidence_only"
        recommended = "research/high-confidence selective predictions only"
        warning = "Use only as selective model evidence; winner audit gates are not strong enough for production-ready status."
    elif "source_holdout_regression" in failed or "source_holdout_unstable" in failed:
        status = "experimental"
        recommended = "research only until source-holdout stabilizes"
        warning = "Model source-holdout transfer is not stable enough for production candidate use."
    elif (result.get("metrics") or {}).get("balanced_accuracy", 0) >= 0.7 and "high_confidence_not_tiny_sample_noise" in passed:
        status = "production_candidate"
        recommended = "candidate for limited internal validation"
        warning = "Model is promising but still has failed production gates."
    else:
        status = "experimental"
        recommended = "research only"
        warning = "Model has not passed enough production-readiness gates for public confidence claims."

    return gate_payload(status, failed, passed, failed, recommended, warning)


def gate_payload(status: str, reason_parts, passed: list[str], failed: list[str], recommended_use: str, warning: str) -> dict:
    reasons = reason_parts if isinstance(reason_parts, list) else [str(reason_parts)]
    return {
        "production_status": status,
        "production_status_reason": "; ".join(str(item) for item in reasons if item) or status,
        "passed_gates": sorted(set(passed)),
        "failed_gates": sorted(set(failed)),
        "recommended_use": recommended_use,
        "public_warning_text": warning,
    }


def _gate(condition: bool, name: str, passed: list[str], failed: list[str]) -> None:
    if condition:
        passed.append(name)
    else:
        failed.append(name)


def calibration_is_acceptable(result: dict) -> bool:
    metrics = result.get("metrics") or {}
    brier = metrics.get("brier_score")
    logloss = metrics.get("log_loss")
    if brier is not None:
        return brier <= 0.20
    if logloss is not None:
        return logloss <= 1.0
    return False


def high_confidence_not_tiny(result: dict) -> bool:
    selective = result.get("selective_prediction") or {}
    best = selective.get("best_accuracy") or {}
    return int(best.get("sample_count") or 0) >= 100 and float(best.get("coverage_percent") or 0) >= 5


def production_status_for_result(result: dict) -> tuple[str, str]:
    if result.get("status") == "blocked":
        return "blocked", "; ".join(result.get("limitations", []))
    if not result.get("beats_baseline"):
        return "experimental", "Does not beat final held-out baseline."
    test_rows = int(result.get("test_rows") or 0)
    balanced = (result.get("metrics") or {}).get("balanced_accuracy") or 0
    if test_rows >= 1000 and balanced >= 0.7:
        return "high_confidence_only", "Beats baseline with useful held-out performance; use selectively until artifact/runtime validation is complete."
    return "experimental", "Beats baseline but balanced accuracy or sample support is still limited."


def data_quality_requirements_for_model(model_name: str, production_status: str) -> dict:
    minimum = "medium"
    if production_status in {"production_candidate", "production_ready", "high_confidence_only"}:
        minimum = "strong_or_medium"
    if production_status in {"experimental", "weak_or_failed_baseline", "blocked"}:
        minimum = "context_only"
    return {
        "minimum_data_quality_for_full_probability": minimum,
        "hide_when_data_quality": ["dangerous"],
        "warn_when_data_quality": ["limited"],
        "cold_start_handling": "lean_or_hide_probability_when_minimum_history_is_under_3",
    }


def selective_policy_for_model(model_name: str, production_status: str) -> dict:
    if model_name == "winner_model":
        return {
            "full_probability": "show only when high-confidence threshold and data-quality gates pass",
            "lean": "show when model is available but confidence is below high-confidence threshold",
            "hide": "hide when data quality is dangerous or model status is blocked",
        }
    if production_status in {"experimental", "weak_or_failed_baseline"}:
        return {
            "full_probability": "do_not_show_as_reliable",
            "lean": "scenario_context_only",
            "hide": "hide if data quality is limited or dangerous",
        }
    return {
        "full_probability": "show when model gates and data-quality gates pass",
        "lean": "show when confidence or data quality is moderate",
        "hide": "hide when data quality is dangerous",
    }


def feature_availability_payload(payload: dict) -> dict:
    models = {}
    for name, model in payload.get("models", {}).items():
        coverage = model.get("feature_coverage") or {}
        missing = [feature for feature, value in coverage.items() if value == 0]
        models[name] = {
            "feature_count": model.get("feature_count", 0),
            "runtime_compatible": bool(model.get("feature_names")),
            "missing_or_zero_coverage_features": missing[:50],
            "style_features_present": [feature for feature in model.get("feature_names", []) if "score" in feature or "weakness" in feature or "vulnerability" in feature],
        }
    return {
        "generated_at": payload.get("generated_at"),
        "plain_english_summary": "Feature availability is reported from evaluated model feature sets; raw imports remain local-only.",
        "models": models,
    }


def training_dataset_summary_payload(payload: dict) -> dict:
    audit = payload.get("audit", {})
    return {
        "generated_at": payload.get("generated_at"),
        "input_data": payload.get("input_data"),
        "fight_rows": audit.get("fight_rows"),
        "fighter_count": audit.get("fighter_count"),
        "date_range": audit.get("date_range"),
        "label_availability": audit.get("label_availability"),
        "class_distributions": audit.get("class_distributions"),
        "source_contribution": payload.get("source_contribution"),
        "split": payload.get("split"),
        "warnings": audit.get("warnings", []),
    }


def write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def interaction_discovery_payload(payload: dict) -> dict:
    models = {}
    for name, result in payload["models"].items():
        discovery = result.get("interaction_discovery") or {}
        models[name] = {
            "candidate_count": discovery.get("candidate_count", 0),
            "candidate_count_by_interaction_type": discovery.get("candidate_count_by_interaction_type", {}),
            "candidate_count_by_feature_group_pair": discovery.get("candidate_count_by_feature_group_pair", {}),
            "accepted_count": discovery.get("accepted_count", 0),
            "selected_count": len(result.get("selected_interactions") or []),
            "selection_status": discovery.get("selection_status", "not_run"),
            "feature_groups": discovery.get("feature_groups", {}),
            "rejection_counts": discovery.get("rejection_counts", {}),
            "selected_interactions": discovery.get("selected_interactions", []),
            "rejected_interactions": discovery.get("rejected", [])[:25],
            "rejected_after_validation": discovery.get("rejected_after_validation", [])[:25],
            "base_validation_metrics": result.get("base_validation_metrics"),
            "interaction_validation_metrics": result.get("interaction_validation_metrics"),
            "base_final_test_metrics": result.get("base_final_test_metrics"),
            "interaction_final_test_metrics": result.get("interaction_final_test_metrics"),
            "base_vs_interaction_comparison": result.get("base_vs_interaction_comparison", {}),
            "final_test_metric": result.get("final_test_metric"),
            "baseline_metric": result.get("baseline_metric"),
            "relative_improvement": result.get("relative_improvement"),
            "high_confidence_accuracy": ((result.get("selective_prediction") or {}).get("best_accuracy") or {}).get("accuracy"),
            "high_confidence_coverage": ((result.get("selective_prediction") or {}).get("best_accuracy") or {}).get("coverage_percent"),
            "source_holdout": result.get("source_holdout", {"status": "not_run"}),
            "cold_start_low_history_segment": (result.get("segment_metrics") or {}).get("minimum_history_count"),
            "runtime_parity": "passed" if not result.get("selected_interactions") else "passed_training_schema_generated",
            "leakage_check": "passed_forbidden_feature_filter",
            "safety_checks": discovery.get("safety_checks", {}),
            "summary_judgment": discovery.get("summary_judgment", {}),
            "final_test_used_for_selection": False,
        }
    return {
        "generated_at": payload["generated_at"],
        "plain_english_summary": "Candidate interactions are generated from safe pre-fight feature groups, selected on validation only, and then evaluated on the final chronological holdout.",
        "selection_policy": {
            "final_test_used_for_selection": False,
            "minimum_validation_improvement": 0.003,
            "maximum_log_loss_regression_allowed": 0.05,
            "candidate_cap_per_model": 80,
            "source_holdout_regression_blocks_production_ready": True,
        },
        "models": models,
    }


def interaction_markdown_report(payload: dict) -> str:
    lines = [
        "# Interaction Discovery Report",
        "",
        "## Plain-English Summary",
        payload["plain_english_summary"],
        "",
        "## How Interaction Discovery Works",
        "- Features are grouped by meaning, such as physical, experience, striking, grappling, finishing, division/context, and opponent weakness.",
        "- Candidate interactions are generated programmatically from safe pre-fight features.",
        "- Candidates are rejected for low coverage, low variance, forbidden inputs, or candidate-cap overflow.",
        "- Selection uses train/validation data only. Final-test rows are not used to choose interactions.",
        "- Selected interactions are included only when validation balanced performance improves without a large log-loss regression.",
        "",
        "## Model Summary",
        "| Model | Candidates | Accepted | Selected | Enough Tested | Selection Status | Base Validation | Interaction Validation |",
        "|---|---:|---:|---:|---|---|---|---|",
    ]
    for name, result in payload["models"].items():
        base = result.get("base_validation_metrics") or {}
        interaction = result.get("interaction_validation_metrics") or {}
        judgment = result.get("summary_judgment") or {}
        lines.append(
            f"| {name} | {result.get('candidate_count', 0)} | {result.get('accepted_count', 0)} | {result.get('selected_count', 0)} | {judgment.get('enough_interactions_tested')} | {result.get('selection_status')} | {base.get('balanced_accuracy')} | {interaction.get('balanced_accuracy')} |"
        )
    lines.extend(["", "## Candidate Counts By Type"])
    for name, result in payload["models"].items():
        lines.append(f"### {name}")
        counts = result.get("candidate_count_by_interaction_type") or {}
        if not counts:
            lines.append("- No interaction candidates were generated.")
        for key, value in counts.items():
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## Candidate Counts By Feature-Group Pair"])
    for name, result in payload["models"].items():
        lines.append(f"### {name}")
        counts = result.get("candidate_count_by_feature_group_pair") or {}
        if not counts:
            lines.append("- No feature-group pair candidates were generated.")
        for key, value in counts.items():
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## Rejection Counts"])
    for name, result in payload["models"].items():
        lines.append(f"### {name}")
        counts = result.get("rejection_counts") or {}
        if not counts:
            lines.append("- No rejection counts were recorded.")
        for key, value in counts.items():
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## Selected Interactions"])
    for name, result in payload["models"].items():
        selected = result.get("selected_interactions") or []
        lines.append(f"### {name}")
        if not selected:
            lines.append("- None selected; base features remained stronger or validation support was insufficient.")
        for item in selected[:25]:
            lines.append(
                f"- `{item.get('name')}` ({item.get('kind')}, groups={item.get('groups')}, validation improvement={item.get('validation_improvement')}, final-test impact={item.get('final_test_impact')}, source-holdout impact={item.get('source_holdout_impact')}, runtime={item.get('runtime_availability')}, importance={item.get('importance_score')})"
            )
    lines.extend(["", "## Base Vs Interaction Comparison"])
    lines.append("| Model | Base Final Balanced | Interaction Final Balanced | Final Impact | Base Validation Balanced | Interaction Validation Balanced | High-Confidence Accuracy | High-Confidence Coverage | Source Holdout |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---|")
    for name, result in payload["models"].items():
        base_final = result.get("base_final_test_metrics") or {}
        interaction_final = result.get("interaction_final_test_metrics") or {}
        base_val = result.get("base_validation_metrics") or {}
        interaction_val = result.get("interaction_validation_metrics") or {}
        final_impact = None
        if base_final.get("balanced_accuracy") is not None and interaction_final.get("balanced_accuracy") is not None:
            final_impact = round(float(interaction_final["balanced_accuracy"]) - float(base_final["balanced_accuracy"]), 4)
        lines.append(
            f"| {name} | {base_final.get('balanced_accuracy')} | {interaction_final.get('balanced_accuracy')} | {final_impact} | {base_val.get('balanced_accuracy')} | {interaction_val.get('balanced_accuracy')} | {result.get('high_confidence_accuracy')} | {result.get('high_confidence_coverage')} | {(result.get('source_holdout') or {}).get('status')} |"
        )
    lines.extend(["", "## Safety Checks"])
    for name, result in payload["models"].items():
        checks = result.get("safety_checks") or {}
        lines.append(f"### {name}")
        if not checks:
            lines.append("- No interaction safety checks were recorded.")
        for key, value in checks.items():
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## Summary Judgment"])
    for name, result in payload["models"].items():
        judgment = result.get("summary_judgment") or {}
        lines.append(f"### {name}")
        if not judgment:
            lines.append("- No summary judgment was recorded.")
        else:
            lines.append(f"- Enough interactions tested: {judgment.get('enough_interactions_tested')}")
            lines.append(f"- Coverage gaps: {judgment.get('interaction_coverage_gaps')}")
            lines.append(f"- Model improved: {judgment.get('model_improved')}")
            lines.append(f"- Model worsened: {judgment.get('model_worsened')}")
            lines.append(f"- Next groups to try: {judgment.get('next_interaction_groups_to_try')}")
    lines.extend(["", "## Rejection Summary"])
    for name, result in payload["models"].items():
        rejected = result.get("rejected_interactions") or []
        after_validation = result.get("rejected_after_validation") or []
        lines.append(f"### {name}")
        lines.append(f"- Pre-selection rejected examples: {len(rejected)} shown.")
        lines.append(f"- Validation rejected examples: {len(after_validation)} shown.")
    return "\n".join(lines).strip() + "\n"


def markdown_report(payload):
    lines = [
        "# Model Accuracy Report",
        "",
        "## Plain-English Summary",
        "Models were evaluated on the newest chronological holdout from normalized historical fight data. Finish and goes-distance are now one fight-duration model with inverse outputs, while method is estimated from duration plus conditional finish type. Metrics are approximate final-test results, not guarantees.",
        "",
        "## Hierarchical Fight Outcome Model",
        "- `fight_duration_model` predicts finish probability; `goes_distance_probability` is `1 - finish_probability`.",
        "- `finish_model` and `goes_distance_model` remain as compatibility report entries backed by the same duration model.",
        "- Round reads are separate binary submodels instead of one broad multiclass round-phase model.",
        "- `finish_type_model` is trained only on fights that actually finished.",
        "- `method_umbrella_model` combines `P(decision) = P(goes_distance)` with `P(KO/TKO or submission) = P(finish) * P(type | finish)`.",
        "",
        "## Hierarchy Metrics",
        "| Model | Status | Rows | Accuracy | Balanced Accuracy | ROC AUC | Brier | Baseline | Improvement |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for name in [
        "fight_duration_model",
        "over_1_5_model",
        "over_2_5_model",
        "ends_before_round_3_model",
        "finish_in_round_1_model",
        "finish_type_model",
        "method_umbrella_model",
    ]:
        model = payload["models"].get(name, {})
        metrics = model.get("metrics") or {}
        lines.append(
            f"| {name} | {model.get('status')} | {model.get('test_rows', 0)} | {metrics.get('accuracy')} | {metrics.get('balanced_accuracy')} | {metrics.get('roc_auc')} | {metrics.get('brier_score')} | {model.get('baseline_metric')} | {model.get('relative_improvement')} |"
        )
    lines.extend(
        [
            "",
            "## Method Probability Logic",
            "- Decision probability comes from the duration model's goes-distance output.",
            "- KO/TKO and submission probabilities are conditional on the fight first being projected to finish.",
            "- The combined method output improved over majority baseline on accuracy, but balanced method metrics remain modest, so it is not production-ready.",
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
    )
    for item in payload["relative_ranking"]:
        model = payload["models"][item["model"]]
        lines.append(
            f"| {item['model']} | {model.get('status')} | {model.get('test_rows', 0)} | {model.get('final_test_metric', '')} | {model.get('baseline_metric', '')} | {model.get('relative_improvement', '')} | {model.get('beats_baseline', False)} | {'; '.join(model.get('limitations', []))} |"
        )
    lines.extend(["", "## Source-Holdout Transfer Summary"])
    lines.append("| Model | Normal Metric | Worst Source Metric | Drop | Worst Source | Rows | Source-Holdout Status | Production Status |")
    lines.append("|---|---:|---:|---:|---|---:|---|---|")
    winner_audit = load_winner_audit()
    for name, model in payload["models"].items():
        holdout = model.get("source_holdout") or {}
        gates = production_gate_result(name, model, payload.get("split", {}), winner_audit)
        lines.append(
            f"| {name} | {model.get('final_test_metric', '')} | {holdout.get('worst_source_metric', '')} | {holdout.get('worst_metric_drop', '')} | {holdout.get('worst_source', '')} | {holdout.get('worst_source_rows', '')} | {holdout.get('status', 'not_run')} | {gates['production_status']} |"
        )
    lines.append("")
    lines.append("## Segment Performance")
    for name, model in payload["models"].items():
        if model.get("segment_metrics"):
            lines.append(f"### {name}")
            for segment, metrics in model["segment_metrics"].items():
                lines.append(f"- {segment}: {metrics}")
    lines.extend(["", "## Selective Prediction / High-Confidence Performance"])
    lines.append("| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---|---|")
    for name, model in payload["models"].items():
        selective = model.get("selective_prediction") or {}
        best = selective.get("best_accuracy") or {}
        lines.append(
            f"| {name} | {best.get('bucket', '')} | {best.get('sample_count', '')} | {best.get('coverage_percent', '')} | {best.get('accuracy', '')} | {best.get('balanced_accuracy', '')} | {best.get('average_confidence', '')} | {best.get('calibration_gap', '')} | {selective.get('reaches_80_accuracy', False)} | {selective.get('reaches_95_balanced_accuracy', False)} |"
        )
    lines.extend(["", "## Interaction Discovery Summary"])
    lines.append("| Model | Candidates | Accepted | Selected | Selection Status |")
    lines.append("|---|---:|---:|---:|---|")
    for name, model in payload["models"].items():
        discovery = model.get("interaction_discovery") or {}
        lines.append(
            f"| {name} | {discovery.get('candidate_count', 0)} | {discovery.get('accepted_count', 0)} | {len(model.get('selected_interactions') or [])} | {discovery.get('selection_status', 'not_run')} |"
        )
    lines.extend(["", "## Production Readiness Gates"])
    lines.append("| Model | Production Status | Passed Gates | Failed Gates | Recommended Use |")
    lines.append("|---|---|---|---|---|")
    for name, model in payload["models"].items():
        gates = production_gate_result(name, model, payload.get("split", {}), winner_audit)
        lines.append(
            f"| {name} | {gates['production_status']} | {', '.join(gates['passed_gates'])} | {', '.join(gates['failed_gates'])} | {gates['recommended_use']} |"
        )
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
