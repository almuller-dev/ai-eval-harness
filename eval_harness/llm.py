"""
#########################################
##      created by: Al Muller
##       filename: eval_harness/llm.py
#########################################
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Protocol

from openai import OpenAI


class LLMClient(Protocol):
    """Protocol for text-generation clients used by eval execution code."""

    def generate(self, *, prompt: str, model: str) -> str: ...


@dataclass
class OpenAIResponsesClient:
    """
    Minimal OpenAI client using the Responses API.
    Docs/examples: client.responses.create(...).output_text
    """

    api_key: str | None = None

    def __post_init__(self) -> None:
        self._client = OpenAI(api_key=self.api_key or os.getenv("OPENAI_API_KEY"))

    def generate(self, *, prompt: str, model: str) -> str:
        resp = self._client.responses.create(
            model=model,
            input=prompt,
        )
        return (resp.output_text or "").strip()
