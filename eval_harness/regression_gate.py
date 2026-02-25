"""Baseline regression gate utilities for CI quality budget enforcement."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _read_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_regression(
    *,
    current_pass_rate: float,
    baseline_pass_rate: float,
    max_drop: float,
) -> tuple[bool, float]:
    drop = baseline_pass_rate - current_pass_rate
    allowed_drop = max(0.0, max_drop)
    return drop <= allowed_drop, drop


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--report-json", required=True)
    ap.add_argument("--baseline-json", default="baselines/eval_baseline.json")
    ap.add_argument(
        "--dataset-key",
        required=True,
        help="Baseline key (for example: classification, extraction)",
    )
    ap.add_argument(
        "--max-drop",
        type=float,
        default=0.03,
        help="Maximum allowed pass-rate drop (absolute, e.g. 0.03 = 3%).",
    )
    args = ap.parse_args()

    report = _read_json(args.report_json)
    baseline = _read_json(args.baseline_json)

    if args.dataset_key not in baseline:
        raise SystemExit(f"FAIL: dataset key '{args.dataset_key}' missing from baseline")

    current_pass_rate = float(report.get("pass_rate", 0.0))
    baseline_pass_rate = float(baseline[args.dataset_key].get("pass_rate", 0.0))

    ok, drop = evaluate_regression(
        current_pass_rate=current_pass_rate,
        baseline_pass_rate=baseline_pass_rate,
        max_drop=args.max_drop,
    )

    if not ok:
        raise SystemExit(
            "FAIL: regression budget exceeded for "
            f"{args.dataset_key}: current={current_pass_rate:.2%}, "
            f"baseline={baseline_pass_rate:.2%}, drop={drop:.2%}, "
            f"allowed={max(0.0, args.max_drop):.2%}"
        )

    print(
        "OK: regression gate passed for "
        f"{args.dataset_key}: current={current_pass_rate:.2%}, "
        f"baseline={baseline_pass_rate:.2%}, drop={drop:.2%}, "
        f"allowed={max(0.0, args.max_drop):.2%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
