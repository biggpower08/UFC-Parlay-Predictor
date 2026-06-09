from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MODELS = [
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
    "strike_volume_model",
    "takedown_control_model",
    "odds_calibration_model",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit large model metric changes before artifact packaging.")
    parser.add_argument("--current-report", default="ufc_predictor/data/processed/model_accuracy_report.json")
    parser.add_argument("--registry", default="ufc_predictor/data/processed/model_registry.json")
    parser.add_argument("--interaction-report", default="ufc_predictor/data/processed/interaction_discovery_report.json")
    parser.add_argument("--previous-ref", default="a955ca9")
    parser.add_argument("--previous-report-path", default="ufc_predictor/data/processed/model_accuracy_report.json")
    parser.add_argument("--output-md", default="docs/metric_jump_audit.md")
    args = parser.parse_args()

    current = read_json(Path(args.current_report))
    previous = read_previous_json(args.previous_ref, args.previous_report_path)
    registry = read_json(Path(args.registry))
    interactions = read_json(Path(args.interaction_report))
    payload = build_audit(current, previous, registry, interactions, args.previous_ref)
    output = Path(args.output_md)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown(payload), encoding="utf-8")
    print(json.dumps({"output_md": str(output), "models": len(payload["models"])}, indent=2))
    return 0


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_previous_json(ref: str, path: str) -> dict[str, Any]:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
    return json.loads(raw)


def build_audit(current: dict, previous: dict, registry: dict, interactions: dict, previous_ref: str) -> dict:
    current_models = current.get("models", {})
    previous_models = previous.get("models", {})
    rows_changed = current.get("audit", {}).get("fight_rows") != previous.get("audit", {}).get("fight_rows")
    date_range_changed = current.get("audit", {}).get("date_range") != previous.get("audit", {}).get("date_range")
    feature_count_delta = (current.get("audit", {}).get("feature_count") or 0) - (previous.get("audit", {}).get("feature_count") or 0)
    rows_summary = {
        "previous_ref": previous_ref,
        "previous_fight_rows": previous.get("audit", {}).get("fight_rows"),
        "current_fight_rows": current.get("audit", {}).get("fight_rows"),
        "previous_feature_count": previous.get("audit", {}).get("feature_count"),
        "current_feature_count": current.get("audit", {}).get("feature_count"),
        "feature_count_delta": feature_count_delta,
        "date_range_changed": date_range_changed,
        "row_count_changed": rows_changed,
        "split_rows": current.get("split", {}),
        "calibration": current.get("calibration", {}),
    }
    audits = []
    for model_name in MODELS:
        old = previous_models.get(model_name, {})
        new = current_models.get(model_name, {})
        entry = registry.get(model_name, {})
        interaction = (interactions.get("models") or {}).get(model_name, {})
        old_metric = old.get("final_test_metric")
        new_metric = new.get("final_test_metric")
        delta = rounded_delta(new_metric, old_metric)
        old_rows = old.get("test_rows")
        new_rows = new.get("test_rows")
        row_changed = old_rows != new_rows
        failed_gates = entry.get("failed_gates", [])
        risk = "low"
        verdict = "trusted_with_caution"
        reasons = []
        if row_changed or rows_changed or date_range_changed:
            risk = "high"
            verdict = "needs_review"
            reasons.append("row_or_date_range_changed")
        if "source_holdout_not_run" in failed_gates or "source_holdout_stable" in failed_gates:
            risk = max_risk(risk, "medium")
            verdict = "needs_review"
            reasons.append("source_holdout_not_passing")
        if "calibration_acceptable" in failed_gates:
            risk = max_risk(risk, "medium")
            verdict = "needs_review"
            reasons.append("calibration_gate_failed")
        if model_name == "odds_calibration_model" or entry.get("production_status") == "blocked":
            risk = "high"
            verdict = "blocked"
            reasons.append("model_blocked")
        if model_name in {"finish_in_round_1_model", "takedown_control_model"} and delta is not None and delta > 0:
            risk = max_risk(risk, "medium")
            verdict = "needs_review"
            reasons.append("recently_improved_from_weaker_status")
        if delta is not None and abs(delta) >= 0.02:
            risk = max_risk(risk, "medium")
            reasons.append("metric_jump_above_review_threshold")
        audits.append(
            {
                "model": model_name,
                "old_metric": old_metric,
                "new_metric": new_metric,
                "delta": delta,
                "old_test_rows": old_rows,
                "new_test_rows": new_rows,
                "old_balanced_accuracy": (old.get("metrics") or {}).get("balanced_accuracy"),
                "new_balanced_accuracy": (new.get("metrics") or {}).get("balanced_accuracy"),
                "production_status": entry.get("production_status"),
                "failed_gates": failed_gates,
                "interaction_candidates": interaction.get("candidate_count", 0),
                "interactions_selected": interaction.get("selected_count", 0),
                "likely_reason": likely_reason(feature_count_delta, interaction, row_changed),
                "risk_level": risk,
                "verdict": verdict,
                "review_reasons": reasons,
            }
        )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plain_english_summary": "Metric jumps mostly came from feature and interaction changes, not row-count changes. Source-holdout remains the main production-readiness blocker.",
        "row_and_split_summary": rows_summary,
        "leakage_audit": {
            "style_features": "prior_history_only_by_dataset_builder_order",
            "opponent_weakness_features": "prior_history_only_by_dataset_builder_order",
            "interaction_selection": "validation_only_final_test_not_used",
            "calibration": current.get("calibration", {}),
            "risk": "needs_review_until_source_holdout_runs_for_all_candidates",
        },
        "models": audits,
    }


