"""Main evaluation execution pipeline and report generation entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean

from .llm import LLMClient, OpenAIResponsesClient
from .metrics import exact_label, json_schema_match
from .prompts import load_prompt, render
from .types import DatasetRow, EvalResult, RunSummary

PROMPT_MAP = {
    "label": "eval_harness/prompts/classify.md",
    "json": "eval_harness/prompts/extract_json.md",
}


def load_dataset(path: str) -> list[DatasetRow]:
    """Load newline-delimited JSON dataset rows into validated models."""
    rows: list[DatasetRow] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(DatasetRow.model_validate_json(line))
    return rows


def evaluate_row(client: LLMClient, *, model: str, row: DatasetRow) -> EvalResult:
    """Evaluate one dataset row with the configured model and task metric."""
    template = load_prompt(PROMPT_MAP[row.task])
    prompt = render(template, input_text=row.input)
    pred = client.generate(prompt=prompt, model=model)

    if row.task == "label":
        expected_label = row.expected["label"]
        out = exact_label(pred, expected_label)

    elif row.task == "json":
        schema = row.expected["schema"]
        out = json_schema_match(pred, schema)

    else:
        raise ValueError(f"Unsupported task: {row.task}")

    return EvalResult(
        row_id=row.id,
        task=row.task,
        passed=out.passed,
        score=out.score,
        details=out.details,
    )


def run_eval(*, dataset_path: str, model: str, client: LLMClient) -> RunSummary:
    """Run all evaluations for a dataset and aggregate pass-rate statistics."""
    rows = load_dataset(dataset_path)
    results = [evaluate_row(client, model=model, row=r) for r in rows]
    passed = sum(1 for r in results if r.passed)
    scores = [r.score for r in results] or [0.0]

    return RunSummary(
        dataset_path=dataset_path,
        model=model,
        total=len(results),
        passed=passed,
        pass_rate=passed / max(1, len(results)),
        avg_score=float(mean(scores)),
        results=results,
    )


def write_reports(summary: RunSummary, *, json_path: str, md_path: str) -> None:
    """Write machine-readable JSON and markdown summary reports."""
    Path(json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(md_path).parent.mkdir(parents=True, exist_ok=True)

    Path(json_path).write_text(summary.model_dump_json(indent=2), encoding="utf-8")

    lines = []
    lines.append("# Eval Report\n")
    lines.append(f"- Dataset: `{summary.dataset_path}`")
    lines.append(f"- Model: `{summary.model}`")
    lines.append(f"- Passed: **{summary.passed}/{summary.total}**")
    lines.append(f"- Pass rate: **{summary.pass_rate:.2%}**")
    lines.append(f"- Avg score: **{summary.avg_score:.3f}**\n")
    lines.append("## Failures\n")
    failures = [r for r in summary.results if not r.passed]
    if not failures:
        lines.append("_None_")
    else:
        for r in failures:
            details = json.dumps(r.details)[:300]
            lines.append(f"- `{r.row_id}` ({r.task}) -> score={r.score:.2f} details={details}")
    Path(md_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    """CLI entrypoint for executing an eval run with optional CI gating."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="Path to a .jsonl dataset")
    ap.add_argument("--model", default="gpt-5.2", help="Model name")
    ap.add_argument("--out-json", default="reports/report.json")
    ap.add_argument("--out-md", default="reports/report.md")
    ap.add_argument("--min-pass-rate", type=float, default=0.90)
    args = ap.parse_args()

    client = OpenAIResponsesClient()

    summary = run_eval(dataset_path=args.dataset, model=args.model, client=client)
    write_reports(summary, json_path=args.out_json, md_path=args.out_md)

    # CI gate
    if summary.pass_rate < args.min_pass_rate:
        raise SystemExit(
            f"FAIL: pass_rate {summary.pass_rate:.2%} < min_pass_rate {args.min_pass_rate:.2%}"
        )

    print(f"OK: pass_rate {summary.pass_rate:.2%} (min {args.min_pass_rate:.2%})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
