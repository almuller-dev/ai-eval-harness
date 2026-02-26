"""
#########################################
##      created by: Al Muller
##       filename: eval_harness/metrics.py
#########################################
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator
from rapidfuzz.distance import Levenshtein


@dataclass(frozen=True)
class MetricOutcome:
    """Normalized metric result with pass/fail state, score, and details."""

    passed: bool
    score: float
    details: dict[str, Any]


def exact_label(pred: str, expected_label: str) -> MetricOutcome:
    """Score case-insensitive exact label matches."""
    p = pred.strip().lower()
    e = expected_label.strip().lower()
    passed = p == e
    return MetricOutcome(
        passed=passed,
        score=1.0 if passed else 0.0,
        details={"pred": p, "expected": e},
    )


def json_schema_match(pred: str, schema: dict[str, Any]) -> MetricOutcome:
    """Parse model output as JSON and validate it against a provided schema."""
    raw = pred.strip()

    try:
        obj = json.loads(raw)
    except Exception as e:
        # small partial credit if it's close to JSON (heuristic)
        # (edit distance to "{}" isn't perfect but keeps things simple)
        dist = Levenshtein.distance(raw[:200], "{}")
        score = max(0.0, 0.2 - min(0.2, dist / 1000))
        return MetricOutcome(
            False,
            float(score),
            {
                "error": "invalid_json",
                "exception": str(e),
                "raw": raw[:400],
            },
        )

    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(obj), key=lambda x: x.path)

    if errors:
        return MetricOutcome(
            False,
            0.0,
            {
                "error": "schema_failed",
                "schema_errors": [e.message for e in errors[:5]],
                "obj": obj,
            },
        )

    return MetricOutcome(True, 1.0, {"obj": obj})
