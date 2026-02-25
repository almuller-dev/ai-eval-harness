from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_report(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _dataset_label(report: dict) -> str:
    dataset_path = str(report.get("dataset_path", ""))
    if dataset_path:
        return Path(dataset_path).stem
    return "unknown"


def build_markdown(reports: list[dict]) -> str:
    lines: list[str] = []
    lines.append("## Eval CI Summary")
    lines.append("")
    lines.append("| Dataset | Passed | Pass Rate | Avg Score |")
    lines.append("|---|---:|---:|---:|")

    for report in reports:
        dataset = _dataset_label(report)
        passed = int(report.get("passed", 0))
        total = int(report.get("total", 0))
        pass_rate = float(report.get("pass_rate", 0.0))
        avg_score = float(report.get("avg_score", 0.0))
        lines.append(f"| `{dataset}` | {passed}/{total} | {pass_rate:.2%} | {avg_score:.3f} |")

    lines.append("")
    lines.append("### Failures")

    any_failure = False
    for report in reports:
        dataset = _dataset_label(report)
        failures = [r for r in report.get("results", []) if not r.get("passed", False)]
        if not failures:
            continue

        any_failure = True
        lines.append(f"- `{dataset}`")
        for failure in failures[:5]:
            row_id = failure.get("row_id", "unknown")
            task = failure.get("task", "unknown")
            score = float(failure.get("score", 0.0))
            lines.append(f"  - `{row_id}` ({task}) score={score:.2f}")

    if not any_failure:
        lines.append("- None")

    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--reports", nargs="+", required=True)
    ap.add_argument("--out", default="reports/pr_comment.md")
    args = ap.parse_args()

    loaded = [_read_report(path) for path in args.reports]
    markdown = build_markdown(loaded)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
