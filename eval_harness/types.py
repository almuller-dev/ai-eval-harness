"""Pydantic models for datasets, row-level results, and evaluation summaries."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TaskType = Literal["label", "json"]


class DatasetRow(BaseModel):
    id: str
    task: TaskType
    input: str
    expected: dict[str, Any]


class EvalResult(BaseModel):
    row_id: str
    task: TaskType
    passed: bool
    score: float = Field(ge=0.0, le=1.0)
    details: dict[str, Any] = Field(default_factory=dict)


class RunSummary(BaseModel):
    dataset_path: str
    model: str
    total: int
    passed: int
    pass_rate: float
    avg_score: float
    results: list[EvalResult]
    notes: str | None = None
