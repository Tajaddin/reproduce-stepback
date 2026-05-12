"""Hand-curated 40-question MMLU-style physics benchmark."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Question:
    id: str
    principle: str
    question: str
    choices: dict[str, str]
    answer: str  # "A" | "B" | "C" | "D"


def _benchmark_dir() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        cand = parent / "benchmark"
        if cand.is_dir() and (cand / "questions.json").is_file():
            return cand
    raise FileNotFoundError("benchmark/ not found")


def load_questions() -> list[Question]:
    raw = json.loads((_benchmark_dir() / "questions.json").read_text(encoding="utf-8"))
    return [
        Question(
            id=q["id"],
            principle=q["principle"],
            question=q["question"],
            choices=q["choices"],
            answer=q["answer"],
        )
        for q in raw
    ]
