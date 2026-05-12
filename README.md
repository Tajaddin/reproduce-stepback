# reproduce-stepback

Reproduction of Zheng et al., "Take a Step Back" (ICLR 2024). On a hand-curated 40-question MMLU-style physics set, Claude Haiku 4.5 scores 100 % on every strategy, so the paper's +5.5-abs-pt step-back effect collapses to +0.0.

[![ci](https://github.com/Tajaddin/reproduce-stepback/actions/workflows/ci.yml/badge.svg)](https://github.com/Tajaddin/reproduce-stepback/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](pyproject.toml)

## Why this exists

The paper reports a +5.5-abs-pt accuracy gain from step-back prompting on PaLM 2-L's MMLU High-School Physics. Two years later, modern instruction-tuned models look like a different population. This repo runs the recipe against Claude Haiku 4.5 on a fresh 40-question set and reports the gap.

## Results

Run: `python bench/run_anthropic.py`, 120 API calls, ~10 min wall clock, ~$0.05.

| Strategy | Accuracy | Correct / N | Unparseable | Paper (PaLM 2-L) |
|---|---:|---:|---:|---:|
| direct | 100.0 % | 40 / 40 | 0 | (no direct baseline) |
| cot | 100.0 % | 40 / 40 | 0 | 60.9 % |
| step_back | 100.0 % | 40 / 40 | 0 | 66.4 % |
| Δ step_back − cot | +0.0 abs pts | | | +5.5 abs pts |

Raw output: [bench/anthropic_results.json](bench/anthropic_results.json).

## Reading the result

The gap is not "step-back is worse than reported." The experimental regime the paper measured in has shifted out from under the experiment. PaLM 2-L scored 60.9 % on vanilla CoT, leaving 39 pts of headroom. Haiku 4.5 hits 100 % zero-shot, so step-back has nothing to add. The recipe still works. On this combination of (Haiku 4.5, MMLU physics, n=40), the effect size is zero. The result is a fingerprint of how the field moved between October 2023 (paper submission) and 2025, not a refutation.

Three claims fall out of the data:

- Frontier 2025 instruction-tuned models name the underlying principle inside vanilla CoT without being prompted. The recipe became a property of the model.
- MMLU-style physics, even rewritten fresh, no longer separates frontier models. The benchmark genre is the issue, not the specific items.
- To see the effect today, swap to a harder set (MMLU-Pro, GPQA-Diamond, FrontierMath) or a weaker model (Llama-3.1-8B via Groq). The `Completion` protocol takes either swap in one line.

## What would change the result

Three modifications restore measurable headroom for step-back to fill:

| Change | Why it works |
|---|---|
| Swap dataset for MMLU-Pro / GPQA-Diamond / FrontierMath | Harder items lower the vanilla-CoT baseline, leaving room for step-back to recover. |
| Swap base model for Llama-3.1-8B via Groq | A weaker base widens the CoT-vs-step-back gap. |
| Raise n to 300+ with bootstrap CIs | n=40 has wide confidence. Small effects need bigger samples to detect. |

The first needs `benchmark/questions.json` replaced. The second is a one-line change behind the `Completion` protocol. The third is mechanical (rerun the loop).

## How to run

```bash
pip install -e ".[anthropic,dev]"
export ANTHROPIC_API_KEY=sk-ant-...

# fixtures + extractor, no API calls
pytest

# 120 API calls
python bench/run_anthropic.py

# CLI
stepback list
stepback run --out bench/results.json
```

## Architecture

```
benchmark/questions.json
        |
        v
  load_questions()
        |
        v
  strategies.PROMPTS[Strategy]  ----  Completion (Mock | Anthropic)
        |                                     |
        +-------------- prompt ---------------+
                                              |
                                              v
                                  extract_answer_letter
                                              |
                                              v
                            score vs Question.answer
                                              |
                                              v
                          StrategyResult, RunResult
                                              |
                                              v
                          bench/anthropic_results.json
```

Three strategies share one runner. Each strategy emits a different prompt, the same backend protocol replies, the same regex extracts the letter, the same scorer compares against ground truth.

## Why a hand-written benchmark

Two reasons:

- Avoid training-set contamination. The 40 items follow the MMLU spec but were written for this repo and never published, so memorisation does not explain the 100 % score.
- Reproducibility under cost. 40 questions × 3 strategies = 120 API calls per run, ~$0.05 on Haiku 4.5.

The set covers 40 distinct principles (Newton's laws, kinematics, conservation of energy and momentum, Ohm's law, ideal gas, work-energy, photon energy, Stefan-Boltzmann, double-slit interference, and so on). Answer-letter distribution is A:4, B:15, C:16, D:5. Skew exists but no letter dominates past 50 % and every letter appears at least 4 times. The integrity check (`scripts/check_questions.py`) runs in CI.

## Tests

```
tests/test_dataset.py     4 passed   40 questions, 4 choices each, balanced answers, unique ids
tests/test_extractor.py   9 passed   "Answer: X" parser handles markdown, parens, fallback, none
tests/test_strategies.py  5 passed   prompt shape for direct / cot / step_back
tests/test_runner.py      4 passed   correct/unparseable counts, per-question records, run_all order
=============================================
22 passed in 0.34s
```

## Caveats

- One base model. Only Haiku 4.5 in the committed run. PaLM 2-L is unavailable, so the comparison is across model families, not a like-for-like run.
- n = 40. A 2-question swing is 5 abs pts. For peer-reviewed claims, expand to 200+ items and bootstrap CIs.
- Greedy decoding, temperature 0, single sample. The paper's larger TimeQA / SituatedQA deltas use self-consistency over multiple samples. Not reproduced here.
- One benchmark out of four. The paper covers MMLU Physics, MMLU Chemistry, TimeQA, SituatedQA. This repo reproduces the recipe on the first. TimeQA / SituatedQA need a retrieval step.
- English only. Multilingual reasoning is out of scope.

## Project layout

```
.
├── paper.md                          # citation + paper's reported numbers table
├── benchmark/questions.json          # 40 hand-curated MMLU-style physics items
├── scripts/check_questions.py        # standalone integrity check, runs in CI
├── src/stepback/
│   ├── dataset.py                    # Question dataclass + load_questions
│   ├── strategies.py                 # Strategy enum + PROMPTS per strategy
│   ├── backends.py                   # Completion Protocol + Mock + Anthropic
│   ├── runner.py                     # extract_answer_letter + run_strategy + StrategyResult
│   └── cli.py                        # `stepback list / run`
├── tests/                            # 4 files, 22 cases
└── bench/run_anthropic.py            # the 120-call hero run, writes anthropic_results.json
```

## License

MIT. See [LICENSE](LICENSE).
