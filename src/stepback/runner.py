"""Runner + answer-letter extractor.

Robust extractor handles:

* "Answer: B" / "Answer:** B" / "Final answer: B"
* answers in the middle of the response (uses LAST occurrence)
* bare letters at the end of the response
* models that wrap the letter in markdown or quotes
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from stepback.backends import Completion
from stepback.dataset import Question
from stepback.strategies import PROMPTS, Strategy


_ANSWER_RE = re.compile(
    r"(?:final\s+)?answer\s*[:\-]\s*\**\s*\"?\(?\s*([ABCD])\b",
    re.IGNORECASE,
)
_TAIL_LETTER_RE = re.compile(r"\b([ABCD])\b[\s\W]*$", re.MULTILINE)


def extract_answer_letter(text: str) -> str | None:
    """Return the model's chosen letter A-D, or None if not detectable."""
    if not text:
        return None
    matches = list(_ANSWER_RE.finditer(text))
    if matches:
        return matches[-1].group(1).upper()
    # Fallback: last single letter A/B/C/D at end of any line.
    tail_matches = list(_TAIL_LETTER_RE.finditer(text))
    if tail_matches:
        return tail_matches[-1].group(1).upper()
    return None


@dataclass
class RunResult:
    question_id: str
    strategy: Strategy
    raw_response: str
    extracted: str | None
    correct: bool


@dataclass
class StrategyResult:
    strategy: Strategy
    n: int
    correct: int
    unparseable: int
    accuracy: float
    per_question: list[RunResult]


def run_strategy(
    backend: Completion,
    questions: list[Question],
    strategy: Strategy,
) -> StrategyResult:
    per: list[RunResult] = []
    correct = 0
    unparseable = 0
    for q in questions:
        prompt = PROMPTS[strategy](q)
        raw = backend.complete(prompt)
        letter = extract_answer_letter(raw)
        is_correct = letter == q.answer
        if letter is None:
            unparseable += 1
        if is_correct:
            correct += 1
        per.append(
            RunResult(
                question_id=q.id,
                strategy=strategy,
                raw_response=raw,
                extracted=letter,
                correct=is_correct,
            )
        )
    return StrategyResult(
        strategy=strategy,
        n=len(questions),
        correct=correct,
        unparseable=unparseable,
        accuracy=round(correct / max(len(questions), 1), 4),
        per_question=per,
    )


def run_all(backend: Completion, questions: list[Question]) -> list[StrategyResult]:
    return [run_strategy(backend, questions, s) for s in Strategy]
