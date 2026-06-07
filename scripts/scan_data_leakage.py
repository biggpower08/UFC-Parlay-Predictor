from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ufc_predictor.config import settings
from ufc_predictor.training.leakage import scan_dataframe


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan CSV columns for pre-fight training leakage risks.")
    parser.add_argument("--input-dir", default="data/imports/kaggle")
    parser.add_argument("--output", default=str(settings.DATA_PROCESSED_DIR / "leakage_report.json"))
    parser.add_argument("--markdown-output", default="docs/leakage_report.md")
    parser.add_argument("--max-rows", type=int, default=1000)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    reports = []
    for path in sorted(input_dir.rglob("*.csv")) if input_dir.exists() else []:
        try:
            frame = pd.read_csv(path, nrows=args.max_rows)
            report = scan_dataframe(frame)
            report["file"] = str(path)
            report["rows_sampled"] = int(len(frame))
            reports.append(report)
        except Exception as exc:  # noqa: BLE001 - audit script should report, not crash on one file.
            reports.append({"file": str(path), "error": str(exc)})

    payload = {
        "input_dir": str(input_dir),
        "files_scanned": len(reports),
        "reports": reports,
    }
    output = Path(args.output)
    _write_text(output, json.dumps(payload, indent=2, default=str))
    markdown = _markdown(payload)
    markdown_path = Path(args.markdown_output)
    _write_text(markdown_path, markdown)
    print(json.dumps({"output": str(output), "markdown_output": str(markdown_path), "files_scanned": len(reports)}, indent=2))
    return 0


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f"{path.name}.tmp")
    tmp_path.write_text(text, encoding="utf-8")
    tmp_path.replace(path)


def _markdown(payload: dict) -> str:
    lines = [
        "# Leakage Report",
        "",
        f"Input folder: `{payload['input_dir']}`",
        f"Files scanned: {payload['files_scanned']}",
        "",
    ]
    for report in payload["reports"]:
        lines.append(f"## {report.get('file')}")
        if report.get("error"):
            lines.append(f"- Error: {report['error']}")
            lines.append("")
            continue
        lines.append(f"- Columns: {report.get('column_count')}")
        lines.append(f"- Summary: `{json.dumps(report.get('summary', {}), sort_keys=True)}`")
        blocked = report.get("blocked_feature_columns", [])
        if blocked:
            preview = ", ".join(blocked[:20])
            suffix = " ..." if len(blocked) > 20 else ""
            lines.append(f"- Blocked/label-only columns: {preview}{suffix}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
