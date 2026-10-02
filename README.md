# Multi-Model Reasoning Research

### Portfolio status

**REGISTERED — EMPIRICAL RESULT NOT RECOVERED FOR THE TARGET QUESTION**

The C0–C6 instrument is implemented and scientifically hardened, but no controlled real-model result set matching the P6 research question has been recovered. Earlier multi-agent repositories are treated as research lineage, not as P6 empirical results.

Controlled research infrastructure for studying **multi-model / collective reasoning** in large language models.

---

# EXP-001 — Fixed-Budget Multi-Model Collaboration Benchmark

## Research question

> **Under a fixed inference-time compute budget, does collaboration between multiple language models improve objective task correctness compared with a single-model baseline and simpler multi-sample strategies?**

The primary outcome is **task-level hidden-test correctness** on a frozen 100-task programming benchmark.

Secondary outcomes are designed to capture the cost of obtaining that correctness:

- model-call usage;
- output-token consumption;
- latency / wall time;
- estimated monetary cost;
- model and evaluator failures;
- candidate-selection behavior.

---

## Conditions

| Condition | Strategy | Core mechanism |
|:--|:--|:--|
| **C0** | Single-model baseline | One candidate from the primary solver |
| **C1** | Independent multi-sample | Three same-model candidates + visible-test selection |
| **C2** | Independent multi-model | Three heterogeneous-model candidates + visible-test selection |
| **C3** | Debate / critique | Two solver candidates plus a critic |
| **C4** | Sequential collaborative refinement | Information passed through a three-stage pipeline |
| **C5** | Solver / critic / verifier / synthesizer | Explicit four-role collaboration |
| **C6** | Sequential collaboration + objective verification | Solver → critic/refinement → synthesizer, then visible-test choice between A and C |

C2 and C6 are deliberately different. C2 keeps the candidates independent; C6 introduces explicit A → B → C information flow and then performs objective selection between executable candidates.

---

# ⚠️ Expected Projection — Pre-Execution

> **EXPECTED ONLY — NOT AN EMPIRICAL RESULT**
>
> Every number in this section is a **prior estimate made before the real EXP-001 run**. These projections exist to make the study falsifiable and to provide a reference for comparison with the eventual measured result.
>
> **They are not measured accuracies, confidence intervals, statistical results, or rankings.**

The repository remains **NOT EXECUTED**. No empirical performance claim is made from the values below.

---

## 1. Projected Hidden-Test Correctness

The current prior uses an estimated **C0 baseline of 78%**.

| Condition | Strategy | Expected center | Approx. 80% range |
|:--|:--|--:|:--:|
| **C0** | Single-model baseline | **78%** | **74–82%** |
| **C1** | Multi-sample + execution-based selection | **83%** | **79–87%** |
| **C2** | Multi-model + execution-based selection | **84%** | **79–88%** |
| **C3** | Debate / critique | **79%** | **74–84%** |
| **C4** | Sequential refinement | **80%** | **75–85%** |
| **C5** | Four-role collaboration | **79%** | **72–85%** |
| **C6** | A → B → C + execution-based choice of A/C | **83%** | **79–87%** |

### Projected central picture

```text
Hidden-Test Correctness

C0   78%
C1   83%   ●
C2   84%   ●
C3   79%   ●
C4   80%   ●
C5   79%   ●
C6   83%   ●
```

The projection therefore does **not** assume that additional collaboration automatically produces a monotonic accuracy increase.

The central hypothesis is narrower:

> **Execution-based candidate selection is expected to be more reliably useful than interaction alone.**

A useful qualitative grouping is:

```text
Selection by execution
C1 ≈ C2 ≈ C6
        ≥
C4 ≳ C3 ≈ C5 ≈ C0
```

This is a **mechanistic hypothesis**, not an empirical ranking.

---

## 2. Prior Probabilities for Specific Claims

| Claim | Prior probability |
|:--|--:|
| **C1 > C0** | **85%** |
| **C1, C2, and C6 all exceed C0** | **65%** |
| **The best condition is one of C1, C2, or C6** | **70%** |
| **C3 is at most 2 percentage points above C0** | **65%** |
| **C5 is below C0** | **25%** |
| **C2 vs. C1 is statistically significant** | **10%** |
| **C5 is the best condition** | **8%** |
| **The exact proposed ordering holds** | **<2%** |
| **Verification matters more than collaboration** | **65%** |

These priors are intentionally uncertain. A result that contradicts them is allowed and can be scientifically informative.

---

