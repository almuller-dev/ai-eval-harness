"""
#########################################
##      created by: Al Muller
##       filename: tests/test_ci_summary.py
#########################################
"""

from eval_harness.ci_summary import build_markdown


def test_build_markdown_includes_failure_details() -> None:
    reports = [
        {
            "dataset_path": "datasets/classification.jsonl",
            "passed": 2,
            "total": 3,
            "pass_rate": 2 / 3,
            "avg_score": 0.67,
            "results": [
                {"row_id": "c1", "task": "label", "passed": True, "score": 1.0},
                {"row_id": "c2", "task": "label", "passed": False, "score": 0.0},
            ],
        }
    ]

    out = build_markdown(reports)
    assert "`classification`" in out
    assert "`c2` (label) score=0.00" in out
