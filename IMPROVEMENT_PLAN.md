# Improvement plan

## What changes
- Rewrite README in spartan voice. Strip em dashes, banned words, AI-style phrasing. Keep the negative-result framing as the template for the rest of the portfolio.
- Pin every dependency to an exact version. No ranges.
- Add `.github/workflows/ci.yml` running pytest on Python 3.10 / 3.11 / 3.12.
- Add CI status badge to README once the workflow lands on main.
- Add an architecture diagram (ASCII) showing question file -> strategies -> backend -> extractor -> scorer.
- Add a "Caveats" section with the same content as "Limitations" but in the active voice the rest of the README uses.
- Add a small `scripts/check_questions.py` integrity check so the benchmark's invariants live in CI, beyond the pytest suite.

## Why
- README has em dashes, banned filler words, and rhetorical setup phrases. Style rules forbid all three.
- Deps are unpinned (`>=` ranges). CI reproducibility breaks on minor releases.
- No CI workflow. A senior engineer scanning the repo sees no green badge.
- The negative-result framing is strong but buried under prose. Pull it to the top.
- The hero numbers come from `bench/anthropic_results.json` already. No code changes needed for the bench itself.

## Out of scope
- Adding new strategies, models, or datasets. The repo's job is one paper, one finding.
- Changing the question set. 40 hand-written items is the agreed scope.
