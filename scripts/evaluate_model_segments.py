from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings


SEGMENTS = [
    "mens_heavyweight",
    "mens_lightweight",
    "womens_strawweight",
    "womens_flyweight",
    "same_division",
    "cross_division",
    "catchweight",
    "odds_available",
    "odds_missing",
    "high_confidence",
    "low_confidence",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate model metrics by segment when row-level benchmark outputs exist.")
    parser.add_argument("--benchmark", default=str(settings.DATA_PROCESSED_DIR / "model_benchmark_report.json"))
    parser.add_argument("--output", default=str(settings.DATA_PROCESSED_DIR / "segment_evaluation_report.json"))
    parser.add_argument("--markdown-output", default="docs/segment_evaluation_report.md")
    args = parser.parse_args()

    benchmark = _read_json(Path(args.benchmark), {"models": []})
    models = []
    for row in benchmark.get("models", []):
        models.append(
            {
                "model": row.get("model"),
                "segment_metrics_available": False,
                "segments_expected": SEGMENTS,
                "reason": "Row-level validation predictions with segment labels are not saved yet.",
            }
        )
    payload = {"models": models}
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    markdown_path = Path(args.markdown_output)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(_markdown(models), encoding="utf-8")
    print(json.dumps({"output": str(output), "markdown_output": str(markdown_path), "models": len(models)}, indent=2))
    return 0


def _read_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def _markdown(models: list[dict]) -> str:
    lines = [
        "# Segment Evaluation Report",
        "",
        "Segment metrics are not available until benchmark scripts save row-level validation predictions with segment labels.",
        "",
    ]
    for model in models:
        lines.append(f"- `{model['model']}`: {model['reason']}")
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
