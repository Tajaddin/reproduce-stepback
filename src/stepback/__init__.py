"""reproduce-stepback: reproduction of Step-Back Prompting (ICLR 2024).

Exports:

* :class:`Question`: one MMLU-style multiple-choice item.
* :func:`load_questions`.
* :func:`extract_answer_letter`.
* :class:`Strategy` enum (DIRECT / COT / STEP_BACK).
* :class:`Completion` Protocol + :class:`MockCompletion` + :class:`AnthropicCompletion`.
* :func:`run_strategy` + :func:`run_all`.
"""

from stepback.backends import AnthropicCompletion, Completion, MockCompletion
from stepback.dataset import Question, load_questions
from stepback.runner import (
    RunResult,
    StrategyResult,
    extract_answer_letter,
    run_all,
    run_strategy,
)
from stepback.strategies import Strategy

__all__ = [
    "AnthropicCompletion",
    "Completion",
    "MockCompletion",
    "Question",
    "RunResult",
    "Strategy",
    "StrategyResult",
    "extract_answer_letter",
    "load_questions",
    "run_all",
    "run_strategy",
]
