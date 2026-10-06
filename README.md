# Multi-Model Reasoning Research

**Fixed-Budget Multi-Model Collaboration under Objective Execution-Based Evaluation**

**Portfolio role.** A cross-model collaboration study: its C0–C6 semantics are local to this repository and are not a replication of the C0–C6 labels in other portfolio projects.

> **Portfolio status:** `COMPLETED — RECORDED EMPIRICAL STUDY`
>
> **EXP-001 status:** `IMPLEMENTED / INTERNALLY AUDITED / EXECUTED / RESULTS RECORDED`
>
> **Results guide.** The public README retains the experimental protocol and recorded-study status. Task-level raw results are not committed publicly, so unreconciled aggregate numerical tables are intentionally omitted.

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

**Recorded study status.** The repository records a completed empirical C0–C6 study under the frozen protocol. The public repository does not commit the task-level raw result archive, so aggregate accuracy/cost/efficiency values are intentionally omitted from this public summary until they can be independently reconciled from source rows.

**Research-positioning boundary.** P6 is adjacent to prior work on repeated sampling, automatic verification, critique/refinement, and multi-agent collaboration, including [Large Language Monkeys](https://arxiv.org/abs/2407.21787), [Self-Refine](https://arxiv.org/abs/2303.17651), and [test-time compute scaling](https://arxiv.org/abs/2408.03314). P6 does **not** claim novelty for those individual mechanisms. Its project-level contribution is the frozen, common comparison of seven collaboration conditions under one execution-based evaluation protocol. It is also not the same experiment as `efficient-reasoning-research`: the two repositories use different model freezes, condition semantics, and protocol/provenance records. They should not be treated as independent replications.

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

7 conditions × 100 tasks × 3 seeds × 4 budgets = **8,400 task-level records**. The public repository does not expose the task-level execution archive, so an aggregate observed model-call total is intentionally not reported here.

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

## 5. Recorded Experimental Study

The repository records a completed C0–C6 multi-model collaboration study under the frozen protocol described above.

The public repository does **not** contain the task-level raw EXP-001 result archive. Because several headline percentages in the historical summary cannot be independently reconstructed from the public task/seed structure without those rows, the aggregate numerical result tables and derived rankings are intentionally omitted from this public README.

What remains established here is the experimental design: seven conditions, frozen model snapshots, fixed call/token ceilings, visible-test selection where specified, hidden-test-only final evaluation, and task-level paired statistical analysis.

**Evidence boundary:** this README documents the recorded study and its protocol; it does not claim that the omitted aggregate values can be independently recomputed from the public repository.

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

> **Inference-code note.** The current helper scripts are retained as implementation/reproducibility infrastructure and are not the provenance source for the recorded summary table in §5. The current analysis implementation now aggregates/bootstraps at the **task** level, and paired confirmatory contrasts report Holm-adjusted p-values. The recorded study values and uncertainty table are preserved as reported study results; future re-analysis should use the same task-clustered/Holm procedure.

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

For a fresh reproduction, the remaining external gates are: **(1)** real Docker sandbox smoke test, **(2)** `OPENAI_API_KEY` in the execution environment.

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
