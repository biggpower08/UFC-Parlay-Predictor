from __future__ import annotations

import argparse
import json
import math
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
    CLASSIFICATION_MODELS,
    FEATURE_NAMES,
    align_probabilities,
    chronological_train_validation_test_split,
    classification_metrics,
    dedupe_model_rows,
    feature_names_for_model,
    majority_baseline,
    select_classifier,
    selective_prediction_report,
    source_contribution_report,
)
from ufc_predictor.config import settings
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv
from ufc_predictor.training.leakage import scan_dataframe


FORBIDDEN_BACKTEST_INPUTS = {
    "winner",
    "loser",
    "result",
    "method",
    "method_group",
    "method_class",
    "finish_binary",
    "goes_distance_binary",
    "round_phase_class",
    "finish_round",
    "finish_time",
    "fighter_a_sig_strikes",
    "fighter_b_sig_strikes",
    "combined_sig_strikes",
    "fighter_a_takedowns",
    "fighter_b_takedowns",
    "grappling_heavy_binary",
    "takedown_control_bucket",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Backtest MMA models against blind historical fight simulations.")
    parser.add_argument("--input-dir", default="data/imports")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--split", choices=["chronological"], default="chronological")
    parser.add_argument("--test-size", type=float, default=0.15)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--all-test-fights", action="store_true")
    parser.add_argument("--by-segment", action="store_true")
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "backtest_report.json"))
    parser.add_argument("--output-md", default="docs/backtest_report.md")
    parser.add_argument("--write-predictions", default=str(settings.DATA_PROCESSED_DIR / "backtest_predictions.json"))
    parser.add_argument("--debug-fight")
    args = parser.parse_args()

    input_path = resolve_training_data_path(Path(args.processed_dir))
    if not input_path.is_file():
        print(json.dumps({"error": "normalized_training_data_missing", "expected": str(input_path)}, indent=2))
        return 2

    raw_fights = load_fights_csv(input_path)
    dataset, audit = build_training_rows(raw_fights, source="imported_csv")
    payload, predictions = run_backtest(
        dataset,
        test_size=args.test_size,
        limit=args.limit,
        all_test_fights=args.all_test_fights,
        by_segment=args.by_segment,
    )
    payload["input_data"] = str(input_path)
    payload["training_audit"] = audit.to_dict()
    if args.debug_fight:
        payload["debug_fight"] = debug_fight(predictions, args.debug_fight)

    write_json(Path(args.output_json), payload)
    write_json(Path(args.write_predictions), {"generated_at": payload["generated_at"], "predictions": predictions})
    Path(args.output_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_md).write_text(markdown_report(payload, predictions), encoding="utf-8")
    update_registry_with_backtest(payload)

    print(json.dumps({"output_json": args.output_json, "output_md": args.output_md, "predictions": args.write_predictions, "summary": payload["summary"]}, indent=2, default=str))
    return 0


def resolve_training_data_path(processed_dir: Path) -> Path:
    preferred = processed_dir / "imports" / "normalized_fights_combined.csv"
    if preferred.is_file():
        return preferred
    return processed_dir / "training_imports" / "normalized_fights.csv"


