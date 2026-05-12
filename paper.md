# Paper

**Take a Step Back: Evoking Reasoning via Abstraction in Large Language Models.**
Huaixiu Steven Zheng, Swaroop Mishra, Xinyun Chen, Heng-Tze Cheng, Ed H. Chi, Quoc V. Le, Denny Zhou. ICLR 2024. ([arXiv:2310.06117](https://arxiv.org/abs/2310.06117))

## Key claim

Before answering a specific question, ask the model a **"step-back" question** that captures the underlying *concept* or *principle*. Use that abstraction as context for the final answer.

Headline reported numbers (Table 2, PaLM 2-L):

| Benchmark | Vanilla CoT | Step-Back | Δ (abs pts) |
|---|---:|---:|---:|
| MMLU High-School Physics | 60.9 | 66.4 | **+5.5** |
| MMLU High-School Chemistry | 60.4 | 65.6 | **+5.2** |
| TimeQA | 45.6 | 66.8 | **+21.2** |
| SituatedQA | 47.5 | 60.7 | **+13.2** |

The paper attributes the gain to two failure modes that step-back addresses:
1. The model loses sight of the *principle* needed (e.g., "ideal gas law") and gets distracted by surface details.
2. Multi-hop retrieval questions benefit from first identifying the abstraction "before/after which event" rather than the literal timestamps.

## What this repo measures

We pick the cleanest single-result reproduction: **MMLU High-School Physics-style questions** on a hand-curated 40-question set. The benchmark questions are written from the same MMLU spec but composed independently so we can verify that the model doesn't have memorized answers.

We compare three prompts against **claude-haiku-4-5-20251001**:

* `direct` — just the question + "Answer:"
* `cot` — "Think step by step." (the paper's vanilla CoT baseline)
* `step_back` — "First, identify the key principle... then answer." (the paper's recipe)

The hero metric is the **absolute-points gap between step-back and CoT on Haiku 4.5**, and how that gap compares to the **+5.5** the paper reports on PaLM 2-L.