# 3. Why the Projection Is Conservative

The projection intentionally avoids assuming that every additional model call contributes an independent improvement.

The expected mechanism is:

```text
Objective verification
        >
Model diversity
        >
Critique / interaction
        >
Role specialization
```

This is a hypothesis about **marginal mechanism value**, not a statement that one condition must outperform another.

The main uncertainty is the degree to which candidate errors are actually independent.

If multiple candidates fail in the same way, adding more candidates creates little benefit.

If candidate failures are complementary, objective selection has more useful alternatives to choose from.

---

# 4. Projected Candidate-Selection Mechanism

For C1, C2, and C6, the final candidate decision is grounded in **visible executable tests** rather than a language model's subjective preference.

The expected conceptual chain is:

```text
More candidate coverage
        ↓
Potentially less-correlated errors
        ↓
Higher probability that at least one candidate is valid
        ↓
Objective visible-test selection
        ↓
Higher hidden-test correctness
```

The important distinction is that visible tests are used for **selection**, while hidden tests remain reserved for **final evaluation**.

The projection assumes that the visible tests contain enough useful signal to distinguish candidates without leaking hidden evaluation information.

---

# 5. Expected Diversity Effects

| Condition | Expected candidate diversity |
|:--|:--|
| **C0** | Minimal |
| **C1** | Low to moderate |
| **C2** | Moderate to high |
| **C3** | Moderate |
| **C4** | Moderate |
| **C5** | High role / semantic diversity |
| **C6** | Moderate candidate diversity + explicit information flow |

The projected mechanism is:

```text
Candidate diversity
        ↓
Potentially lower error correlation
        ↓
More useful alternatives
        ↓
Higher chance of selecting a correct candidate
```

The projection does **not** assume unlimited gains from diversity. Saturation and correlated failures remain plausible.

---

# 6. Mechanistic Expectations by Condition

## C1 — Independent Same-Model Sampling

C1 is expected to benefit from repeated exploration of the same model's solution space.

The main mechanism is:

> **More independent attempts + objective selection.**

The prior expectation is about **+5 percentage points** over C0 at the central estimate.

The projection does not assume that all three generations will be meaningfully different.

---

## C2 — Independent Multi-Model Sampling

C2 adds model heterogeneity while keeping candidate generation independent.

The expected benefit is therefore primarily associated with:

```text
Model diversity
      ↓
Potentially different failure modes
      ↓
More complementary candidates
```

The projected central estimate is **84%**, only about **1 pp above C1**.

That small gap is deliberate: the prior does not assume that multi-model diversity automatically produces a large improvement.

The probability that the C2–C1 gap is statistically significant is only **10%** under the stated prior.

---

## C3 — Debate / Critique

C3 introduces explicit critique without an external execution-based selector.

The expected benefit is limited because models can critique one another while still sharing the same incorrect assumption.

The projection therefore places C3 near the baseline:

**79% central estimate, 74–84% plausible operating range.**

---

## C4 — Sequential Collaborative Refinement

C4 introduces explicit information flow between stages.

The expected mechanism is:

```text
Candidate
   ↓
Interpretation / critique
   ↓
Refinement
   ↓
Revised candidate
```

The expected gain comes from **information reuse**, not merely from spending more calls.

The projection is intentionally modest:

**80% central estimate.**

A correct candidate can also be damaged by an incorrect refinement, so sequential collaboration is not assumed to be monotonic.

---

## C5 — Role Specialization

C5 separates the protocol into:

```text
Solver
   ↓
Critic
   ↓
Verifier
   ↓
Synthesizer
```

The hypothesis is that specialization can expose complementary information.

At the same time, C5 has the largest number of stages and the widest uncertainty band in the projection:

**79% central estimate, 72–85% range.**

The prior probability that C5 is the best condition is only **8%**.

This is intentional: role specialization is treated as a testable hypothesis, not as an assumed benefit.

---

## C6 — Sequential Collaboration + Objective Verification

C6 combines sequential information flow with an executable selection step:

```text
Solver A
   ↓
Critic / Refinement B
   ↓
Synthesizer C
   ↓
Visible-test evaluation
   ↓
Choose A or C
```

The final decision is therefore grounded in executable evidence.

The projected central estimate is **83%**, with an approximate **79–87%** range.

The main uncertainty is the **A/C tie-break case**: when both candidates pass visible tests, the selection policy can materially affect C6.

---

# 7. Projected Error Decomposition

The benchmark is intended to distinguish several failure classes:

