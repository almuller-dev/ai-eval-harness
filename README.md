# AI Eval Harness

A minimal, reproducible evaluation harness for LLM prompt tasks.

## What this repo demonstrates
- Reproducible eval datasets (`.jsonl`)
- CI gating (fail PRs on quality regressions)
- Deterministic unit tests (no API required)
- Optional live LLM eval job in GitHub Actions (runs only when `OPENAI_API_KEY` is set)

## Local dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pytest -q
ruff check . && ruff format --check .

# Live eval (requires OPENAI_API_KEY)
export OPENAI_API_KEY="..."
python -m eval_harness.runner --dataset datasets/classification.jsonl --model gpt-5.2 --min-pass-rate 0.90
```

## GitHub Actions
- `test` job always runs (lint + unit tests)
- `evals` job runs only when repo secrets include `OPENAI_API_KEY`