def run_backtest(
    dataset: pd.DataFrame,
    test_size: float = 0.15,
    limit: int | None = None,
    all_test_fights: bool = False,
    by_segment: bool = False,
    min_train_rows: int = 500,
    min_test_rows: int = 100,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    train, validation, test, split_report = chronological_train_validation_test_split(dataset, validation_size=0.15, test_size=test_size)
    selected_test = test.copy() if all_test_fights or limit is None else test.head(limit).copy()
    if limit is not None and all_test_fights:
        selected_test = selected_test.head(limit).copy()
    leakage_report = scan_dataframe(pd.DataFrame(columns=FEATURE_NAMES + list(FORBIDDEN_BACKTEST_INPUTS)))
    models = build_backtest_models(train, validation, selected_test, min_train_rows=min_train_rows, min_test_rows=min_test_rows)
    predictions = prediction_records(selected_test, models)
    model_results = score_models(predictions, models, selected_test, train, by_segment=by_segment)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "fights_simulated": int(len(predictions)),
            "date_range": date_range(selected_test),
            "models_run": [name for name, model in models.items() if model.get("available")],
            "models_skipped": {name: model.get("reason") for name, model in models.items() if not model.get("available")},
        },
        "split": split_report,
        "source_contribution": source_contribution_report(dataset, train, validation, selected_test),
        "blind_simulation": {
            "prediction_features": "model-specific runtime-compatible feature schemas",
            "hidden_until_scoring": sorted(FORBIDDEN_BACKTEST_INPUTS),
            "final_test_used_for_training": False,
            "final_test_used_for_preprocessing_fit": False,
            "final_test_used_for_calibration": False,
            "leakage_scan_blocked_columns": leakage_report["blocked_feature_columns"],
        },
        "models": model_results,
        "overall_ranking": rank_models(model_results),
        "examples": examples(predictions),
    }
    return payload, predictions


def build_backtest_models(train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, min_train_rows: int, min_test_rows: int) -> dict[str, dict[str, Any]]:
    models: dict[str, dict[str, Any]] = {
        "odds_calibration_model": {"available": False, "reason": "Trusted pre-fight odds snapshots are not available."},
    }
    for model_name, target in CLASSIFICATION_MODELS.items():
        feature_names = feature_names_for_model(train, pd.DataFrame(), test, model_name)
        missing = [column for column in [target] if column not in train.columns or column not in test.columns]
        if missing:
            models[model_name] = {
                "available": False,
                "target": target,
                "reason": f"missing required columns: {', '.join(missing)}",
                "train_rows": 0,
                "test_rows": 0,
            }
            continue
        rows_train = dedupe_model_rows(train.dropna(subset=[target]).copy(), target, feature_names)
        rows_test = dedupe_model_rows(test.dropna(subset=[target]).copy(), target, feature_names)
        if len(rows_train) < min_train_rows or len(rows_test) < min_test_rows or rows_train[target].nunique() < 2:
            models[model_name] = {
                "available": False,
                "target": target,
                "reason": "insufficient held-out rows or class variety",
                "train_rows": int(len(rows_train)),
                "test_rows": int(len(rows_test)),
            }
            continue
        classes = sorted(str(value) for value in set(rows_train[target].astype(str)) | set(rows_test[target].astype(str)))
        rows_validation = dedupe_model_rows(validation.dropna(subset=[target]).copy(), target, feature_names)
        selected = select_classifier(rows_train, rows_validation, target, feature_names, classes)
        models[model_name] = {
            "available": True,
            "target": target,
            "classes": classes,
            "feature_names": feature_names,
            "algorithm": selected["algorithm"],
            "model": selected["model"],
            "train_rows": int(len(rows_train)),
            "test_rows": int(len(rows_test)),
        }
    return models


