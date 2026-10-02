# Multi-Model Reasoning Research

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