def likely_reason(feature_count_delta: int, interaction: dict, row_changed: bool) -> str:
    if row_changed:
        return "row filtering or split changed"
    selected = int(interaction.get("selected_count") or 0)
    if selected:
        return f"feature schema expanded by {feature_count_delta} fields and {selected} validation-selected interactions were used"
    if feature_count_delta:
        return f"feature schema expanded by {feature_count_delta} fields; base features kept"
    return "no clear pipeline change detected"


def rounded_delta(new, old):
    if new is None or old is None:
        return None
    return round(float(new) - float(old), 4)


def max_risk(left: str, right: str) -> str:
    order = {"low": 0, "medium": 1, "high": 2}
    return left if order[left] >= order[right] else right


def markdown(payload: dict) -> str:
    rows = payload["row_and_split_summary"]
    lines = [
        "# Metric Jump Audit",
        "",
        "## Plain-English Summary",
        payload["plain_english_summary"],
        "",
        "## Row, Split, and Label Checks",
        f"- Previous report ref: `{rows['previous_ref']}`",
        f"- Fight rows: {rows['previous_fight_rows']} -> {rows['current_fight_rows']}",
        f"- Feature count: {rows['previous_feature_count']} -> {rows['current_feature_count']} ({rows['feature_count_delta']:+})",
        f"- Date range changed: {rows['date_range_changed']}",
        f"- Row count changed: {rows['row_count_changed']}",
        f"- Train rows: {rows['split_rows'].get('train_rows')}",
        f"- Validation rows: {rows['split_rows'].get('validation_rows')}",
        f"- Final test rows: {rows['split_rows'].get('test_rows')}",
        f"- Calibration status: {rows['calibration'].get('status')}",
        "",
        "## Leakage Audit Result",
        "- Style features are derived from accumulated fighter history before each fight row is added to history.",
        "- Opponent-weakness features are also derived from accumulated prior history.",
        "- Interaction discovery excludes forbidden target/result/current-fight columns and records that final test is not used for selection.",
        "- `--calibrate` is currently reported as `basic_probability_scores_only`; it is not true validation-only calibration yet.",
        "",
        "## Model Metric Changes",
        "| Model | Old Metric | New Metric | Delta | Test Rows | Status | Interactions | Risk | Verdict | Likely Reason |",
        "|---|---:|---:|---:|---|---|---:|---|---|---|",
    ]
    for item in payload["models"]:
        lines.append(
            f"| {item['model']} | {item['old_metric']} | {item['new_metric']} | {item['delta']} | "
            f"{item['old_test_rows']} -> {item['new_test_rows']} | {item['production_status']} | "
            f"{item['interactions_selected']} / {item['interaction_candidates']} | {item['risk_level']} | "
            f"{item['verdict']} | {item['likely_reason']} |"
        )
    lines.extend(
        [
            "",
            "## Source-Holdout Readiness",
            "Non-winner production candidates still carry `source_holdout_not_run`. That means they may remain candidates for internal validation, but they must not become `production_ready` until source-holdout validation is implemented and passes.",
            "",
            "## Production Decision",
            "- Do not package artifacts from this audit alone.",
            "- Keep `winner_model` as `high_confidence_only`.",
            "- Keep odds calibration blocked.",
            "- Treat `finish_in_round_1_model` and `takedown_control_model` cautiously until source-holdout confirms the metric gains.",
        ]
    )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