```text
Generation Failure
        │
        ├── Incomplete / malformed candidate
        │
Reasoning Failure
        │
        ├── Algorithmic or logical error
        │
Coordination Failure
        │
        ├── Critique / refinement does not repair the defect
        │
Selection Failure
        │
        ├── Correct candidate generated but not selected
        │
Execution Failure
        │
        ├── Runtime / timeout / sandbox failure
        │
        ▼
Final Incorrectness
```

Unlike the projected accuracy numbers, no precise percentage distribution is frozen here as a scientific prior. The experiment is expected to **measure** the failure composition rather than manufacture an artificial decomposition in advance.

The resulting analysis should distinguish at least:

- reasoning failures;
- selection failures;
- incomplete or malformed generation;
- coordination / critique failures;
- evaluator / sandbox failures.

---

# 8. Fixed Inference Budgets

EXP-001 defines four budget envelopes:

| Budget | Max calls | Max output tokens | Max wall time | Max estimated cost |
|:--|--:|--:|--:|--:|
| **B1** | 4 | 2,048 | 120 s | $1.00 |
| **B2** | 8 | 4,096 | 240 s | $2.00 |
| **B3** | 12 | 6,144 | 360 s | $3.00 |
| **B4** | 16 | 8,192 | 480 s | $4.00 |

Each C0–C6 condition fits within the **B1** condition-level envelope.

Therefore, B2–B4 should **not** be interpreted as automatic evidence of scaling for the registered C0–C6 experiment. Larger budgets provide headroom for future adaptive or extended variants, but a scaling claim requires a protocol that actually allocates additional calls to the experimental conditions.

This distinction prevents unused budget capacity from being mistaken for empirical scaling evidence.

---

# 9. Model-Call and Token Structure

The frozen generation configuration reserves up to **512 output tokens per model call**.

The registered call structure therefore implies these theoretical maximum output-token counts:

| Condition | Calls | Maximum output tokens |
|:--|--:|--:|
| **C0** | 1 | 512 |
| **C1** | 3 | 1,536 |
| **C2** | 3 | 1,536 |
| **C3** | 3 | 1,536 |
| **C4** | 3 | 1,536 |
| **C5** | 4 | 2,048 |
| **C6** | 3 | 1,536 |

These are **upper bounds**, not expected realized usage.

The instrumentation records both:

- reserved budget;
- actual usage.

Actual cost and latency should therefore be calculated from telemetry rather than inferred only from configured maxima.

---

# 10. Projected Efficiency Analysis

Accuracy alone is not sufficient for an inference-time collaboration study.

The final analysis should report measured values for:

`Accuracy`

`Accuracy per Model Call`

`Accuracy per 1K Output Tokens`

`Accuracy per Dollar`

`Accuracy per Second`

The projection does **not** assign numerical values to these efficiency metrics before execution because realized input/output token usage, failures, latency, and selected candidates must be measured.

The intended research question is:

> **How much additional correctness is obtained for each additional unit of inference computation?**

---

# 11. Statistical Resolution

The benchmark contains **100 tasks**.

At accuracy near 80%, a single accuracy estimate has a standard error of roughly **4 percentage points** under a simple binomial approximation.

For paired comparisons, the experiment should use the fact that all conditions are evaluated on the same tasks.

A paired analysis such as **McNemar's test** is appropriate for binary task-level outcomes.

The report should include:

- number of tasks correct in each condition;
- discordant task counts for paired comparisons;
- effect sizes / percentage-point differences;
- uncertainty estimates;
- significance tests where appropriate.

Differences of only a few percentage points should be interpreted cautiously.

---

# 12. Largest Sources of Uncertainty

### C6 tie-break behavior

When both A and C pass visible tests, the choice between them can move C6 by several points.

### Visibility in C3–C5

If the implementation gives those conditions additional visible execution information, the projection may undervalue them.

### Strength of C0

If the single-model baseline is unusually strong, the marginal value of diversity can shrink.

### Budget allocation

All registered conditions fit within B1. Higher budgets do not automatically create additional scientific leverage unless call allocation is parameterized by budget.

### Visible-to-hidden test gap

Execution-based selection can only exploit the visible tests to the extent that they correlate with hidden correctness.

---

# 13. Diagnostic Patterns for the Real Run

These patterns are **audit signals**, not explanations to assume in advance.

