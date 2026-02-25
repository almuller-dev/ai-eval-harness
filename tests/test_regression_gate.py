import pytest

from eval_harness.regression_gate import evaluate_regression


def test_regression_gate_passes_within_budget() -> None:
    ok, drop = evaluate_regression(
        current_pass_rate=0.88,
        baseline_pass_rate=0.90,
        max_drop=0.03,
    )
    assert ok is True
    assert drop == pytest.approx(0.02)


def test_regression_gate_fails_over_budget() -> None:
    ok, drop = evaluate_regression(
        current_pass_rate=0.85,
        baseline_pass_rate=0.90,
        max_drop=0.03,
    )
    assert ok is False
    assert drop == pytest.approx(0.05)