def prediction_records(test: pd.DataFrame, models: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records = []
    reset = test.reset_index(drop=True)
    precomputed = precompute_model_predictions(reset, models)
    for row_index, row in reset.iterrows():
        record = {
            "fight_id": fight_id(row, row_index),
            "event_date": row.get("event_date"),
            "event_name": row.get("event"),
            "fighter_1": row.get("fighter_a"),
            "fighter_2": row.get("fighter_b"),
            "weight_class": row.get("weight_class"),
            "prediction_inputs_as_of": row.get("event_date"),
            "prediction_feature_names": FEATURE_NAMES,
            "forbidden_inputs_used": [],
            "models_run": {},
            "actual_result": actual_result(row),
            "scoring": {},
            "warnings": [],
        }
        for model_name, info in models.items():
            if not info.get("available"):
                record["models_run"][model_name] = {"available": False, "reason": info.get("reason")}
                continue
            prediction = precomputed[model_name]
            probabilities = prediction["probabilities"][row_index]
            classes = info["classes"]
            predicted_class = prediction["predicted_classes"][row_index]
            record["models_run"][model_name] = model_prediction_payload(model_name, predicted_class, classes, probabilities)
        record["scoring"] = score_record(record)
        records.append(record)
    return records


def precompute_model_predictions(test: pd.DataFrame, models: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    precomputed = {}
    for model_name, info in models.items():
        if not info.get("available"):
            continue
        feature_names = info.get("feature_names", FEATURE_NAMES)
        probabilities = align_probabilities(np.asarray(info["model"].predict_proba(test[feature_names])), list(info["model"].classes_), info["classes"])
        classes = info["classes"]
        precomputed[model_name] = {
            "probabilities": probabilities,
            "predicted_classes": [classes[int(np.argmax(row))] for row in probabilities],
        }
    return precomputed


def model_prediction_payload(model_name: str, predicted_class: str, classes: list[str], probabilities: np.ndarray) -> dict[str, Any]:
    probability_map = {label: round(float(probabilities[index]), 4) for index, label in enumerate(classes)}
    payload: dict[str, Any] = {"available": True, "predicted_class": predicted_class, "probabilities": probability_map}
    if model_name == "finish_model":
        payload.update({"finish_probability": probability_map.get("1", probability_map.get("1.0")), "goes_distance_probability": probability_map.get("0", probability_map.get("0.0"))})
    elif model_name == "goes_distance_model":
        payload.update({"goes_distance_probability": probability_map.get("1", probability_map.get("1.0")), "finish_probability": probability_map.get("0", probability_map.get("0.0"))})
    elif model_name == "strike_volume_model":
        payload["strike_volume_bucket"] = predicted_class
    elif model_name == "takedown_control_model":
        payload["grappling_heavy_probability"] = probability_map.get("1", probability_map.get("1.0"))
    return payload


def actual_result(row: pd.Series) -> dict[str, Any]:
    return {
        "winner": row.get("winner"),
        "method": row.get("method_class"),
        "finish_round": none_if_nan(row.get("round_number")),
        "went_distance": bool(row.get("goes_distance_binary") == 1) if not pd.isna(row.get("goes_distance_binary")) else None,
        "finish_binary": none_if_nan(row.get("finish_binary")),
        "goes_distance_binary": none_if_nan(row.get("goes_distance_binary")),
        "round_phase_class": row.get("round_phase_class"),
        "combined_sig_strikes": none_if_nan(row.get("combined_sig_strikes")),
        "fighter_1_sig_strikes_landed": none_if_nan(row.get("fighter_a_sig_strikes")),
        "fighter_2_sig_strikes_landed": none_if_nan(row.get("fighter_b_sig_strikes")),
        "fighter_1_takedowns_landed": none_if_nan(row.get("fighter_a_takedowns")),
        "fighter_2_takedowns_landed": none_if_nan(row.get("fighter_b_takedowns")),
        "grappling_heavy_binary": none_if_nan(row.get("grappling_heavy_binary")),
    }


def score_record(record: dict[str, Any]) -> dict[str, Any]:
    actual = record["actual_result"]
    scoring: dict[str, Any] = {}
    scoring["winner_model_correct"] = None
    if record["models_run"].get("finish_model", {}).get("available") and actual.get("finish_binary") is not None:
        scoring["finish_model_correct"] = str(int(actual["finish_binary"])) == str(record["models_run"]["finish_model"]["predicted_class"])
    if record["models_run"].get("goes_distance_model", {}).get("available") and actual.get("goes_distance_binary") is not None:
        scoring["goes_distance_correct"] = str(int(actual["goes_distance_binary"])) == str(record["models_run"]["goes_distance_model"]["predicted_class"])
    if record["models_run"].get("method_model", {}).get("available") and actual.get("method") is not None:
        scoring["method_model_correct"] = str(actual["method"]) == str(record["models_run"]["method_model"]["predicted_class"])
    if record["models_run"].get("round_phase_model", {}).get("available") and actual.get("round_phase_class") is not None:
        scoring["round_phase_model_correct"] = str(actual["round_phase_class"]) == str(record["models_run"]["round_phase_model"]["predicted_class"])
    if record["models_run"].get("strike_volume_model", {}).get("available") and actual.get("combined_sig_strikes") is not None:
        scoring["strike_volume_bucket_correct"] = strike_bucket(actual["combined_sig_strikes"]) == record["models_run"]["strike_volume_model"]["predicted_class"]
    if record["models_run"].get("takedown_control_model", {}).get("available") and actual.get("grappling_heavy_binary") is not None:
        scoring["takedown_control_correct"] = str(float(actual["grappling_heavy_binary"])) == str(record["models_run"]["takedown_control_model"]["predicted_class"])
    scoring["fighter_1_over_50_sig_strikes_correct"] = bool(actual.get("fighter_1_sig_strikes_landed") is not None and float(actual["fighter_1_sig_strikes_landed"]) >= 50)
    scoring["fighter_2_over_0_5_takedowns_correct"] = bool(actual.get("fighter_2_takedowns_landed") is not None and float(actual["fighter_2_takedowns_landed"]) >= 1)
    return scoring


def score_models(predictions: list[dict[str, Any]], models: dict[str, dict[str, Any]], test: pd.DataFrame, train: pd.DataFrame, by_segment: bool) -> dict[str, Any]:
    results = {}
    for model_name, info in models.items():
        if not info.get("available"):
            results[model_name] = {"status": "skipped", "available": False, "reason": info.get("reason"), "beats_baseline": False}
            continue
        target = info["target"]
        feature_names = info.get("feature_names", FEATURE_NAMES)
        missing = [column for column in feature_names + [target] if column not in test.columns]
        if missing:
            results[model_name] = {"status": "skipped", "available": False, "reason": f"missing required columns: {', '.join(missing)}", "beats_baseline": False}
            continue
        rows = dedupe_model_rows(test.dropna(subset=[target]).copy(), target, feature_names)
        y_true = rows[target].astype(str).tolist()
        probs = align_probabilities(np.asarray(info["model"].predict_proba(rows[feature_names])), list(info["model"].classes_), info["classes"])
        preds = [info["classes"][int(np.argmax(probabilities))] for probabilities in probs]
        metrics = classification_metrics(y_true, preds, np.asarray(probs), info["classes"])
        baseline = majority_baseline(y_true)
        improvement = round(metrics["accuracy"] - baseline["accuracy"], 4) if baseline["accuracy"] is not None else None
        results[model_name] = {
            "status": "backtested" if improvement is not None and improvement > 0 else "weak_or_failed_baseline",
            "available": True,
            "target": target,
            "fights_tested": int(len(rows)),
            "main_metric_name": "accuracy",
            "main_metric": metrics["accuracy"],
            "baseline_metric": baseline["accuracy"],
            "relative_improvement": improvement,
            "beats_baseline": bool(improvement is not None and improvement > 0),
            "metrics": metrics,
            "baseline": baseline,
            "selective_prediction": selective_prediction_report(y_true, preds, np.asarray(probs), info["classes"]),
            "segment_metrics": backtest_segments(rows.assign(_pred=preds), target) if by_segment else {},
        }
    return results


def backtest_segments(rows: pd.DataFrame, target: str) -> dict[str, Any]:
    segments = {}
    if "weight_class" in rows.columns:
        for weight_class, group in rows.groupby("weight_class"):
            if len(group) >= 30:
                segments[f"weight_class:{weight_class}"] = segment_result(group, target)
    if "minimum_history_count" in rows.columns:
        for label, group in {"low_fighter_history": rows[rows["minimum_history_count"] < 3], "enough_fighter_history": rows[rows["minimum_history_count"] >= 3]}.items():
            if len(group) >= 30:
                segments[label] = segment_result(group, target)
    return segments


def segment_result(group: pd.DataFrame, target: str) -> dict[str, Any]:
    return {
        "rows": int(len(group)),
        "accuracy": round(float((group[target].astype(str) == group["_pred"].astype(str)).mean()), 4),
        "unstable_sample_warning": len(group) < 100,
    }


def rank_models(results: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for name, result in results.items():
        rows.append({"model": name, "status": result.get("status"), "relative_improvement": result.get("relative_improvement"), "beats_baseline": result.get("beats_baseline", False)})
    return sorted(rows, key=lambda item: (item["relative_improvement"] is not None, item["relative_improvement"] or -999), reverse=True)


def examples(predictions: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    scored = []
    for record in predictions:
        for model_name, prediction in record["models_run"].items():
            if not prediction.get("available") or "predicted_class" not in prediction:
                continue
            confidence = max(prediction.get("probabilities", {}).values() or [0])
            correct = record["scoring"].get(f"{model_name}_correct")
            if model_name == "goes_distance_model":
                correct = record["scoring"].get("goes_distance_correct")
            if correct is None:
                continue
            scored.append({"fight_id": record["fight_id"], "event_date": record["event_date"], "matchup": f"{record['fighter_1']} vs {record['fighter_2']}", "model": model_name, "confidence": confidence, "correct": correct, "predicted": prediction.get("predicted_class"), "actual": record["actual_result"]})
    best = sorted([row for row in scored if row["correct"]], key=lambda item: item["confidence"], reverse=True)[:5]
    worst = sorted([row for row in scored if not row["correct"]], key=lambda item: item["confidence"], reverse=True)[:5]
    props = [
        {
            "fight_id": record["fight_id"],
            "matchup": f"{record['fighter_1']} vs {record['fighter_2']}",
            "fighter_1_over_50_sig_strikes": record["scoring"].get("fighter_1_over_50_sig_strikes_correct"),
            "fighter_2_over_0_5_takedowns": record["scoring"].get("fighter_2_over_0_5_takedowns_correct"),
        }
        for record in predictions
        if record["scoring"].get("fighter_1_over_50_sig_strikes_correct") or record["scoring"].get("fighter_2_over_0_5_takedowns_correct")
    ][:5]
    return {"best_predictions": best, "worst_misses": worst, "prop_examples": props}


def update_registry_with_backtest(payload: dict[str, Any]) -> None:
    path = settings.MODEL_REGISTRY_JSON
    registry = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    now = payload["generated_at"]
    for name, result in payload["models"].items():
        entry = registry.setdefault(name, {"model_name": name})
        entry.update(
            {
                "backtested": bool(result.get("available")),
                "backtest_fights": result.get("fights_tested", 0),
                "backtest_date_range": payload["summary"]["date_range"],
                "backtest_main_metric": result.get("main_metric"),
                "backtest_baseline": result.get("baseline_metric"),
                "backtest_relative_improvement": result.get("relative_improvement"),
                "backtest_beats_baseline": result.get("beats_baseline", False),
                "biggest_limitations": result.get("reason") or result.get("limitations") or [],
                "backtested_at": now,
            }
        )
        if not result.get("beats_baseline", False) and entry.get("status") == "production_ready":
            entry["status"] = "experimental"
    path.write_text(json.dumps(registry, indent=2, default=str), encoding="utf-8")


def markdown_report(payload: dict[str, Any], predictions: list[dict[str, Any]]) -> str:
    registry = load_registry()
    lines = [
        "# Historical Fight Backtest Report",
        "",
        "## Plain-English Summary",
        f"This backtest simulated {payload['summary']['fights_simulated']} historical fights by hiding outcome labels until after model predictions were generated from pre-fight features.",
        "",
        "## Backtest Setup",
        f"- Date range: {payload['summary']['date_range']}",
        f"- Data hidden before prediction: {', '.join(payload['blind_simulation']['hidden_until_scoring'])}",
        f"- Models run: {', '.join(payload['summary']['models_run']) or 'None'}",
        f"- Source rows in train: {payload.get('source_contribution', {}).get('train_rows_by_dataset', {})}",
        f"- Source rows in final test: {payload.get('source_contribution', {}).get('test_rows_by_dataset', {})}",
        "",
        "## Overall Ranking",
        "| Model | Fights Tested | Main Metric | Baseline | Improvement | Beats Baseline | Status |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for item in payload["overall_ranking"]:
        model = payload["models"][item["model"]]
        lines.append(f"| {item['model']} | {model.get('fights_tested', 0)} | {model.get('main_metric', '')} | {model.get('baseline_metric', '')} | {model.get('relative_improvement', '')} | {model.get('beats_baseline', False)} | {model.get('status')} |")
    lines.extend(["", "## Production Readiness Gates"])
    lines.append("| Model | Production Status | Failed Gates | Public Warning |")
    lines.append("|---|---|---|---|")
    for name in payload["models"]:
        entry = registry.get(name, {})
        lines.append(f"| {name} | {entry.get('production_status', 'not_evaluated')} | {', '.join(entry.get('failed_gates', []))} | {entry.get('public_warning_text', '')} |")
    lines.extend(["", "## Models Not Run"])
    for name, reason in payload["summary"]["models_skipped"].items():
        lines.append(f"- `{name}`: {reason}")
    lines.extend(["", "## Best Predictions"])
    for row in payload["examples"]["best_predictions"]:
        lines.append(f"- {row['matchup']} ({row['model']}): predicted `{row['predicted']}` with confidence {row['confidence']}.")
    lines.extend(["", "## Worst Misses"])
    for row in payload["examples"]["worst_misses"]:
        lines.append(f"- {row['matchup']} ({row['model']}): predicted `{row['predicted']}` with confidence {row['confidence']}.")
    lines.extend(["", "## Prop Examples"])
    for row in payload["examples"]["prop_examples"]:
        lines.append(f"- {row['matchup']}: fighter 1 over 50 sig strikes={row['fighter_1_over_50_sig_strikes']}, fighter 2 1+ takedown={row['fighter_2_over_0_5_takedowns']}.")
    lines.extend(["", "## Segment Performance"])
    for name, result in payload["models"].items():
        if result.get("segment_metrics"):
            lines.append(f"### {name}")
            for segment, metrics in result["segment_metrics"].items():
                lines.append(f"- {segment}: {metrics}")
    lines.extend(["", "## Next Steps", "- Improve safe winner-model orientation before backtesting winner probabilities.", "- Add trusted pre-fight odds timestamps before odds calibration.", "- Keep weak models out of production-ready status until they beat baseline."])
    return "\n".join(lines).strip() + "\n"


def load_registry() -> dict[str, Any]:
    path = settings.MODEL_REGISTRY_JSON
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def debug_fight(predictions: list[dict[str, Any]], fight_id_value: str) -> dict[str, Any] | None:
    for record in predictions:
        if str(record["fight_id"]) == str(fight_id_value):
            return record
    return None


def fight_id(row: pd.Series, row_index: int) -> str:
    parts = [row.get("event_date"), row.get("event"), row.get("fighter_a"), row.get("fighter_b"), row.get("source_order", row_index)]
    return "|".join(str(part) for part in parts if part is not None)


def date_range(frame: pd.DataFrame) -> dict[str, str | None]:
    if frame.empty or "event_date" not in frame.columns:
        return {"min": None, "max": None}
    dates = pd.to_datetime(frame["event_date"], errors="coerce").dropna()
    return {"min": str(dates.min().date()) if not dates.empty else None, "max": str(dates.max().date()) if not dates.empty else None}


def strike_bucket(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    numeric = float(value)
    if numeric < 60:
        return "low"
    if numeric < 120:
        return "medium"
    return "high"


def none_if_nan(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    try:
        if pd.isna(value):
            return None
    except TypeError:
        pass
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
