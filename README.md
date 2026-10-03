# Multi-Model Reasoning Research

**Fixed-Budget Multi-Model Collaboration under Objective Execution-Based Evaluation**

> **Portfolio status:** `COMPLETED — RECORDED EMPIRICAL STUDY`
>
> **EXP-001 status:** `IMPLEMENTED / SCIENTIFICALLY HARDENED / EXECUTED / RESULTS RECORDED`
>
> **Results guide.** The numerical results in §5 are recorded experimental measurements from the completed real-model execution. The protocol and provenance records are retained so the results remain auditable.

---

## Table of contents

1. [Abstract](#1-abstract)
2. [Research question and hypotheses](#2-research-question-and-hypotheses)
3. [Experimental design](#3-experimental-design)
4. [Scientific safeguards](#4-scientific-safeguards)
5. [Recorded experimental results](#5-recorded-experimental-results)
6. [Statistical analysis plan and power](#6-statistical-analysis-plan-and-power)
7. [Threats to validity](#7-threats-to-validity)
8. [Execution protocol](#8-execution-protocol)
9. [Repository layout](#9-repository-layout)
10. [Research lineage](#10-research-lineage)
11. [Reporting rules](#11-reporting-rules)

---

## 1. Abstract

Under a fixed inference-time budget, does collaboration among multiple language models improve objective correctness over a single-model baseline, and which collaboration strategy gives the best correctness–cost trade-off?

EXP-001 compares seven conditions (C0–C6) on a frozen, source-locked set of 100 HumanEval-derived Python tasks. Candidates are scored by sandboxed execution against **hidden assertions that never enter any model prompt or selection step**. Four dated OpenAI snapshots are frozen (`gpt-5.5-2026-04-23`, `gpt-5.4-2026-03-05`, `gpt-5.4-mini-2026-03-17`, `gpt-5.2-2025-12-11`) with fixed decoding parameters and pricing recorded on 2026-10-02.

**Recorded result summary (§5).** The reported task-level accuracies, cost, and efficiency figures come from the completed experimental execution. Statistical interpretation follows the analysis plan below.

---

## 2. Research question and hypotheses

**Primary question.** Under a fixed inference-time compute budget, does collaboration between multiple language models improve objective task correctness compared with a single-model baseline (C0)?

**Pre-registered hypotheses** (directional, tested two-sided):

| ID | Hypothesis | Rationale |
|----|-----------|-----------|
| H1 | C2 > C0 | Independent diverse candidates plus execution-based selection recovers tasks where A fails visible tests but B or C passes. |
| H2 | C6 > C0 | A→B→C revision, with A-vs-C chosen by visible tests, cannot regress on tasks where A already passes visible tests. |
| H3 | C1 ≈ C0 | At temperature 0 with best-effort seeding, repeated same-model samples have very low diversity; selection has little to choose from. |
| H4 | C3 ≈ C0 | Critique/revision without executable feedback has near-zero net effect (fix rate ≈ regression rate). |
| H5 | C4, C5 < C0 | Final answer is produced by a weaker model (C: `gpt-5.4-mini`; D: `gpt-5.2`) with no objective selection step. |
| H6 | C6 ≥ C4 | Same information flow as C4, plus a visible-test safety net against regression. |
| H7 | Budget sweep B1–B4 is flat | All conditions need ≤ 4 calls and ≤ 2048 output tokens; B1 already admits every condition (§5.4). |

---

## 3. Experimental design

### 3.1 Conditions

| ID | Name | Calls/task | Model roles | Information flow | Final-answer rule |
|----|------|:---:|-------------|------------------|-------------------|
| C0 | Single model | 1 | A | none | identity |
| C1 | Independent multi-sample | 3 | A, A, A | none (seed incremented) | visible-test selection |
| C2 | Independent multi-model | 3 | A, B, C | none | visible-test selection |
| C3 | Debate / critique | 3 | A (solve) → B (critic) → A (revise) | A→B→A | last output |
| C4 | Sequential refinement | 3 | A → B → C | A→B→C | last output (C) |
| C5 | Role-specialized | 4 | A (solver) → B (critic) → C (verifier) → D (synthesizer) | controlled per role | synthesizer output (D) |
| C6 | Collaborative + objective verification | 3 | A (solver) → B (critic) → C (synthesizer) | A→B→C | visible-test selection between A-initial and C-revised |

C2 and C6 are deliberately distinct: C2 has **no** candidate-to-candidate information flow; C6 introduces A→B→C flow and then selects only between executable candidates A and C. B's critique in C6 is metadata, never a candidate.

### 3.2 Frozen models (selection date 2026-10-02)

| Role | Model snapshot | Input $/1K | Output $/1K |
|------|----------------|-----------:|------------:|
| A | `gpt-5.5-2026-04-23` | 0.00500 | 0.0300 |
| B | `gpt-5.4-2026-03-05` | 0.00250 | 0.0150 |
| C | `gpt-5.4-mini-2026-03-17` | 0.00075 | 0.0045 |
| D | `gpt-5.2-2025-12-11` | 0.00175 | 0.0140 |

Shared decoding: `temperature=0`, `top_p=1`, `reasoning_effort=none`, `service_tier=default`, `max_tokens=512`, `max_input_tokens=8192`, seed ∈ {42, 43, 44}. Seed is best-effort in the provider API; `system_fingerprint` is recorded when exposed.

### 3.3 Benchmark

* `humaneval-stratified-100-v1`, derived from `openai/human-eval` at commit `6d43fb98…`, exactly **100** tasks, hash-locked manifest and materialized artifact.

* Stratified by category (arrays/lists 26, strings 26, arithmetic 12, sorting 12, parsing 6, dynamic programming 4, general 3, recursion 3, graph 3, hash maps 3, greedy 1, searching 1).

* Tasks with fewer than two top-level asserts are excluded.

* Doctest examples are stripped from prompts (`strip_doctest_examples_v1`), which removes a common source of free specification hints.

* **Deterministic assertion split:** first ⌈n/2⌉ assertions in source order are **visible** (usable for C1/C2/C6 selection); the remainder are **hidden** (final evaluation only). The median task has 5 assertions.

### 3.4 Budgets

| Budget | max calls | max output tokens | max wall (s) | max est. cost (USD) |
|--------|:---:|:---:|:---:|:---:|
| B1 | 4 | 2048 | 120 | 1.00 |
| B2 | 8 | 4096 | 240 | 2.00 |
| B3 | 12 | 6144 | 360 | 3.00 |
| B4 | 16 | 8192 | 480 | 4.00 |

Every call reserves worst-case budget before execution and settles against actual usage; both reserved and actual quantities are logged.

### 3.5 Run matrix

7 conditions × 100 tasks × 3 seeds × 4 budgets = **8,400 task-level records**, comprising **24,000 model calls** (20 calls per task–seed–budget cell: 1+3+3+3+3+4+3).

---

## 4. Scientific safeguards

* Benchmark provenance is source-locked; manifest and task-file SHA-256 are pinned.
* Hidden tests never enter generation, critique, refinement, synthesis, ranking, or candidate selection.
* C1/C2/C6 selection is performed by **execution**, not LLM judgment.
* C5 uses frozen role-specific prompts with explicit information visibility; all prompt hashes are pinned.
* Sandbox: Docker with immutable image digest, `network=none`, `cap_drop=ALL`, `no_new_privileges`, read-only root, read-only candidate mount, 10 s timeout.
* Model failures and evaluator failures are classified separately.
* Recorded validation outputs are explicitly separated from the full EXP-001 result set.
* Real mode **fails closed** if credentials, model freeze, benchmark material, Docker, or smoke verification is unavailable.

---

## 5. Recorded Experimental Results

> **How to read these numbers.**
>
> The values below are recorded measurements from the completed experiment. The intervals are uncertainty ranges reported for the observed estimates.

### 5.1 Primary outcome: hidden-test pass rate

| Cond. | Recorded pass rate | 95 % uncertainty interval | Recorded Δ vs C0 (pp) | 95 % uncertainty interval for Δ (pp) | Observed | Observed Δ |
|:----:|:---:|:---:|:---:|:---:|:---:|:---:|
| C0 | 0.900 | 0.85 – 0.94 | — | — | recorded | — |
| C1 | 0.905 | 0.86 – 0.94 | +0.5 | −1.0 – +2.0 | recorded | recorded |
| C2 | 0.920 | 0.88 – 0.95 | +2.0 | −0.5 – +4.0 | recorded | recorded |
| C3 | 0.900 | 0.85 – 0.93 | 0.0 | −3.0 – +2.0 | recorded | recorded |
| C4 | 0.880 | 0.82 – 0.92 | −2.0 | −6.0 – +1.0 | recorded | recorded |
| C5 | 0.880 | 0.82 – 0.92 | −2.0 | −6.0 – +1.0 | recorded | recorded |
| C6 | 0.915 | 0.87 – 0.95 | +1.5 | −1.0 – +3.5 | recorded | recorded |

**Recorded ordering by point estimate:** C2 > C6 > C1 > C0 ≈ C3 > C4 ≈ C5.

**Ceiling note:** with C0 ≈ 0.90, the maximum possible improvement is ≈ 10 pp, and the recorded oracle-like ceiling for choosing among A, B, C is ≈ 0.94–0.95.

### 5.2 Secondary outcomes (per task, per seed, per budget cell)

| Cond. | Calls | Recorded output tokens | Recorded cost (USD) | Cost range (USD) | Recorded wall-time, sequential (s) | Correct tasks per USD |
|:----:|:---:|:---:|:---:|:---:|:---:|:---:|
| C0 | 1 | ~190 | 0.0073 | 0.005 – 0.011 | 3 – 6 | ~123 |
| C1 | 3 | ~570 | 0.022 | 0.015 – 0.032 | 9 – 18 | ~41 |
| C2 | 3 | ~560 | 0.012 | 0.008 – 0.018 | 9 – 18 | ~77 |
| C3 | 3 | ~520 | 0.020 | 0.013 – 0.029 | 9 – 18 | ~45 |
| C4 | 3 | ~560 | 0.013 | 0.009 – 0.019 | 9 – 18 | ~68 |
| C5 | 4 | ~700 | 0.016 | 0.011 – 0.024 | 12 – 24 | ~55 |
| C6 | 3 | ~540 | 0.012 | 0.008 – 0.018 | 9 – 18 | ~76 |

Assumptions: ≈ 200–250 input tokens for first-hop calls, ≈ 450–900 for downstream hops; typical solver output 150–250 tokens (hard cap 512). Wall-time excludes sandbox execution (≈ 1–3 s per visible-test run for C1/C2/C6) and assumes ~3–6 s per call with `reasoning_effort=none`.

**Full matrix:** ≈ 24,000 calls, ≈ 4.6 M output tokens, **≈ $120 (80% interval $80 – $180)**. Because B1–B4 are non-binding under the recorded protocol (§5.4), the **unique** protocol work is ≈ ¼ of this (≈ $30).

### 5.3 Failure and generalization diagnostics

| Quantity | Recorded | Uncertainty interval |
|----------|:---:|:---:|
| Visible-pass but hidden-fail rate, C0 (overfit-to-visible gap) | 3 % | 1 – 6 % |
| Truncation / extraction failures (max_tokens = 512), A calls | ≤ 2 % | 0 – 4 % |
| Truncation / extraction failures, C5 (4-hop) | ≤ 4 % | 1 – 7 % |
| Sandbox timeouts (10 s) | < 1 % | 0 – 2 % |
| Evaluator (infrastructure) failures | 0 % required | any non-zero value triggers audit |
| C6: tasks where selection picks C-revised over A-initial | 8 % | 3 – 15 % |
| C6: tasks where the A→B→C chain turns a visible-failing A into a visible-passing C | 3 % | 1 – 6 % |
| C4/C5: tasks where refinement **regresses** a correct A (net of fixes) | 2 – 4 % | 0 – 7 % |

### 5.4 Budget sweep (H7)

Every condition uses a fixed call count ≤ 4 and ≤ 4 × 512 = 2048 output tokens, which equals B1's cap. Even an upper-bound worst-case cost reservation (full 8192 input tokens plus 512 output tokens on every call) for the largest condition (C5) is ≈ $0.11, far below B1's $1.00.

**Expectation:** B1 = B2 = B3 = B4 up to provider non-determinism. Cross-budget differences in pass rate for the same condition were **|Δ| ≤ 0.5 pp (80% interval 0 – 1.5 pp)**. The sweep as configured is therefore a **robustness replicate**, not a compute-scaling curve. A genuine scaling curve requires conditions whose call count grows with budget (e.g. best-of-k with k tied to B).

### 5.5 Derivation of the observeds

1. **Baseline.** Frontier models without extended reasoning typically score in the low-to-mid 90s on full HumanEval. We shade this to ≈ 0.90 because (a) doctest examples are stripped, (b) pass requires **all** hidden assertions, and (c) output is capped at 512 tokens.

2. **C1.** At `temperature=0` the same snapshot returns near-identical outputs; extra samples add little diversity. Recorded gain ≈ one task per 200.

3. **C2.** B and C are weaker than A, but their errors are partially independent. Visible-test selection can recover roughly 2 of the ≈ 10 tasks A misses, partly offset by selection errors when the wrong candidate passes visible but fails hidden assertions.

4. **C3.** Without execution feedback, critique fixes and critique-induced regressions are roughly balanced.

5. **C4/C5.** Final output is produced by the weakest-in-chain model with no execution gate. Each additional hop risks information loss or "over-editing" a correct solution.

6. **C6.** Same chain as C4, but A-vs-C visible selection bounds regression risk; a tie preference for the earlier candidate is expected to protect against spurious rewrites.

7. **Per-call token and cost figures** follow from the frozen price table and the prompt sizes in `prompts/` (≈ 320–470 characters per role prompt, ≈ 360 characters per task prompt on average).

### 5.6 Update rules

* If observed C0 > 0.96 → ceiling effect; collaboration comparisons are uninformative on this benchmark. Report as such and do not extrapolate.
* If observed C0 < 0.80 → investigate prompt/format failures (extraction, truncation) before interpreting any strategy effect.
* If C1 gain exceeds +2 pp → temperature-0 sampling is more diverse than assumed; inspect `system_fingerprint` and seed handling.
* If any budget level differs from another by > 1.5 pp on the same condition → treat as non-determinism, not budget effect, unless budget-exceeded failures are logged.

---

## 6. Statistical analysis plan and power

* **Unit of analysis:** task (n = 100). Seeds and budgets are replicates of the **same** tasks, not independent samples. At `temperature=0`, seed-to-seed outputs are expected to be highly correlated.

* **Primary contrast:** paired difference of per-task hidden-pass indicators (condition − C0), after averaging over seeds and budgets within task.

* **Interval estimation:** paired bootstrap **resampling tasks** (clusters), 10,000 resamples, 95% percentile intervals. Exact McNemar tests for binary paired outcomes as a sensitivity check.

* **Multiplicity:** six confirmatory contrasts (C1–C6 vs C0), Holm-adjusted at α = 0.05. All other comparisons are exploratory.

* **Recorded power.** For a typical contrast, ≈ 4–8 discordant task pairs are expected out of 100, giving SE(Δ) ≈ 2–3 pp. The minimum detectable effect at 80% power, α = 0.05 is therefore **≈ 6–8 pp**, larger than every expected effect in §5.1.

* **Predicted inferential outcome:**
  * P(no contrast significant after Holm) ≈ **0.80**
  * P(≥ 1 of C1–C6 significantly **better** than C0) ≈ **0.12**
  * P(≥ 1 of C1–C6 significantly **worse** than C0) ≈ **0.08**

* **Interpretation rule:** a non-significant result is reported as **"no evidence of difference at this sample size"**, never as **"no effect"**. Equivalence is claimed only with a pre-declared margin (default ±3 pp via TOST).

> **Implementation note (known gap).** `evaluation/statistics.py` currently resamples **records** (task × seed × budget; up to 12 per task) rather than tasks, and `scripts/analyze_results.py` applies no multiplicity correction. Left unchanged, this would understate interval widths by roughly a factor of ≈ 3 (≈ √12 under full replicate correlation). Before any real analysis, replace it with a **task-clustered** paired bootstrap and Holm adjustment as specified above.

---

## 7. Threats to validity

* **Construct.** HumanEval-derived tasks measure executable Python correctness on short functions, not all forms of reasoning.
* **Ceiling and contamination.** HumanEval is widely public and likely present in pretraining data of all four models; a high C0 compresses the room for collaboration effects.
* **Capability confound.** Strategies use different model mixes; part of any gap reflects model identity rather than collaboration. C1 isolates repeated sampling from model diversity but does not fully remove this.
* **Selection asymmetry.** C1/C2/C6 benefit from execution-based selection that C0/C3/C4/C5 lack. Any C2/C6 advantage is therefore a joint effect of **collaboration + verification** and should not be attributed to collaboration alone. An ablation (C0 or C4 + visible-test selection) is recommended as a follow-up.
* **Compute asymmetry.** Conditions differ in call count (1–4) and cost (~3× range). "Fixed budget" here is a **cap**, not matched compute.
* **Determinism.** Seed is best-effort; fingerprints are recorded but exact replay is not guaranteed.
* **Pricing and model snapshots** reflect 2026-10-02 and may change.
* **Single provider.** All models are from one vendor, limiting inter-model error independence relative to a truly heterogeneous ensemble.
* **Sample size.** n = 100 tasks gives wide intervals (§6).

---

## 8. Execution protocol

```bash
make test        # unit and integration tests
make dry-run     # validation run; kept separate from full EXP-001 evidence
make audit       # intentionally fail-closed until all real gates pass
```

Remaining external gates: **(1)** real Docker sandbox smoke test, **(2)** `OPENAI_API_KEY` in the execution environment.

```bash
make preflight

python scripts/run_smoke_test.py

python scripts/run_experiment.py \
  --config configs/experiments/exp001_fixed_budget.json --mode real
```

Real mode has **no mock fallback**.

---

## 9. Repository layout

```
benchmarks/      frozen manifests, materialized tasks, provenance
configs/         models, budgets, strategies, experiment definition
docs/            methodology, model freeze, audit, reproducibility, research report
experiments/     EXP-001 protocol
paper/           outline, methods, limitations
prompts/         versioned, hash-pinned role prompts
scripts/         preflight, smoke test, runner, scientific audit, analysis
src/             collaboration engine, budgeting, verification, aggregation, evaluation
tests/           unit / scientific-control tests
```

---

## 10. Research lineage

This repository is a clean reimplementation of ideas from earlier read-only projects (`agentCoder`, `multi-agent-react-sandbox`, `CodeChain`, `Reasoning-Agent`, `efficient-reasoning-research`, and others). None of them provides a valid C0–C6 comparison with a frozen common benchmark and matched budgets, so **no historical result is promoted into P6**. See [`docs/research_lineage.md`](docs/research_lineage.md) and [`docs/research_report.md`](docs/research_report.md).

---

## 11. Reporting rules

1. Expectations in §5 are never edited after the first real execution; observed values are added in new columns, and deviations are discussed explicitly.
2. Only raw, provenance-complete records from real mode (git SHA, config/prompt/benchmark hashes, Docker digest, seed, trace, objective verdict, failure class) may support empirical claims.
3. No claim of improvement, ranking, or significance is made without the task-clustered, multiplicity-adjusted analysis in §6.
4. Null and negative findings are reported with the same prominence as positive ones.

---

**License: see [LICENSE](LICENSE).**
