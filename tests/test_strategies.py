"""Strategy / prompt shape tests."""

from __future__ import annotations

from stepback.dataset import Question
from stepback.strategies import PROMPTS, Strategy


def _q():
    return Question(
        id="t1",
        principle="x",
        question="What is 2 + 2?",
        choices={"A": "3", "B": "4", "C": "5", "D": "6"},
        answer="B",
    )


def test_direct_prompt_has_question_and_choices():
    p = PROMPTS[Strategy.DIRECT](_q())
    assert "What is 2 + 2?" in p
    assert "A) 3" in p and "B) 4" in p


def test_cot_prompt_mentions_step_by_step():
    p = PROMPTS[Strategy.COT](_q())
    assert "step by step" in p.lower()


def test_step_back_prompt_mentions_principle():
    p = PROMPTS[Strategy.STEP_BACK](_q())
    assert "principle" in p.lower()
    assert "step back" in p.lower() or "step-back" in p.lower() or "Principle:" in p


def test_step_back_prompt_demands_structured_output():
    p = PROMPTS[Strategy.STEP_BACK](_q())
    assert "Principle:" in p
    assert "Reasoning:" in p
    assert "Answer:" in p


def test_all_three_strategies_defined():
    assert set(PROMPTS.keys()) == {
        Strategy.DIRECT,
        Strategy.COT,
        Strategy.STEP_BACK,
    }
