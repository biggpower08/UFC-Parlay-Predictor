from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_model_accuracy import CLASSIFICATION_MODELS, chronological_train_validation_test_split, feature_names_for_model
from ufc_predictor.config import settings
from ufc_predictor.features.feature_schema import (
    DATA_QUALITY_FEATURES,
    ELO_FEATURES,
    GRAPPLING_FEATURES,
    OPPONENT_WEAKNESS_FEATURES,
    PROFILE_FEATURES,
    RECENT_FORM_FEATURES,
    RECORD_FEATURES,
    SIZE_CONTEXT_FEATURES,
    STRIKING_FEATURES,
    STYLE_SCORE_FEATURES,
)
from ufc_predictor.training.dataset_builder import build_training_rows, load_fights_csv, normalize_method, normalize_result_type, parse_round_time_seconds
from ufc_predictor.training.deduping import add_deduping_columns, dedupe_summary
from ufc_predictor.utils.helpers import normalize_name


TARGET_COLUMNS = {
    "winner_model": "f1_wins_safe",
    "fight_duration_model": "finish_binary",
    "finish_model": "finish_binary",
    "goes_distance_model": "goes_distance_binary",
    "over_1_5_model": "over_1_5_binary",
    "over_2_5_model": "over_2_5_binary",
    "ends_before_round_3_model": "ends_before_round_3_binary",
    "finish_in_round_1_model": "finish_in_round_1_binary",
    "finish_type_model": "finish_type_class",
    "method_umbrella_model": "method_class",
    "method_model": "method_class",
    "strike_volume_model": "combined_strike_volume_bucket",
    "takedown_control_model": "grappling_heavy_binary",
}

