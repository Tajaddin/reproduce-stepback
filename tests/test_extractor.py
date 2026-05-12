"""extract_answer_letter unit tests."""

from __future__ import annotations

from stepback import extract_answer_letter


def test_explicit_answer_colon():
    assert extract_answer_letter("Answer: B") == "B"


def test_answer_in_middle_picks_last():
    text = "Answer: A — wait, let me reconsider.\nAnswer: C"
    assert extract_answer_letter(text) == "C"


def test_lowercase_letter_normalized():
    assert extract_answer_letter("answer: d") == "D"


def test_answer_with_markdown_bold():
    assert extract_answer_letter("**Answer:** C") == "C"


def test_final_answer_phrasing():
    assert extract_answer_letter("Final Answer: A") == "A"


def test_answer_with_parens_and_quotes():
    assert extract_answer_letter('Answer: "(B)"') == "B"


def test_bare_letter_at_end_fallback():
    text = "Long reasoning paragraph here.\nThe correct option is\n\nC\n"
    assert extract_answer_letter(text) == "C"


def test_no_letter_returns_none():
    assert extract_answer_letter("I cannot answer.") is None


def test_empty_string_returns_none():
    assert extract_answer_letter("") is None
