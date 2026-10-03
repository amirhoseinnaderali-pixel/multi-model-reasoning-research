# Multi-Model Reasoning — Evidence Report

## Scope

This report distinguishes the research instrument from empirical measurements that can actually be verified from repository artifacts.

## Research question

Under a fixed inference-time budget, does explicit multi-model collaboration improve objective program-synthesis performance compared with single-model and simpler multi-sample strategies?

## Current evidence status

**CONTROLLED STUDY IMPLEMENTED — NO PROVENANCE-COMPLETE FULL EMPIRICAL RESULT SET CURRENTLY COMMITTED**

The repository contains a frozen 100-task benchmark, C0–C6 condition definitions, model/prompt/budget controls, objective selection logic, hidden-test isolation, and validation/audit procedures.

The repository does not currently contain a provenance-complete full C0–C6 raw result dataset that would justify reporting benchmark accuracy, cost, significance, or a performance ordering as measured findings.

## What is supported

The current repository supports the following factual claims:

- The fixed-budget multi-model research question was formalized.
- C0–C6 are implemented as distinct experimental conditions.
- C2 prevents candidate-to-candidate information flow during generation.
- C6 introduces explicit A→B→C collaboration and then applies executable visible-test selection between the initial and revised candidates.
- Hidden tests are isolated from generation and selection.
- Model IDs, prompts, benchmark provenance, and budget accounting are instrumented.
- The real execution path is fail-closed rather than silently falling back to a mock result.

## What is not supported

The current repository does not justify claims that:

- multi-model collaboration improves correctness;
- debate or sequential collaboration outperforms independent sampling;
- role specialization improves accuracy;
- graph/aggregation or verification has a measured effect of a particular size;
- any C0–C6 condition is empirically the best;
- a specific benchmark accuracy, cost, confidence interval, or significance value was obtained by the full study.

## Historical lineage

Related earlier repositories include:

- `multi-agent-react-sandbox`: real historical execution trace, but invalid legacy correctness measurement;
- `agentCoder` / `agent_coder`: multi-agent code-generation development;
- `Reasoning-Agent---Multi-Stage-AI-Reasoning-System`: planner/judge/replanner pipeline;
- `codechain`: sequential refinement implementation.

These are useful engineering/research lineage, but they are not interchangeable with the present controlled C0–C6 study because their tasks, controls, budgets, and evaluation evidence differ.

## Evidence policy

A result is considered empirical only when the underlying execution artifact is preserved with enough provenance to reconstruct:

- task identity;
- condition;
- seed;
- model/prompt configuration;
- candidate identity;
- objective evaluation outcome;
- relevant budget/telemetry fields.

Configuration files, projections, validation runs, and source code alone are not treated as benchmark results.

## Reproducibility boundary

The frozen protocol remains available for future real execution. Any future quantitative claim should be generated from raw result artifacts produced by that protocol and should be reported separately from validation and historical evidence.