| Observed pattern | First audit target |
|:--|:--|
| **C1 exactly equals C0** | Zero effective diversity, sampling configuration, or pipeline bug |
| **C2 exactly equals C1** | Model routing or model-identity freeze |
| **All conditions nearly identical or near 100%** | Mock / `validation_only` output |
| **C4 or C5 far below C0** | 512-token truncation or parsing failures |
| **Hidden accuracy far below visible accuracy** | Weak visible tests / limited selection signal |
| **Evaluator failures >5%** | Sandbox or evaluator validity |
| **C6 well below C1** | A/C tie-break behavior |

The intended response to a surprising result is an **implementation and provenance audit first**, followed by scientific interpretation.

---

# 14. Scientific Safeguards

EXP-001 is designed to prevent hidden evaluation information from entering the generation or selection process.

- Benchmark provenance is source-locked to **100 tasks**.
- Hidden tests are never supplied during generation, critique, refinement, synthesis, ranking, or candidate selection.
- C1/C2/C6 use **visible objective execution** for candidate selection.
- C5 uses frozen role-specific prompts and explicit information visibility.
- Every model call reserves worst-case budget before execution and settles against actual usage.
- Reserved and actual budget quantities are both recorded.
- Model failures and evaluator failures are explicitly classified.
- Mock validation is labeled `validation_only` and cannot become scientific evidence.
- Real mode fails closed when required credentials, model freeze, benchmark material, Docker, or smoke verification are unavailable.

---

# 15. Current Empirical Status

**IMPLEMENTED / SCIENTIFICALLY HARDENED / NOT EXECUTED**

The current repository has:

- a frozen 100-task benchmark;
- frozen model identities and pricing;
- frozen prompts;
- fixed budget envelopes;
- hidden-test isolation;
- objective visible-test selection where specified;
- model / evaluator failure instrumentation;
- a fail-closed real execution path.

What it does **not** yet have is a real C0–C6 empirical result set for the target research question.

Therefore, this README intentionally does **not** claim:

- that collaboration improves correctness;
- that C1/C2/C6 actually outperform C0;
- that C5 is inferior or superior;
- any empirical accuracy percentage;
- any empirical cost ranking;
- any statistical significance result;
- any overall winning strategy.

The projection above remains a prior until real execution produces provenance-complete task-level results.

---

# 16. Reproducibility Boundary

The authoritative experiment specification is frozen in the repository.

Key artifacts include:

```text
configs/experiments/exp001_fixed_budget.json
configs/models/models.json
configs/budgets/
prompts/
benchmarks/manifests/exp001_v1.json
benchmarks/programming/exp001_v1/tasks.jsonl
```

The real experiment should replace projected values with measured values **without changing the evaluation definitions merely to fit the observations**.

In particular:

```text
Expected projection
        ↓
Real execution
        ↓
Raw task-level results
        ↓
Audit / validity checks
        ↓
Statistical analysis
        ↓
Empirical conclusion
```

This separation is part of the scientific design.

---

# 17. Final Expected Summary

| Measure | Pre-execution projection |
|:--|:--|
| **Baseline correctness** | **~78%** |
| **C1 expected center** | **~83%** |
| **C2 expected center** | **~84%** |
| **C3 expected center** | **~79%** |
| **C4 expected center** | **~80%** |
| **C5 expected center** | **~79%** |
| **C6 expected center** | **~83%** |
| **Expected gain of highest projected center** | **~5–6 pp** |
| **Expected dominant mechanism** | **Objective verification / execution-based selection** |
| **Expected role of diversity** | **Useful when candidate errors are complementary** |
| **Expected interaction-only benefit** | **Small / uncertain** |
| **Projected scaling conclusion** | **Not identifiable from unused B2–B4 capacity alone** |
| **Empirical result status** | **Not executed** |

### Bottom line

The pre-execution hypothesis is deliberately modest:

> **Objective verification is expected to provide a more reliable source of improvement than collaboration alone, while model diversity may provide additional gains when candidate errors are not highly correlated.**

The real value of EXP-001 is not whether the projection is correct. It is whether the frozen experiment can **test and potentially falsify** that projection under controlled conditions.

---

## Validation

```bash
make test
make dry-run
make audit
```

`make audit` remains intentionally fail-closed until the real execution gates pass.

## Real execution

After the full gate passes:

```bash
make preflight
python scripts/run_smoke_test.py
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.json --mode real
```

Real mode has no mock fallback.

---

## Paper / Research Status

**IMPLEMENTED / SCIENTIFICALLY HARDENED / NOT EXECUTED**

See [docs/research_report.md](docs/research_report.md) for the historical evidence audit and conclusion.
