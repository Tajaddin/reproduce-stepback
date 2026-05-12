"""Real Haiku 4.5 reproduction of step-back vs CoT vs direct."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from stepback import AnthropicCompletion, load_questions, run_all


OUT = Path(__file__).resolve().parent / "anthropic_results.json"


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    except Exception:
        pass

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 2

    backend = AnthropicCompletion()
    questions = load_questions()
    print(f"model={backend.model}, n={len(questions)}, strategies=3")

    results = run_all(backend, questions)

    direct = next(r for r in results if r.strategy.value == "direct")
    cot = next(r for r in results if r.strategy.value == "cot")
    step = next(r for r in results if r.strategy.value == "step_back")

    out = {
        "model": backend.model,
        "n_questions": len(questions),
        "strategies": [
            {
                "strategy": r.strategy.value,
                "accuracy": r.accuracy,
                "correct": r.correct,
                "unparseable": r.unparseable,
                "wrong_ids": [p.question_id for p in r.per_question if not p.correct],
            }
            for r in results
        ],
        "deltas": {
            "step_back_vs_cot_abs_pts": round((step.accuracy - cot.accuracy) * 100, 2),
            "step_back_vs_direct_abs_pts": round((step.accuracy - direct.accuracy) * 100, 2),
            "cot_vs_direct_abs_pts": round((cot.accuracy - direct.accuracy) * 100, 2),
        },
        "paper_reference_palm2_l": {
            "mmlu_hs_physics_cot_pct": 60.9,
            "mmlu_hs_physics_step_back_pct": 66.4,
            "delta_abs_pts": 5.5,
        },
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))
    print(f"\nwrote {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
