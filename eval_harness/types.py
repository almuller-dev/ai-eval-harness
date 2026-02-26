"""
#########################################
##      created by: Al Muller
##       filename: eval_harness/types.py
#########################################
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TaskType = Literal["label", "json"]


class DatasetRow(BaseModel):
    """One dataset example with task metadata and expected outputs."""

    id: str
    task: TaskType
    input: str
    expected: dict[str, Any]


class EvalResult(BaseModel):
    """Row-level evaluation outcome produced by runner metrics."""

    row_id: str
    task: TaskType
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    details: dict[str, Any] = Field(default_factory=dict)


class RunSummary(BaseModel):
    """Aggregate summary for a single dataset evaluation run."""

    dataset_path: str
    model: str
    total: int
    passed: int
    pass_rate: float
    avg_score: float
    results: list[EvalResult]
    notes: str | None = None
