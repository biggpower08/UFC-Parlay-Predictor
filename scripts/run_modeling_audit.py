from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the UFC/MMA modeling audit workflow.")
    parser.add_argument("--input-dir", default="data/imports")
    parser.add_argument("--include-mentor-silver", action="store_true")
    parser.add_argument("--mentor-zip", default="")
    parser.add_argument("--include-github", action="store_true")
    parser.add_argument("--include-expert-signals", action="store_true")
    parser.add_argument("--benchmark", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--fail-on-high-risk-leakage", action="store_true")
    parser.add_argument("--output-dir", default="ufc_predictor/data/processed")
    parser.add_argument("--docs-dir", default="docs")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    docs_dir = Path(args.docs_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(parents=True, exist_ok=True)

    steps = []
    steps.append(_run_step("leakage_scan", [sys.executable, "scripts/scan_data_leakage.py", "--input-dir", args.input_dir, "--output", str(output_dir / "leakage_report.json"), "--markdown-output", str(docs_dir / "leakage_report.md")], args.verbose))
    steps.append(_run_step("import_training_dataset", [sys.executable, "scripts/import_training_dataset.py", "--input-dir", args.input_dir], args.verbose))
    audit_cmd = [
        sys.executable,
        "scripts/audit_training_data.py",
        "--input-dir",
        args.input_dir,
        "--output",
        str(output_dir / "data_audit_report.json"),
        "--markdown-output",
        str(docs_dir / "data_audit_report.md"),
    ]
    if args.include_mentor_silver:
        audit_cmd.append("--include-mentor-silver")
        if args.mentor_zip:
            audit_cmd.extend(["--mentor-zip", args.mentor_zip])
    steps.append(_run_step("training_data_audit", audit_cmd, args.verbose))
    steps.append(_run_step("training_dataset_dry_run", [sys.executable, "scripts/build_training_dataset.py", "--source", "imported_csv", "--dry-run", "--missingness-report"], args.verbose))

    if args.benchmark:
        steps.append(_run_step("winner_silver_benchmark_audit", [sys.executable, "scripts/train_winner_model.py", "--source", "silver", "--dry-run", "--split", "chronological"], args.verbose, allow_failure=True))
        steps.append(_run_step("prop_training_plan", [sys.executable, "scripts/train_prop_models.py", "--source", "imported_csv", "--dry-run"], args.verbose))
        steps.append(_run_step("benchmark_report", [sys.executable, "scripts/benchmark_training_models.py", "--output", str(output_dir / "model_benchmark_report.json"), "--markdown-output", str(docs_dir / "model_benchmark_report.md")], args.verbose))
        steps.append(_run_step("segment_evaluation", [sys.executable, "scripts/evaluate_model_segments.py", "--output", str(output_dir / "segment_evaluation_report.json"), "--markdown-output", str(docs_dir / "segment_evaluation_report.md")], args.verbose))

    validation = _validate_registry(output_dir / "model_benchmark_report.json")
    leakage_risk = _leakage_risk(output_dir / "leakage_report.json")
    summary = {
        "steps": steps,
        "registry_validation": validation,
        "leakage_risk": leakage_risk,
        "final_summary_table": _summary_table(output_dir / "model_benchmark_report.json", output_dir / "data_audit_report.json"),
        "notes": _notes(args),
    }
    summary_path = output_dir / "modeling_audit_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, default=str), encoding="utf-8")
    markdown_path = docs_dir / "modeling_audit_summary.md"
    markdown_path.write_text(_markdown(summary), encoding="utf-8")
    print(json.dumps({"summary": str(summary_path), "markdown": str(markdown_path), "steps": steps}, indent=2, default=str))

    hard_failures = [step for step in steps if step["returncode"] != 0 and not step.get("allowed_failure")]
    if hard_failures:
        return 1
    if args.fail_on_high_risk_leakage and leakage_risk.get("high_risk_review_needed"):
        return 3
    return 0


def _run_step(name: str, command: list[str], verbose: bool, allow_failure: bool = False) -> dict:
    completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False)
    if verbose or completed.returncode != 0:
        if completed.stdout:
            print(completed.stdout)
        if completed.stderr:
            print(completed.stderr, file=sys.stderr)
    return {
        "name": name,
        "command": _display_command(command),
        "returncode": completed.returncode,
        "allowed_failure": allow_failure,
        "stdout_tail": completed.stdout[-2000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def _display_command(command: list[str]) -> str:
    return " ".join(command)


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _validate_registry(benchmark_path: Path) -> dict:
    benchmark = _read_json(benchmark_path, {"models": []})
    required = {"model", "status", "rows_used", "main_metric", "baseline", "beats_baseline", "leakage_risk", "runtime_compatible", "notes"}
    missing = {}
    for row in benchmark.get("models", []):
        gaps = sorted(required - set(row))
        if gaps:
            missing[row.get("model", "unknown")] = gaps
    return {"valid": not missing, "missing_fields": missing}


def _leakage_risk(path: Path) -> dict:
    report = _read_json(path, {})
    counts: dict[str, int] = {}
    for item in report.get("reports", []):
        for label, count in item.get("summary", {}).items():
            counts[label] = counts.get(label, 0) + int(count)
    return {
        "classification_counts": counts,
        "high_risk_review_needed": bool(counts.get("unknown_review_needed", 0)),
        "note": "Leakage columns in raw files are expected; the key is excluding them from features.",
    }


def _summary_table(benchmark_path: Path, audit_path: Path) -> list[dict]:
    benchmark = _read_json(benchmark_path, {})
    if benchmark.get("models"):
        return benchmark["models"]
    audit = _read_json(audit_path, {})
    rows = []
    for model, status in audit.get("model_readiness", {}).items():
        rows.append(
            {
                "model": model,
                "status": status.get("status"),
                "rows_used": status.get("rows", 0),
                "main_metric": None,
                "baseline": None,
                "beats_baseline": None,
                "leakage_risk": "unknown_review_needed",
                "runtime_compatible": model not in {"winner_model", "odds_calibration_model", "expert_signal_model"},
                "notes": status.get("reason", ""),
            }
        )
    return rows


def _notes(args) -> list[str]:
    notes = [
        "Raw Kaggle/GitHub/manual/expert files are training inputs only and must not be committed.",
        "Supabase remains the production database; deployed runtime should use Supabase plus small bundled artifacts.",
    ]
    if args.include_github:
        notes.append("GitHub dataset support is local-folder only in this pass; no live GitHub download is required.")
    if args.include_expert_signals:
        notes.append("Expert signal support requires pre-fight timestamp verification before training.")
    return notes


def _markdown(summary: dict) -> str:
    lines = [
        "# Modeling Audit Summary",
        "",
        "## Steps",
    ]
    for step in summary["steps"]:
        status = "ok" if step["returncode"] == 0 else "failed"
        if step.get("allowed_failure") and step["returncode"] != 0:
            status = "allowed failure"
        lines.append(f"- `{step['name']}`: {status}")
    lines.extend(
        [
            "",
            "## Final Summary Table",
            "",
            "| Model | Status | Rows Used | Main Metric | Baseline | Beats Baseline | Leakage Risk | Runtime Compatible | Notes |",
            "|---|---|---:|---:|---:|---|---|---|---|",
        ]
    )
    for row in summary.get("final_summary_table", []):
        lines.append(
            "| {model} | {status} | {rows_used} | {main_metric} | {baseline} | {beats_baseline} | {leakage_risk} | {runtime_compatible} | {notes} |".format(
                **{key: _cell(row.get(key)) for key in ("model", "status", "rows_used", "main_metric", "baseline", "beats_baseline", "leakage_risk", "runtime_compatible", "notes")}
            )
        )
    return "\n".join(lines).strip() + "\n"


def _cell(value):
    if value is None:
        return ""
    return str(value).replace("|", "/")


if __name__ == "__main__":
    raise SystemExit(main())
