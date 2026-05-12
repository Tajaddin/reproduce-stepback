"""Three prompting strategies.

* ``DIRECT``   — no chain of thought; the paper's baseline ablation.
* ``COT``      — "Let's think step by step." (the paper's vanilla CoT baseline.)
* ``STEP_BACK`` — first ask a step-back question that names the principle,
                  then answer the original. The paper's main contribution.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from stepback.backends import Completion
from stepback.dataset import Question


class Strategy(str, enum.Enum):
    DIRECT = "direct"
    COT = "cot"
    STEP_BACK = "step_back"


def _format_choices(q: Question) -> str:
    return "\n".join(f"{k}) {v}" for k, v in q.choices.items())


def _prompt_direct(q: Question) -> str:
    return (
        f"Question: {q.question}\n\n"
        f"{_format_choices(q)}\n\n"
        "Answer with exactly one letter: A, B, C, or D. "
        "Format your final answer as 'Answer: <letter>'."
    )


def _prompt_cot(q: Question) -> str:
    return (
        f"Question: {q.question}\n\n"
        f"{_format_choices(q)}\n\n"
        "Let's think step by step. After your reasoning, give the final answer "
        "as 'Answer: <letter>' on its own line."
    )


_STEP_BACK_INSTRUCTION = (
    "Before answering, first take a STEP BACK and identify the high-level "
    "physical principle or concept the question is testing. State the principle "
    "in one sentence under a 'Principle:' header. Then apply that principle to "
    "the specific values in the question and reach your final answer.\n\n"
    "Format your reply as:\n"
    "Principle: <one sentence naming the law or concept>\n"
    "Reasoning: <work the problem step by step>\n"
    "Answer: <one letter A/B/C/D>"
)


def _prompt_step_back(q: Question) -> str:
    return (
        f"Question: {q.question}\n\n"
        f"{_format_choices(q)}\n\n"
        f"{_STEP_BACK_INSTRUCTION}"
    )


PROMPTS: dict[Strategy, "callable[[Question], str]"] = {
    Strategy.DIRECT: _prompt_direct,
    Strategy.COT: _prompt_cot,
    Strategy.STEP_BACK: _prompt_step_back,
}
