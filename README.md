# Multi-Model Reasoning Research

Controlled research infrastructure for studying **multi-model / collective reasoning** in large language models.

## Research question

> **Can collaboration between multiple language models improve reasoning performance compared with a single language model, and which collaboration strategy provides the best correctness–compute trade-off?**

This repository is a scientific instrument, not a multi-agent demo. It is deliberately designed so the eventual evidence may show that collaboration helps, does not help, helps only for some protocols/budgets, or does not justify additional computation.

## EXP-001

**Fixed-Budget Multi-Model Collaboration Benchmark**

Conditions:

- **C0** — Single Model Baseline
- **C1** — Independent Multi-Sample with visible objective candidate selection
- **C2** — Independent Multi-Model with visible objective candidate selection
- **C3** — Debate / Critique
- **C4** — Sequential Collaborative Refinement
- **C5** — Explicit Solver / Critic / Verifier / Synthesizer specialization
- **C6** — Collaboration + Objective Verification

Seeds: `42, 43, 44`.

Budgets: `B1–B4` with hard call/token/time/cost limits.

Primary metric: **objective correctness**.

Secondary metrics: calls, generated tokens, latency, estimated cost, and explicit failure classes.

## Scientific safeguards

- Budget reservation occurs **before** each model call.
- C1/C2 candidate selection uses visible objective execution, not exact string majority.
- Hidden tests never enter strategy context or candidate selection.
- C5 roles use separate versioned prompts with explicit information visibility.
- Objective execution is independent of LLM self-evaluation.
- Infrastructure failures are distinct from wrong answers, timeouts, malformed outputs, and model failures.
- Prompts, model configs, benchmark provenance, seeds, execution traces, and git state are traceable.
- Mock validation is structurally marked `validation_only` and cannot enter scientific analysis.
- Real execution fails closed when credentials, models, Docker, benchmark material, or frozen provenance are unavailable.
- No empirical result is stored in the paper as evidence before real execution.

## Current status

**IMPLEMENTED / NOT EXECUTED.**

The software scaffold, seven collaboration protocols, budget enforcement, benchmark provenance gate, objective-verification interfaces, statistical utilities, validation-only dry run, tests, and fail-closed audit are implemented.

The scientific experiment remains **not executable until external inputs are frozen**: benchmark task material, model snapshots/pricing, and an immutable Docker image digest. The repository intentionally does not fabricate any of them.

## Validation

```bash
make test
make dry-run
make audit
```

`make audit` is expected to fail closed until the real-execution gates are satisfied.

## Lineage

Previous repositories are **READ-ONLY source material** and are not modified by this project. Methodological lessons are documented in `docs/research_lineage.md`, with `efficient-reasoning-research` serving as the immediate methodological predecessor for fixed budgets, objective evaluation, manifests, and auditability.

## Real execution

After freezing the benchmark material, model configuration, pricing, role prompts, and Docker digest:

```bash
make preflight
python scripts/run_experiment.py --config configs/experiments/exp001_fixed_budget.json --mode real
```

No fallback to mock models occurs in real mode.

## Paper status

The paper outline is present, but **Results are explicitly pending execution**. No accuracy, significance, latency, cost, or conclusion is claimed by this repository yet.
