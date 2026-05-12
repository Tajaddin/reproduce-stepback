"""Sanity checks on the 40-question benchmark."""

from __future__ import annotations

from stepback import load_questions


def test_load_questions_returns_40():
    qs = load_questions()
    assert len(qs) == 40


def test_each_question_has_four_choices_and_valid_answer():
    for q in load_questions():
        assert set(q.choices.keys()) == {"A", "B", "C", "D"}, q.id
        assert q.answer in {"A", "B", "C", "D"}, q.id
        assert q.principle, q.id
        assert q.question, q.id


def test_no_duplicate_ids():
    ids = [q.id for q in load_questions()]
    assert len(ids) == len(set(ids))


def test_answer_distribution_is_balanced():
    """Avoid leaking a "guess C" baseline by accident."""
    from collections import Counter
    counts = Counter(q.answer for q in load_questions())
    # each letter should appear at least 4 times across 40 questions
    for letter in "ABCD":
        assert counts[letter] >= 4, f"{letter} only used {counts[letter]} times"
    # ... and no single letter dominates
    assert max(counts.values()) <= len(load_questions()) // 2
