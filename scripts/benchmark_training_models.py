from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings


def main() -> int:
    parser = argparse.ArgumentParser(description="Summarize current model benchmark/readiness results.")
    parser.add_argument("--audit", default=str(settings.DATA_PROCESSED_DIR / "data_audit_report.json"))
    parser.add_argument("--registry", default=str(settings.MODEL_REGISTRY_JSON))
    parser.add_argument("--metrics", default=str(settings.PROP_MODEL_METRICS_JSON))
    parser.add_argument("--output", default=str(settings.DATA_PROCESSED_DIR / "model_benchmark_report.json"))
    parser.add_argument("--markdown-output", default="docs/model_benchmark_report.md")
    args = parser.parse_args()

    audit = _read_json(Path(args.audit), {})
    registry = _read_json(Path(args.registry), {})
    metrics = _read_json(Path(args.metrics), {})
    rows = []
    model_names = set(registry) | set(audit.get("model_readiness", {})) | set(metrics)
    if "round_model" in model_names:
        # The current trained round model uses round-phase labels; keep one canonical row.
        model_names.discard("round_phase_model")
    for model_name in sorted(model_names):
        entry = registry.get(model_name, {})
        readiness = audit.get("model_readiness", {}).get(model_name, {})
        if model_name == "round_model" and not readiness:
            readiness = audit.get("model_readiness", {}).get("round_phase_model", {})
        metric_entry = metrics.get(model_name, {})
        validation = metric_entry.get("metrics", {}).get("validation") or entry.get("metrics") or {}
        baseline = metric_entry.get("metrics", {}).get("majority_class_baseline") or entry.get("baseline_metrics") or {}
        main_metric = validation.get("accuracy")
        baseline_metric = baseline.get("accuracy")
        beats_baseline = None
        if main_metric is not None and baseline_metric is not None:
            beats_baseline = float(main_metric) > float(baseline_metric)
        rows.append(
            {
                "model": model_name,
                "status": entry.get("status") or readiness.get("status") or metric_entry.get("status") or "not_trained",
                "rows_used": entry.get("rows_used") or readiness.get("rows") or 0,
                "main_metric": main_metric,
                "baseline": baseline_metric,
                "beats_baseline": beats_baseline,
                "leakage_risk": entry.get("leakage_risk") or ("moderate_risk" if model_name == "winner_model" else "unknown_review_needed"),
                "runtime_compatible": entry.get("runtime_compatible", False),
                "notes": _notes(entry, readiness, metric_entry),
            }
        )

    payload = {"models": rows}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    markdown_path = Path(args.markdown_output)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_markdown(rows), encoding="utf-8")
    print(json.dumps({"output": str(output), "markdown_output": str(markdown_path), "models": rows}, indent=2, default=str))
    return 0


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _notes(entry: dict, readiness: dict, metric_entry: dict) -> str:
    limitations = entry.get("limitations") or []
    if limitations:
        return limitations[0]
    if readiness.get("reason"):
        return readiness["reason"]
    if metric_entry.get("reason"):
        return metric_entry["reason"]
    return ""


def _markdown(rows: list[dict]) -> str:
    lines = [
        "# Model Benchmark Report",
        "",
        "| Model | Status | Rows Used | Main Metric | Baseline | Beats Baseline | Leakage Risk | Runtime Compatible | Notes |",
        "|---|---:|---:|---:|---:|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {model} | {status} | {rows_used} | {main_metric} | {baseline} | {beats_baseline} | {leakage_risk} | {runtime_compatible} | {notes} |".format(
                **{key: _cell(value) for key, value in row.items()}
            )
        )
    return "\n".join(lines).strip() + "\n"


def _cell(value):
    if value is None:
        return ""
    return str(value).replace("|", "/")


if __name__ == "__main__":
    raise SystemExit(main())
