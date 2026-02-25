from __future__ import annotations

from pathlib import Path


def load_prompt(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def render(template: str, *, input_text: str) -> str:
    return template.replace("{{input}}", input_text)
