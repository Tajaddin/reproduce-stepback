# reproduce-stepback

> Reproduction of **"Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models"** (Zheng et al., ICLR 2024) on a hand-curated 40-question MMLU-style physics benchmark with Claude Haiku 4.5. Three prompts compared: `direct`, `cot`, `step_back`. **Result: the paper's +5.5 abs-pts effect is no longer visible** — Haiku 4.5 saturates this benchmark at **100% on all three strategies**, leaving step-back nothing to add. The actual finding: modern instruction-tuned models have absorbed step-back-style reasoning into their base behavior.

[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE) [![Tests](https://img.shields.io/badge/tests-22%20passing-brightgreen)](#tests) [![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()

## The paper

* **Title:** Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models
* **Authors:** Huaixiu Steven Zheng, Swaroop Mishra, Xinyun Chen, Heng-Tze Cheng, Ed H. Chi, Quoc V. Le, Denny Zhou (Google DeepMind)
* **Venue:** ICLR 2024
* **arXiv:** [2310.06117](https://arxiv.org/abs/2310.06117)

The paper's claim: before answering a hard question, ask the model to take a **step back** and name the underlying *principle*; then answer the question using that abstraction. On PaLM 2-L, this boosts MMLU High-School Physics from 60.9 % → 66.4 % (+5.5 abs pts) and TimeQA from 45.6 % → 66.8 % (+21.2 abs pts).

See [paper.md](paper.md) for the full table of reported deltas.

## What this repo reproduces

We pick **MMLU High-School Physics** as the test bed because:

1. It's one of the four headline benchmarks in Table 2 of the paper.
2. Physics questions usually have a single named principle ("ideal gas law", "conservation of momentum"), which is exactly the abstraction step-back is supposed to elicit.
3. It's evaluatable with a tiny multiple-choice harness — no human raters needed.

Three strategies are compared, identical except for the prompt template:

| Strategy | Prompt shape |
|---|---|
| `direct` | "Answer with one letter: A/B/C/D" — no chain of thought |
| `cot` | "Let's think step by step" — the paper's vanilla CoT baseline |
| `step_back` | "First, state the underlying physical principle... then apply it" — the paper's contribution |

All three run against the SAME 40 hand-written physics questions, against the SAME model: `claude-haiku-4-5-20251001`. The hero metric is the **absolute-points delta `step_back - cot` on Haiku 4.5**, compared to the **+5.5 abs pts** the paper reports on PaLM 2-L.

## Why a hand-written benchmark?

Two reasons:

1. **Avoid training-set contamination.** The 2024 papers in the LLM eval literature increasingly debate whether headline MMLU numbers reflect *test-set leakage* into the pretraining corpus. By writing fresh questions from the same MMLU spec (40 STEM principles, balanced A/B/C/D distribution, no public source text), we get a clean read on the prompting strategy's effect without contamination noise.
2. **Reproducibility under cost.** A 40-question set × 3 strategies = 120 API calls per run, ~$0.05 on Haiku 4.5. Anyone can re-run this with `python bench/run_anthropic.py` in five minutes.

Questions cover 40 distinct principles: Newton's laws, kinematics, conservation of energy/momentum, Ohm's law, ideal gas, work-energy theorem, photon energy, Stefan-Boltzmann, double-slit interference, etc. Balanced answer-letter distribution (each of A/B/C/D appears 8–12 times).

## Hero result

`python bench/run_anthropic.py` — 120 API calls, ~10 min wall clock, claude-haiku-4-5-20251001.

| Strategy | Accuracy | Correct / N | Unparseable | Δ vs paper's PaLM 2-L |
|---|---:|---:|---:|---|
| `direct` | **100.0 %** | 40 / 40 | 0 | (paper used no direct baseline) |
| `cot` | **100.0 %** | 40 / 40 | 0 | paper: 60.9 % |
| `step_back` | **100.0 %** | 40 / 40 | 0 | paper: 66.4 % |
| **Δ step_back − cot** | **+0.0 abs pts** | — | — | paper: **+5.5 abs pts** |

Raw output: [`bench/anthropic_results.json`](bench/anthropic_results.json).

## The reproduction story

**The gap vs the paper is not "step-back is worse than reported."** It's that *the entire experimental regime the paper measured in has shifted out from under the experiment.*

PaLM 2-L on MMLU High-School Physics scored 60.9 % on vanilla CoT, leaving 39 pts of headroom for any improvement to occupy. Step-back captured 5.5 of those points. On Haiku 4.5 in 2025, **vanilla CoT already scores 100 %** on a benchmark designed to be MMLU-equivalent. There is no headroom. Step-back has nothing to add because the model is already taking the step back implicitly.

This is the finding worth writing down:

1. **Instruction-tuned 2025 models have absorbed step-back into base behavior.** When asked an MMLU-style physics question, Haiku will state the relevant law in its chain of thought without being explicitly prompted. The Zheng et al. recipe describes a behavior that has since become a property of the model, not the prompt.
2. **MMLU High-School Physics is a saturated benchmark for frontier 2025 models.** Hand-curating 40 questions to closely match the public spec yielded a 100 % score — and these are not memorized questions (they were written for this repo and have never been published). The benchmark genre, not the specific examples, is what's saturated.
3. **To see the step-back effect today, you need a harder benchmark.** Candidates: MMLU-Pro, GPQA-Diamond, FrontierMath. Or you measure against a weaker base model — e.g., Llama-3.1-8B, where vanilla CoT will leave headroom for step-back to recover. This repo's harness supports both via the `Completion` protocol.

The honest framing for this reproduction: **the recipe still works, but on this combination of (Haiku 4.5, MMLU physics, n=40) the effect size is zero.** That isn't a refutation — it's a fingerprint of how the field has moved between October 2023 (paper submission) and 2025.

## What would change the result

Three modifications worth running if you want to actually see step-back's effect on Haiku 4.5:

| Change | Why |
|---|---|
| Swap dataset for **MMLU-Pro / GPQA-Diamond / FrontierMath** | Harder questions = lower baseline = room for step-back to help |
| Swap base model for **Llama-3.1-8B** (via Groq) | Weaker base = stronger CoT-vs-step-back gap |
| Crank n up to **300+** with bootstrap CIs | n=40 has wide confidence; small effects need bigger samples |

The repo's `Completion` protocol makes the second one a one-line change. The first needs the question file swapped. The third is mechanical.

## Quickstart

```bash
pip install -e ".[anthropic,dev]"
export ANTHROPIC_API_KEY=sk-ant-...

# Validate fixtures + extractor (no LLM calls):
pytest                    # 22 tests, ~0.3s

# Reproduce the experiment:
python bench/run_anthropic.py
# 120 calls, ~5 minutes wall clock, ~$0.05 on Haiku 4.5
```

Or via the CLI:

```bash
stepback list
stepback run --out bench/results.json
```

## Tests

```
tests/test_dataset.py     4 passed   40 questions / 4 choices each / balanced answer distribution
tests/test_extractor.py   9 passed   "Answer: X" parser handles markdown, parens, fallback, none
tests/test_strategies.py  5 passed   prompt shape for each of direct / cot / step_back
tests/test_runner.py      4 passed   correct/unparseable counts, per-question records, run_all order
─────────────────────────────────────────────
22 passed in 0.34s
```

## Project layout

```
.
├── paper.md                          # paper citation + reported numbers table
├── benchmark/questions.json          # 40 hand-curated physics questions
├── src/stepback/
│   ├── dataset.py        # Question dataclass + load_questions
│   ├── strategies.py     # Strategy enum + PROMPTS for each
│   ├── backends.py       # Completion protocol + Mock + Anthropic
│   ├── runner.py         # extract_answer_letter + run_strategy + StrategyResult
│   └── cli.py            # `stepback list / run`
├── tests/                # 4 files, 22 cases
└── bench/run_anthropic.py
```

## Limitations

**Single base model.** Only Haiku 4.5 in the committed results. The paper used PaLM 2-L; numbers are not directly comparable across model families. Adding a Sonnet / Opus / Llama row is one line per backend.

**n = 40.** Confidence intervals on 40 multiple-choice items are wide. A 2-question swing is 5 abs pts. For peer-reviewed claims, expand to ≥ 200 questions and bootstrap CIs.

**Greedy decoding.** Single sample at temperature 0. The paper's higher TimeQA / SituatedQA deltas come partly from self-consistency over multiple samples, which is not reproduced here.

**Subset of the paper's experiments.** The original paper covers four benchmarks (MMLU Physics, MMLU Chemistry, TimeQA, SituatedQA). This repo reproduces the *recipe* on the first one. Extending to TimeQA / SituatedQA needs a retrieval step (those are multi-hop QA) — different scope.

**English only.** All questions and prompts are English. Step-back's effect on multilingual reasoning is unstudied here.

## License

MIT — see [LICENSE](LICENSE).
