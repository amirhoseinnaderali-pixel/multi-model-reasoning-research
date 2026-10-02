# Multi-Model Reasoning — Historical Evidence Report

## Research question

Under a fixed inference-time budget, does explicit multi-model collaboration improve objective reasoning/program-synthesis performance compared with single-model and simpler multi-sample strategies?

## Portfolio status

REGISTERED — EMPIRICAL RESULT NOT RECOVERED FOR THE TARGET QUESTION

The current repository contains a controlled C0–C6 multi-model collaboration benchmark design, but no real empirical result set was recovered from the repository or its visible Git history.

## Evidence audit

The current project freezes a 100-task benchmark, model identities/pricing, budget accounting, hidden-test isolation, role-specific prompts, and fail-closed real execution.

Its current status is explicitly: IMPLEMENTED / SCIENTIFICALLY HARDENED / EXECUTED / RESULTS RECORDED.

No empirical accuracy, cost, significance, or strategy ranking is claimed.

### Historical lineage checked

Related earlier repositories include multi-agent-react-sandbox, agentCoder, agent_coder, Reasoning-Agent---Multi-Stage-AI-Reasoning-System, and codechain.

These repositories demonstrate genuine development of multi-agent, sequential-model, or reasoning pipelines.

However, they do not provide a valid historical P6 comparison because they lack one or more of the required controls: no frozen common task benchmark across C0–C6; no fixed matched inference budget; no complete condition-level result table; no controlled single-model baseline paired with multi-model conditions; no consistent objective evaluation across conditions.

multi-agent-react-sandbox does preserve a real 24-agent historical run, but its evaluation protocol is invalid for correctness and it is already documented as the historical evidence for P2. Reusing that artifact as a P6 performance result would conflate research questions and controls.

codechain implements a three-call sequential refinement design, but its own repository records the controlled experiment as not yet executed.

Reasoning-Agent---Multi-Stage-AI-Reasoning-System implements planner/logic/judge/replanner stages, but contains no preserved controlled result set.

## What can be claimed

P6 can honestly claim that:

- a fixed-budget multi-model collaboration question was formalized;
- C0–C6 conditions were implemented;
- visible and hidden evaluation boundaries were designed;
- model failures, budgets, provenance, and objective selection were instrumented;
- real execution is fail-closed.

## What cannot be claimed

The available evidence does not establish:

- that multi-model collaboration improves correctness;
- that debate/critique is better than independent sampling;
- that sequential collaboration is better than single-model generation;
- that specialized solver/critic/verifier roles improve performance;
- any accuracy, cost, or significance ranking among C0–C6.

## Conclusion

P6 is a completed controlled research-instrument project, but not a completed empirical study of the target question.

The older multi-agent repositories remain valuable research lineage and engineering evidence. They are not promoted into P6 empirical results because the necessary controlled comparisons are absent.

## Reproducibility boundary

The current P6 repository is the authoritative implementation of the target experiment. Future empirical claims must be based on raw, provenance-complete C0–C6 result files from the frozen benchmark and budget protocol.