FEATURE_GROUPS = {
    "profile": PROFILE_FEATURES,
    "record": RECORD_FEATURES,
    "recent_form": RECENT_FORM_FEATURES,
    "elo": ELO_FEATURES,
    "striking": STRIKING_FEATURES,
    "grappling": GRAPPLING_FEATURES,
    "style": STYLE_SCORE_FEATURES,
    "opponent_weakness": OPPONENT_WEAKNESS_FEATURES,
    "size_context": SIZE_CONTEXT_FEATURES,
    "data_quality": DATA_QUALITY_FEATURES,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Diagnose source-transfer weakness across imported MMA datasets.")
    parser.add_argument("--processed-dir", default=str(settings.DATA_PROCESSED_DIR))
    parser.add_argument("--input", default=None)
    parser.add_argument("--output-json", default=str(settings.DATA_PROCESSED_DIR / "source_transfer_diagnostics.json"))
    parser.add_argument("--output-md", default="docs/source_transfer_diagnostics.md")
    parser.add_argument("--drift-output-json", default=str(settings.DATA_PROCESSED_DIR / "source_feature_label_drift_report.json"))
    parser.add_argument("--drift-output-md", default="docs/source_feature_label_drift_report.md")
    parser.add_argument("--strategy-output-json", default=str(settings.DATA_PROCESSED_DIR / "source_strategy_ablation_report.json"))
    parser.add_argument("--strategy-output-md", default="docs/source_strategy_ablation_report.md")
    args = parser.parse_args()

    input_path = Path(args.input) if args.input else resolve_training_data_path(Path(args.processed_dir))
    if not input_path.is_file():
        print(json.dumps({"error": "normalized_training_data_missing", "expected": str(input_path)}, indent=2))
        return 2

    raw = load_fights_csv(input_path)
    normalized_raw = add_deduping_columns(raw) if not raw.empty else raw
    dataset, audit = build_training_rows(raw, source="imported_csv")
    train, validation, test, split = chronological_train_validation_test_split(dataset, validation_size=0.15, test_size=0.15)
    model_report = load_json(settings.DATA_PROCESSED_DIR / "model_accuracy_report.json")
    registry = load_json(settings.MODEL_REGISTRY_JSON)

    diagnostics = build_source_diagnostics(normalized_raw, dataset, train, validation, test, model_report, registry, audit.to_dict(), split)
    drift = build_feature_label_drift_report(dataset, train, validation, test, model_report, registry)
    strategy = build_strategy_ablation_report(diagnostics, drift, model_report, registry)

    write_json(Path(args.output_json), diagnostics)
    write_json(Path(args.drift_output_json), drift)
    write_json(Path(args.strategy_output_json), strategy)
    write_text(Path(args.output_md), source_diagnostics_markdown(diagnostics))
    write_text(Path(args.drift_output_md), drift_markdown(drift))
    write_text(Path(args.strategy_output_md), strategy_markdown(strategy))

    print(json.dumps({"diagnostics": args.output_json, "drift": args.drift_output_json, "strategy": args.strategy_output_json}, indent=2))
    return 0


def resolve_training_data_path(processed_dir: Path) -> Path:
    preferred = processed_dir / "imports" / "normalized_fights_combined.csv"
    if preferred.is_file():
        return preferred
    return processed_dir / "training_imports" / "normalized_fights.csv"


def build_source_diagnostics(
    raw: pd.DataFrame,
    dataset: pd.DataFrame,
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    model_report: dict,
    registry: dict,
    audit: dict,
    split: dict,
) -> dict[str, Any]:
    sources = sorted(dataset["source_dataset"].dropna().astype(str).unique()) if "source_dataset" in dataset.columns else []
    source_reports = {}
    train_validation = pd.concat([train, validation], ignore_index=True)
    raw_by_source = {source: raw[raw.get("source_dataset", pd.Series(dtype=str)).astype(str) == source].copy() for source in sources}
    for source in sources:
        rows = dataset[dataset["source_dataset"].astype(str) == source].copy()
        raw_rows = raw_by_source.get(source, pd.DataFrame())
        final_rows = test[test["source_dataset"].astype(str) == source].copy()
        tv_rows = train_validation[train_validation["source_dataset"].astype(str) == source].copy()
        model_impacts = model_source_impacts(source, model_report, registry)
        drift_grade = source_drift_grade(model_impacts, rows)
        source_reports[source] = {
            "row_count": int(len(rows)),
            "date_range": date_range(rows),
            "final_test_row_count": int(len(final_rows)),
            "train_validation_row_count": int(len(tv_rows)),
            "target_coverage_by_model": target_coverage(rows),
            "missingness_by_feature_group": missingness_by_feature_group(rows),
            "method_label_distribution": distribution(rows, "method_class"),
            "finish_goes_distance_distribution": {
                "finish_binary": distribution(rows, "finish_binary"),
                "goes_distance_binary": distribution(rows, "goes_distance_binary"),
            },
            "round_distribution": {
                "over_1_5_binary": distribution(rows, "over_1_5_binary"),
                "over_2_5_binary": distribution(rows, "over_2_5_binary"),
                "ends_before_round_3_binary": distribution(rows, "ends_before_round_3_binary"),
                "finish_in_round_1_binary": distribution(rows, "finish_in_round_1_binary"),
                "round_phase_class": distribution(rows, "round_phase_class"),
            },
            "finish_type_distribution": distribution(rows, "finish_type_class"),
            "strike_takedown_control_distribution": {
                "combined_strike_volume_bucket": distribution(rows, "combined_strike_volume_bucket"),
                "grappling_heavy_binary": distribution(rows, "grappling_heavy_binary"),
                "takedown_control_bucket": distribution(rows, "takedown_control_bucket"),
            },
            "fighter_name_normalization_issues": fighter_name_issues(raw_rows),
            "weight_class_normalization_issues": weight_class_issues(raw_rows, rows),
            "method_label_normalization_issues": method_label_issues(raw_rows),
            "finish_time_round_parsing_issues": finish_time_round_issues(raw_rows, rows),
            "no_contest_dq_overturned_handling": result_handling_issues(raw_rows, rows),
            "mirrored_duplicate_patterns": dedupe_summary(raw_rows) if not raw_rows.empty else dedupe_summary(rows),
            "source_priority_deduping_impact": source_priority_impact(source, raw, rows),
            "suspicious_columns_or_leakage_risks": suspicious_columns(raw_rows),
            "feature_distribution_drift_vs_others": feature_drift_vs_others(dataset, rows),
            "models_failing_hardest": model_impacts[:5],
            "drift_grade": drift_grade,
            "root_cause_summary": root_cause_summary(source, rows, model_impacts),
        }
    ufc = source_reports.get("ufc_stats_complete", {})
    return {
        "generated_at": now(),
        "input_summary": {
            "rows": int(len(dataset)),
            "sources": sources,
            "audit": audit,
            "split": split,
        },
        "source_reports": source_reports,
        "ufc_stats_complete_answer": {
            "present": bool(ufc),
            "likely_failure_mode": ufc.get("root_cause_summary", []),
            "is_noisy": "high missingness/stat distribution drift" in ufc.get("root_cause_summary", []),
            "label_difference_suspected": "label distribution drift" in ufc.get("root_cause_summary", []),
            "normalization_issue_suspected": bool(ufc.get("weight_class_normalization_issues", {}).get("variant_count") or ufc.get("method_label_normalization_issues", {}).get("noncanonical_count")),
            "duplicate_issue_suspected": bool((ufc.get("mirrored_duplicate_patterns") or {}).get("duplicate_fight_rows")),
            "target_definition_difference_suspected": any("round/time" in item for item in ufc.get("root_cause_summary", [])),
        },
    }


def build_feature_label_drift_report(dataset: pd.DataFrame, train: pd.DataFrame, validation: pd.DataFrame, test: pd.DataFrame, model_report: dict, registry: dict) -> dict[str, Any]:
    models = ["fight_duration_model", "finish_model", "goes_distance_model", "over_1_5_model", "over_2_5_model", "ends_before_round_3_model", "finish_in_round_1_model", "finish_type_model", "method_umbrella_model", "strike_volume_model", "takedown_control_model"]
    source_names = sorted(dataset["source_dataset"].dropna().astype(str).unique())
    model_reports = {}
    for model in models:
        target = TARGET_COLUMNS[model]
        features = feature_names_for_model(train, validation, test, model if model not in {"finish_model", "goes_distance_model"} else "fight_duration_model")
        by_source = {}
        for source in source_names:
            rows = dataset[dataset["source_dataset"].astype(str) == source].copy()
            final_rows = test[test["source_dataset"].astype(str) == source].copy()
            others = dataset[dataset["source_dataset"].astype(str) != source].copy()
            holdout = source_holdout_for(model, source, model_report)
            label_score = label_drift_score(rows, others, target)
            feature_score = feature_drift_score(rows, others, features)
            risk = source_risk_score(feature_score, label_score, holdout)
            by_source[source] = {
                "target": target,
                "row_count": int(len(rows)),
                "final_test_row_count": int(len(final_rows)),
                "target_rate": target_rate(rows, target),
                "baseline_rate": majority_rate(rows, target),
                "accuracy": holdout.get("accuracy"),
                "balanced_accuracy": holdout.get("balanced_accuracy"),
                "source_holdout_drop": holdout.get("metric_drop"),
                "unstable_sample_warning": bool(holdout.get("unstable_sample_warning") or len(final_rows) < 300),
                "missingness_by_selected_feature_group": missingness_by_feature_group(rows, features),
                "style_score_distributions": numeric_summary(rows, STYLE_SCORE_FEATURES),
                "opponent_weakness_score_distributions": numeric_summary(rows, OPPONENT_WEAKNESS_FEATURES),
                "selected_interaction_distributions": selected_interaction_distributions(model, source, rows, model_report),
                "low_history_row_rate": low_history_rate(rows),
                "enough_history_row_rate": round(1 - low_history_rate(rows), 4),
                "weight_class_distribution": distribution(rows, "weight_class"),
                "gender_division_distribution": gender_division_distribution(rows),
                "feature_drift_score": feature_score,
                "label_drift_score": label_score,
                "overall_source_risk_score": risk,
                "drift_grade": grade_from_score(risk),
            }
        model_reports[model] = {
            "production_status": registry.get(model, {}).get("production_status"),
            "source_holdout_status": registry.get(model, {}).get("source_holdout_status"),
            "sources": by_source,
        }
    return {"generated_at": now(), "models": model_reports}


def build_strategy_ablation_report(diagnostics: dict, drift: dict, model_report: dict, registry: dict) -> dict[str, Any]:
    strategies = []
    for model, target in TARGET_COLUMNS.items():
        if model == "winner_model":
            continue
        entry = registry.get(model, {})
        holdout = entry.get("source_holdout") or {}
        worst_source = holdout.get("worst_source")
        normal = entry.get("final_test_metric")
        strategies.extend(
            [
                strategy_row(model, "current_combined_source_training", [], normal, holdout, entry, "baseline strategy currently used for reports"),
                strategy_row(model, "exclude_ufc_stats_complete_from_training_test_on_it", ["ufc_stats_complete"], normal, holdout, entry, "already represented by source-holdout when ufc_stats_complete is the held-out source"),
                strategy_row(model, "source_quality_flags_enabled", [], normal, holdout, entry, "recommended next implementation; not used as direct source shortcut"),
                strategy_row(model, "source_balanced_sampling_or_weights", [], normal, holdout, entry, "candidate next experiment to reduce domination by any one source"),
                strategy_row(model, "model_specific_source_subset", [worst_source] if worst_source else [], normal, holdout, entry, model_specific_source_note(model, worst_source)),
            ]
        )
    return {
        "generated_at": now(),
        "selection_warning": "Strategies are diagnostic recovery candidates. Production status is still governed by strict source-holdout gates and should not be selected from final test alone.",
        "strategies": strategies,
        "recommendations": recovery_recommendations(registry),
    }


def strategy_row(model: str, name: str, excluded: list[str], normal_metric, holdout: dict, registry_entry: dict, note: str) -> dict[str, Any]:
    status = registry_entry.get("production_status")
    return {
        "model": model,
        "strategy": name,
        "sources_excluded": [item for item in excluded if item],
        "normal_chronological_metric": normal_metric,
        "source_holdout_metric": holdout.get("worst_source_metric"),
        "worst_source": holdout.get("worst_source"),
        "drop": holdout.get("worst_metric_drop"),
        "calibration_impact": "not_measured_in_this_ablation",
        "row_count_impact": "estimated_or_strategy_dependent",
        "production_status_after_gates": status,
        "production_status_improves": status == "production_candidate",
        "risk_notes": note,
    }


def model_source_impacts(source: str, model_report: dict, registry: dict) -> list[dict[str, Any]]:
    impacts = []
    for model, entry in (model_report.get("models") or {}).items():
        holdout = entry.get("source_holdout") or {}
        for row in holdout.get("by_source") or []:
            if row.get("source") == source:
                impacts.append(
                    {
                        "model": model,
                        "production_status": registry.get(model, {}).get("production_status"),
                        "source_holdout_status": holdout.get("status"),
                        "accuracy": row.get("accuracy"),
                        "balanced_accuracy": row.get("balanced_accuracy"),
                        "metric_drop": row.get("metric_drop"),
                        "balanced_accuracy_drop": row.get("balanced_accuracy_drop"),
                        "rows": row.get("rows"),
                        "unstable_sample_warning": row.get("unstable_sample_warning"),
                    }
                )
    return sorted(impacts, key=lambda item: float(item.get("metric_drop") or 0), reverse=True)


def target_coverage(rows: pd.DataFrame) -> dict[str, int]:
    return {model: int(rows[target].notna().sum()) if target in rows.columns else 0 for model, target in TARGET_COLUMNS.items()}


def missingness_by_feature_group(rows: pd.DataFrame, features: list[str] | None = None) -> dict[str, float]:
    groups = FEATURE_GROUPS if features is None else {"selected_features": features}
    output = {}
    for group, columns in groups.items():
        present = [column for column in columns if column in rows.columns]
        if not present or rows.empty:
            output[group] = 1.0
        else:
            output[group] = round(float(rows[present].isna().sum().sum()) / float(len(rows) * len(present)), 4)
    return output


def distribution(rows: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in rows.columns or rows.empty:
        return {}
    counts = Counter(str(value) for value in rows[column].dropna())
    return dict(sorted((key, int(value)) for key, value in counts.items()))


def date_range(rows: pd.DataFrame) -> dict[str, str | None]:
    dates = pd.to_datetime(rows.get("event_date"), errors="coerce").dropna() if not rows.empty else pd.Series(dtype="datetime64[ns]")
    return {"min": str(dates.min().date()) if not dates.empty else None, "max": str(dates.max().date()) if not dates.empty else None}


def fighter_name_issues(raw: pd.DataFrame) -> dict[str, Any]:
    columns = [column for column in ["fighter_1", "fighter_2", "fighter_a", "fighter_b", "winner_name", "loser_name"] if column in raw.columns]
    values = []
    for column in columns:
        values.extend(raw[column].dropna().astype(str).tolist())
    normalized = [normalize_name(value) for value in values]
    return {
        "raw_name_count": len(values),
        "empty_after_normalization": int(sum(1 for value in normalized if not value)),
        "punctuation_variant_examples": sorted({value for value in values if any(char in value for char in [".", "'", "-", "  "])})[:20],
    }


def weight_class_issues(raw: pd.DataFrame, rows: pd.DataFrame) -> dict[str, Any]:
    values = raw.get("weight_class", rows.get("weight_class", pd.Series(dtype=str))).dropna().astype(str)
    normalized = values.str.lower().str.replace(" bout", "", regex=False).str.strip()
    return {
        "variant_count": int(values.nunique() - normalized.nunique()),
        "raw_examples": sorted(values.unique().tolist())[:30],
        "normalized_examples": sorted(normalized.unique().tolist())[:30],
    }


def method_label_issues(raw: pd.DataFrame) -> dict[str, Any]:
    source = raw.get("method", raw.get("method_group", pd.Series(dtype=str))).dropna().astype(str)
    mapped = source.apply(normalize_method)
    return {
        "raw_distribution": dict(source.value_counts().head(30)),
        "canonical_distribution": dict(mapped.value_counts()),
        "noncanonical_count": int(sum(1 for value in source if value not in {"Decision", "KO/TKO", "Submission", "Other"})),
    }


def finish_time_round_issues(raw: pd.DataFrame, rows: pd.DataFrame) -> dict[str, Any]:
    time_col = raw.get("time", raw.get("finish_time", pd.Series(dtype=object)))
    parsed_time = time_col.apply(parse_round_time_seconds) if len(time_col) else pd.Series(dtype=object)
    rounds = pd.to_numeric(raw.get("round", rows.get("round_number", pd.Series(dtype=object))), errors="coerce")
    return {
        "rows": int(len(raw)),
        "missing_round_count": int(rounds.isna().sum()) if len(rounds) else 0,
        "missing_or_unparsed_time_count": int(parsed_time.isna().sum()) if len(parsed_time) else 0,
        "over_1_5_missing_labels": int(rows.get("over_1_5_binary", pd.Series(dtype=object)).isna().sum()) if not rows.empty else 0,
        "over_2_5_missing_labels": int(rows.get("over_2_5_binary", pd.Series(dtype=object)).isna().sum()) if not rows.empty else 0,
    }


def result_handling_issues(raw: pd.DataFrame, rows: pd.DataFrame) -> dict[str, Any]:
    raw_results = raw.get("result", pd.Series(dtype=object)).dropna().astype(str)
    normalized = raw_results.apply(normalize_result_type)
    non_win_rows = rows[rows.get("result_type", pd.Series(dtype=object)).isin(["nc", "draw", "unknown"])] if "result_type" in rows.columns else pd.DataFrame()
    labels_present = int(non_win_rows[list(set(TARGET_COLUMNS.values()) & set(non_win_rows.columns))].notna().sum().sum()) if not non_win_rows.empty else 0
    return {
        "raw_result_distribution": dict(raw_results.value_counts().head(20)),
        "normalized_result_distribution": dict(normalized.value_counts()),
        "non_win_rows_with_model_labels": labels_present,
    }


def source_priority_impact(source: str, raw: pd.DataFrame, rows: pd.DataFrame) -> dict[str, int]:
    if raw.empty or "source_dataset" not in raw.columns:
        return {"rows_before_training_builder": int(len(raw)), "rows_after_training_builder": int(len(rows)), "difference": 0}
    source_rows = raw[raw["source_dataset"].astype(str) == source]
    return {"rows_before_training_builder": int(len(source_rows)), "rows_after_training_builder": int(len(rows)), "difference": int(len(source_rows) - len(rows))}


def suspicious_columns(raw: pd.DataFrame) -> list[str]:
    suspicious_terms = ["winner", "loser", "result", "method", "finish", "round", "time", "odds", "moneyline"]
    return sorted([column for column in raw.columns if any(term in column.lower() for term in suspicious_terms)])[:80]


def feature_drift_vs_others(all_rows: pd.DataFrame, source_rows: pd.DataFrame) -> dict[str, Any]:
    scores = {}
    other_rows = all_rows[~all_rows.index.isin(source_rows.index)].copy()
    for group, columns in FEATURE_GROUPS.items():
        scores[group] = feature_drift_score(source_rows, other_rows, columns)
    return scores


def feature_drift_score(rows: pd.DataFrame, others: pd.DataFrame, columns: list[str]) -> float:
    values = []
    for column in columns:
        if column not in rows.columns or column not in others.columns:
            continue
        left = pd.to_numeric(rows[column], errors="coerce").dropna()
        right = pd.to_numeric(others[column], errors="coerce").dropna()
        if len(left) < 20 or len(right) < 20:
            continue
        std = float(right.std()) or 1.0
        values.append(min(3.0, abs(float(left.mean()) - float(right.mean())) / std) / 3.0)
    return round(float(sum(values) / len(values)), 4) if values else 0.0


def label_drift_score(rows: pd.DataFrame, others: pd.DataFrame, column: str) -> float:
    if column not in rows.columns or column not in others.columns:
        return 1.0
    left = rows[column].dropna().astype(str)
    right = others[column].dropna().astype(str)
    if left.empty or right.empty:
        return 1.0
    labels = sorted(set(left) | set(right))
    left_rates = left.value_counts(normalize=True)
    right_rates = right.value_counts(normalize=True)
    tvd = sum(abs(float(left_rates.get(label, 0)) - float(right_rates.get(label, 0))) for label in labels) / 2
    return round(float(tvd), 4)


def source_holdout_for(model: str, source: str, report: dict) -> dict[str, Any]:
    entry = (report.get("models") or {}).get(model) or {}
    if model in {"finish_model", "goes_distance_model"}:
        entry = (report.get("models") or {}).get("fight_duration_model") or entry
    if model == "method_model":
        entry = (report.get("models") or {}).get("method_umbrella_model") or entry
    holdout = entry.get("source_holdout") or {}
    for row in holdout.get("by_source") or []:
        if row.get("source") == source:
            return row
    return {}


def target_rate(rows: pd.DataFrame, column: str) -> float | dict[str, float] | None:
    if column not in rows.columns:
        return None
    values = rows[column].dropna()
    if values.empty:
        return None
    numeric = pd.to_numeric(values, errors="coerce")
    if numeric.notna().all() and set(numeric.dropna().unique()).issubset({0, 1}):
        return round(float(numeric.mean()), 4)
    return {str(key): round(float(value), 4) for key, value in values.astype(str).value_counts(normalize=True).sort_index().items()}


def majority_rate(rows: pd.DataFrame, column: str) -> float | None:
    if column not in rows.columns:
        return None
    values = rows[column].dropna().astype(str)
    if values.empty:
        return None
    return round(float(values.value_counts(normalize=True).iloc[0]), 4)


def numeric_summary(rows: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, float]]:
    output = {}
    for column in columns:
        if column not in rows.columns:
            continue
        values = pd.to_numeric(rows[column], errors="coerce").dropna()
        if len(values) < 20:
            continue
        output[column] = {"mean": round(float(values.mean()), 4), "median": round(float(values.median()), 4), "missing_rate": round(float(rows[column].isna().mean()), 4)}
    return output


def selected_interaction_distributions(model: str, source: str, rows: pd.DataFrame, report: dict) -> dict[str, Any]:
    entry = (report.get("models") or {}).get(model) or {}
    interactions = entry.get("selected_interactions_detailed") or []
    output = {}
    for item in interactions:
        name = item.get("name")
        if name and name in rows.columns:
            output[name] = numeric_summary(rows, [name]).get(name, {})
    return output


def low_history_rate(rows: pd.DataFrame) -> float:
    if "minimum_history_count" not in rows.columns or rows.empty:
        return 1.0
    values = pd.to_numeric(rows["minimum_history_count"], errors="coerce").fillna(0)
    return round(float((values < 3).mean()), 4)


def gender_division_distribution(rows: pd.DataFrame) -> dict[str, int]:
    values = rows.get("weight_class", pd.Series(dtype=str)).dropna().astype(str).str.lower()
    return {"women": int(values.str.contains("women").sum()), "men_or_open": int((~values.str.contains("women")).sum())}


def source_risk_score(feature_score: float, label_score: float, holdout: dict) -> float:
    drop = float(holdout.get("metric_drop") or 0)
    balanced = 1 - float(holdout.get("balanced_accuracy") or 0.5)
    return round(max(0.0, min(1.0, 0.35 * feature_score + 0.35 * label_score + 0.2 * max(0, drop) + 0.1 * max(0, balanced))), 4)


def grade_from_score(score: float) -> str:
    if score >= 0.55:
        return "dangerous drift"
    if score >= 0.35:
        return "high drift"
    if score >= 0.18:
        return "medium drift"
    return "low drift"


def source_drift_grade(model_impacts: list[dict[str, Any]], rows: pd.DataFrame) -> str:
    worst_drop = max([float(item.get("metric_drop") or 0) for item in model_impacts] or [0])
    missing = max(missingness_by_feature_group(rows).values() or [0])
    score = min(1.0, worst_drop + 0.3 * missing)
    return grade_from_score(score)


def root_cause_summary(source: str, rows: pd.DataFrame, impacts: list[dict[str, Any]]) -> list[str]:
    reasons = []
    if any(float(item.get("metric_drop") or 0) > 0.15 for item in impacts):
        reasons.append("source-holdout regression")
    if label_drift_score(rows, rows.iloc[0:0], "method_class") >= 1.0:
        reasons.append("missing or sparse labels")
    group_missing = missingness_by_feature_group(rows)
    if max(group_missing.values() or [0]) > 0.5:
        reasons.append("high missingness/stat distribution drift")
    if any(item.get("model") in {"over_1_5_model", "over_2_5_model", "ends_before_round_3_model"} and float(item.get("metric_drop") or 0) > 0.12 for item in impacts):
        reasons.append("round/time target transfer weakness")
    if source == "ufc_stats_complete" and impacts:
        reasons.append("models trained on other sources do not transfer cleanly to this source")
    return reasons or ["no obvious high-risk drift detected"]


def recovery_recommendations(registry: dict) -> dict[str, str]:
    return {
        "winner_model": "Keep high_confidence_only until winner-specific source holdout and leakage audit gates pass.",
        "fight_duration_model": "Investigate duration label drift and try source-stable feature subsets before restoring candidate status.",
        "finish_model": "Compatibility output follows fight_duration_model.",
        "goes_distance_model": "Compatibility output follows fight_duration_model.",
        "round_models": "Check round/time parsing and avoid production until source-holdout stabilizes.",
        "finish_type_model": "Audit method mappings and consider binary KO/TKO-vs-other and submission-vs-other finish submodels.",
        "method_umbrella_model": "Keep composite and improve through duration and finish-type components.",
        "strike_volume_model": "Treat ufc_stats_complete as a likely preferred stat-label source, but keep output experimental until transfer/calibration improves.",
        "takedown_control_model": "Check takedown/control coverage and definitions by source before production use.",
        "odds_calibration_model": "Remain blocked until trusted pre-fight odds timestamps exist.",
    }


def model_specific_source_note(model: str, worst_source: str | None) -> str:
    if model in {"strike_volume_model", "takedown_control_model"}:
        return "stat models may need source eligibility based on reliable strike/takedown coverage, not all combined sources"
    if model in {"over_1_5_model", "over_2_5_model", "ends_before_round_3_model", "finish_in_round_1_model"}:
        return "round models should use only sources with reliable finish round/time parsing"
    if model in {"finish_type_model", "method_umbrella_model", "method_model"}:
        return "method models should use sources with clean canonical method labels"
    return f"review weakest source {worst_source} before packaging"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def source_diagnostics_markdown(payload: dict) -> str:
    lines = ["# Source Transfer Diagnostics", "", "## Plain-English Summary", "This report compares each imported source against the combined training set and highlights why source-holdout transfer is weak. It does not weaken gates or mark any model production-ready.", "", "## Source Summary", "| Source | Rows | Date Range | Final-Test Rows | Drift Grade | Hardest Failing Models |", "|---|---:|---|---:|---|---|"]
    for source, report in payload["source_reports"].items():
        hardest = ", ".join(item["model"] for item in report.get("models_failing_hardest", [])[:3])
        date = report.get("date_range", {})
        lines.append(f"| {source} | {report.get('row_count')} | {date.get('min')} to {date.get('max')} | {report.get('final_test_row_count')} | {report.get('drift_grade')} | {hardest} |")
    lines += ["", "## UFCStats Complete Answer"]
    answer = payload.get("ufc_stats_complete_answer", {})
    for key, value in answer.items():
        lines.append(f"- {key}: {value}")
    lines += ["", "## Source Details"]
    for source, report in payload["source_reports"].items():
        lines += [f"### {source}", f"- Root causes: {', '.join(report.get('root_cause_summary', []))}", f"- Target coverage: `{json.dumps(report.get('target_coverage_by_model', {}), default=str)}`", f"- Missingness by feature group: `{json.dumps(report.get('missingness_by_feature_group', {}), default=str)}`", ""]
    return "\n".join(lines) + "\n"


def drift_markdown(payload: dict) -> str:
    lines = ["# Source Feature And Label Drift Report", "", "## Plain-English Summary", "This report grades each model/source pair for label drift, feature drift, and source-holdout risk. Higher-risk rows should stay experimental.", "", "| Model | Source | Rows | Target Rate | Holdout Drop | Feature Drift | Label Drift | Risk | Grade |", "|---|---|---:|---|---:|---:|---:|---:|---|"]
    for model, item in payload.get("models", {}).items():
        for source, report in item.get("sources", {}).items():
            lines.append(f"| {model} | {source} | {report.get('row_count')} | {report.get('target_rate')} | {report.get('source_holdout_drop')} | {report.get('feature_drift_score')} | {report.get('label_drift_score')} | {report.get('overall_source_risk_score')} | {report.get('drift_grade')} |")
    return "\n".join(lines) + "\n"


def strategy_markdown(payload: dict) -> str:
    lines = ["# Source Strategy Ablation Report", "", "## Plain-English Summary", "This report lists controlled recovery strategies. Current source-holdout already acts as the exclude-source ablation. Stable source-holdout can restore production-candidate status, but no model is marked production-ready in this pass.", "", "| Model | Strategy | Excluded Sources | Normal Metric | Holdout Metric | Worst Source | Drop | Status After Gates | Improves Production Status | Notes |", "|---|---|---|---:|---:|---|---:|---|---|---|"]
    for row in payload.get("strategies", []):
        lines.append(f"| {row.get('model')} | {row.get('strategy')} | {', '.join(row.get('sources_excluded') or [])} | {row.get('normal_chronological_metric')} | {row.get('source_holdout_metric')} | {row.get('worst_source')} | {row.get('drop')} | {row.get('production_status_after_gates')} | {row.get('production_status_improves')} | {row.get('risk_notes')} |")
    lines += ["", "## Recovery Recommendations"]
    for model, rec in payload.get("recommendations", {}).items():
        lines.append(f"- `{model}`: {rec}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
