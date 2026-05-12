"""runner + StrategyResult integration tests with MockCompletion."""

from __future__ import annotations

from stepback import (
    MockCompletion,
    Strategy,
    load_questions,
    run_all,
    run_strategy,
)


def test_runner_counts_correct_and_unparseable():
    qs = load_questions()[:5]
    call_count = {"n": 0}

    def responder(prompt, system):
        i = call_count["n"]
        call_count["n"] += 1
        if i < 2:
            # first two: correct
            return f"Answer: {qs[i].answer}"
        if i == 2:
            return "I refuse to answer"  # no letter at all => unparseable
        return "Answer: Z"  # invalid letter => unparseable

    mock = MockCompletion(responder=responder)
    res = run_strategy(mock, qs, Strategy.DIRECT)
    assert res.n == 5
    assert res.correct == 2
    assert res.unparseable == 3


def test_run_strategy_returns_per_question_records():
    qs = load_questions()[:3]
    mock = MockCompletion(responder=lambda p, s: f"Answer: A")
    res = run_strategy(mock, qs, Strategy.COT)
    assert len(res.per_question) == 3
    for r, q in zip(res.per_question, qs):
        assert r.question_id == q.id
        assert r.strategy == Strategy.COT


def test_perfect_mock_yields_100pct_accuracy():
    qs = load_questions()[:4]
    answers = iter([q.answer for q in qs])
    mock = MockCompletion(responder=lambda p, s: f"Answer: {next(answers)}")
    res = run_strategy(mock, qs, Strategy.STEP_BACK)
    assert res.accuracy == 1.0
    assert res.correct == 4


def test_run_all_returns_three_results_in_order():
    qs = load_questions()[:2]
    mock = MockCompletion(responder=lambda p, s: "Answer: A")
    results = run_all(mock, qs)
    assert [r.strategy for r in results] == [
        Strategy.DIRECT,
        Strategy.COT,
        Strategy.STEP_BACK,
    ]
