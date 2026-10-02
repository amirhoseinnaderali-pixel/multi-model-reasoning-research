# Multi-Model Reasoning Research

### Portfolio status

**REGISTERED — EMPIRICAL RESULT NOT RECOVERED FOR THE TARGET QUESTION**

The C0–C6 instrument is implemented and hardened, but no controlled real-model result set matching the P6 research question was recovered. Earlier multi-agent repositories are treated as lineage, not as P6 empirical results.

Controlled research infrastructure for studying **multi-model / collective reasoning** in large language models.

## EXP-001

**Fixed-Budget Multi-Model Collaboration Benchmark**

Conditions:
- **C0** — Single Model Baseline
- **C1** — Independent Multi-Sample with visible objective candidate selection
- **C2** — Independent Multi-Model with visible objective candidate selection
- **C3** — Debate / Critique
- **C4** — Sequential Collaborative Refinement
- **C5** — Explicit Solver / Critic / Verifier / Synthesizer specialization
- **C6** — Sequential Solver -> Critic/Refinement -> Synthesizer, followed by independent visible objective verification

C2 and C6 remain scientifically distinct: C2 has no candidate-to-candidate information flow; C6 deliberately introduces A -> B -> C information flow and then selects only between executable A and C using visible tests.

### Expected Projection — Pre-Execution

> ⚠️ **EXPECTED ONLY — NOT AN EMPIRICAL RESULT**
>
> The values below are **prior estimates made before the real EXP-001 run**. They are included to make the study falsifiable and to provide a reference against which the eventual real run can be compared. **No accuracy, ranking, or significance claim is made from these numbers.**

#### Projected hidden-test correctness

| Condition | Strategy | Expected center | Approx. 80% range |
|:--|:--|--:|--:|
| **C0** | Single-model baseline | **78%** | 74–82% |
| **C1** | Multi-sample + execution-based selection | **83%** | 79–87% |
| **C2** | Multi-model + execution-based selection | **84%** | 79–88% |
| **C3** | Debate / critique | **79%** | 74–84% |
| **C4** | Sequential refinement | **80%** | 75–85% |
| **C5** | Four-role collaboration | **79%** | 72–85% |
| **C6** | A → B → C with execution-based choice of A/C | **83%** | 79–87% |

**Expected mechanism:** objective execution-based verification is hypothesized to contribute more than interaction alone.

```text
Expected ordering (hypothesis)

Execution-based selection
C1 ≈ C2 ≈ C6
        ≥
C4 ≳ C3 ≈ C5 ≈ C0
```

#### Prior probabilities for specific claims

| Claim | Prior probability |
|:--|--:|
| **C1 > C0** | **85%** |
| **C1, C2, and C6 all exceed C0** | **65%** |
| **Best condition is C1, C2, or C6** | **70%** |
| **C3 is at most 2 pp above C0** | **65%** |
| **C5 is below C0** | **25%** |
| **C2 vs C1 is statistically significant** | **10%** |
| **C5 is the best condition** | **8%** |
| **Exact proposed ordering holds** | **<2%** |
| **Verification matters more than collaboration** | **65%** |

<details>
<summary><strong>Interpretation and statistical resolution</strong></summary>

With 100 tasks and accuracy near 80%, the expected standard error of a single accuracy estimate is roughly **4 percentage points**. Paired comparisons are more informative, but differences of only a few points should still be treated cautiously. The planned analysis uses paired comparisons such as **McNemar's test** and reports discordant counts rather than relying only on percentages.

The largest uncertainties are:

- **C6 tie-break behavior:** when both A and C pass visible tests, the choice between them may move C6 by several points.
- **Visibility in C3–C5:** if these conditions can also use visible execution feedback, this projection may understate them.
- **C0 strength:** a particularly strong baseline can reduce the marginal value of model diversity.
- **Budget scaling:** the current conditions fit within the primary budget, so larger budgets may not reveal scaling effects unless call counts are parameterized by budget.

</details>

<details>
<summary><strong>Diagnostic checks for the real run</strong></summary>

These patterns are treated as audit signals, not explanations to be assumed in advance:

| Observed pattern | First audit target |
|:--|:--|
| C1 exactly equals C0 | Sampling diversity, temperature, or pipeline behavior |
| C2 exactly equals C1 | Model routing / model-identity freeze |
| All conditions are nearly identical or near 100% | Mock or `validation_only` execution |
| C4/C5 fall far below C0 | 512-token truncation or output parsing |
| Hidden accuracy is far below visible accuracy | Weak visible tests / limited selection signal |
| Evaluator failures exceed 5% | Sandbox or evaluator validity |
| C6 is well below C1 | A/C tie-break behavior |

</details>

**Key discipline:** the real experiment may confirm, weaken, or contradict these projections. A surprising outcome is a result to audit and investigate—not a reason to retroactively change the prior.

## Scientific safeguards

- Benchmark provenance is source-locked and exactly 100 tasks.
- Hidden tests never enter generation, critique, refinement, synthesis, ranking, or candidate selection.
- C1/C2/C6 visible selection is performed by execution, not LLM judgment.
- C5 uses frozen role-specific prompts and explicit information visibility.
- Every model call reserves worst-case budget before execution and settles against actual usage.
- Reserved and actual budget quantities are both recorded.
- Model failures and evaluator failures are explicitly classified.
- Mock validation is marked `validation_only` and cannot become scientific evidence.
- Real mode fails closed when credentials, model freeze, benchmark material, Docker, or smoke verification are unavailable.

## Current status

**IMPLEMENTED / SCIENTIFICALLY HARDENED / NOT EXECUTED.**

Models and provider pricing are now frozen. The remaining execution gates are the real Docker sandbox smoke test and credentials in the execution environment. No empirical accuracy, cost, significance, or strategy ranking is claimed.

## Validation

```bash
make test
make dry-run
make audit
```

`make audit` remains intentionally fail-closed until real execution gates pass.

## Real execution

After the full gate passes:

```bash
make preflight
python scripts/run_smoke_test.py
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.json --mode real
```

Real mode has no mock fallback.

## Paper status

**IMPLEMENTED / SCIENTIFICALLY HARDENED / NOT EXECUTED.**

See [docs/research_report.md](docs/research_report.md) for the historical evidence audit and conclusion.
