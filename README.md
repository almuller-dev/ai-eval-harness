# AI Eval Harness

A minimal, reproducible evaluation harness for LLM prompt tasks.

## What this repo demonstrates
- Reproducible eval datasets (`.jsonl`)
- CI gating (fail PRs on quality regressions)
- Deterministic unit tests (no API required)
- Optional live LLM eval job in GitHub Actions (runs only when `OPENAI_API_KEY` is set)
- Baseline regression budgets (fail when pass-rate drops beyond allowed deltas)
- Automatic PR comments with eval summary and failures

## Local dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pytest -q
ruff check . && ruff format --check .

# Live eval (requires OPENAI_API_KEY)
export OPENAI_API_KEY="..."
python -m eval_harness.runner --dataset datasets/classification.jsonl --model gpt-5.2 --min-pass-rate 0.90

# Baseline regression gate example
python -m eval_harness.regression_gate --report-json reports/classification.json --baseline-json baselines/eval_baseline.json --dataset-key classification --max-drop 0.03
```

## GitHub Actions
- `test` job always runs (lint + unit tests)
- `evals` job runs only when repo secrets include `OPENAI_API_KEY`
- `evals` enforces baseline regression budgets from `baselines/eval_baseline.json`
- `evals` posts or updates a PR comment with dataset pass rates and failure rows
