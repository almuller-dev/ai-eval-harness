"""
#########################################
##      created by: Al Muller
##       filename: eval_harness/prompts.py
#########################################
"""

from __future__ import annotations

from pathlib import Path


def load_prompt(path: str) -> str:
    """Load a prompt template file from disk."""
    return Path(path).read_text(encoding="utf-8")


def render(template: str, *, input_text: str) -> str:
    """Render prompt template placeholders with row input text."""
    return template.replace("{{input}}", input_text)
