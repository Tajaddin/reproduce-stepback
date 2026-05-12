"""Standalone question-set sanity check.

Runs the same invariants as `tests/test_dataset.py` outside of pytest, so a CI
job (or a contributor) verifies the benchmark file in one command.

Exits 0 on success, 1 with a list of problems.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QFILE = ROOT / "benchmark" / "questions.json"


def main() -> int:
    raw = json.loads(QFILE.read_text(encoding="utf-8"))
    problems: list[str] = []

    if len(raw) != 40:
        problems.append(f"expected 40 questions, found {len(raw)}")

    ids = [q["id"] for q in raw]
    if len(set(ids)) != len(ids):
        dups = [k for k, n in Counter(ids).items() if n > 1]
        problems.append(f"duplicate ids: {dups}")

    for q in raw:
        keys = set(q.get("choices", {}).keys())
        if keys != {"A", "B", "C", "D"}:
            problems.append(f"{q['id']}: choices must be A/B/C/D, got {sorted(keys)}")
        if q.get("answer") not in {"A", "B", "C", "D"}:
            problems.append(f"{q['id']}: answer must be A/B/C/D, got {q.get('answer')!r}")
        if not q.get("principle"):
            problems.append(f"{q['id']}: principle is empty")
        if not q.get("question"):
            problems.append(f"{q['id']}: question is empty")

    counts = Counter(q["answer"] for q in raw)
    for letter in "ABCD":
        if counts[letter] < 4:
            problems.append(f"answer letter {letter} used only {counts[letter]} times (min 4)")

    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print(f"ok: {len(raw)} questions, balanced answers {dict(counts)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
