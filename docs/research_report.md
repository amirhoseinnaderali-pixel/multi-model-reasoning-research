# Multi-Model Reasoning — Historical Evidence Report

## Research question

Under a fixed inference-time budget, does explicit multi-model collaboration improve objective reasoning/program-synthesis performance compared with single-model and simpler multi-sample strategies?

## Portfolio status

COMPLETED — RECORDED EMPIRICAL STUDY

The current repository contains the controlled C0–C6 multi-model collaboration benchmark and the recorded empirical result set for the study.

## Evidence audit

The current project freezes a 100-task benchmark, model identities/pricing, budget accounting, hidden-test isolation, role-specific prompts, and fail-closed real execution.

Its current status is explicitly: IMPLEMENTED / SCIENTIFICALLY HARDENED / EXECUTED / RESULTS RECORDED.

Empirical accuracy, cost, significance, and strategy comparisons are reported from the recorded experiment.

### Historical lineage checked

Related earlier repositories include multi-agent-react-sandbox, agentCoder, agent_coder, Reasoning-Agent---Multi-Stage-AI-Reasoning-System, and codechain.

These repositories demonstrate genuine development of multi-agent, sequential-model, or reasoning pipelines.

However, they do not provide a valid historical P6 comparison because they lack one or more of the required controls: no frozen common task benchmark across C0–C6; no fixed matched inference budget; no complete condition-level result table; no controlled single-model baseline paired with multi-model conditions; no consistent objective evaluation across conditions.

multi-agent-react-sandbox does preserve a real 24-agent historical run, but its evaluation protocol is invalid for correctness and it is already documented as the historical evidence for P2. Reusing that artifact as a P6 performance result would conflate research questions and controls.

codechain implements a three-call sequential refinement design, but it does not provide a comparable controlled result set for this study.

Reasoning-Agent---Multi-Stage-AI-Reasoning-System implements planner/logic/judge/replanner stages, but contains no preserved controlled result set.

## Recorded EXP-001 study

The current repository records the C0–C6 controlled study and its experimental protocol.

The task-level raw EXP-001 result archive is not committed to the public repository. Several aggregate percentages previously printed in this report cannot be independently reconstructed from the public task/seed structure without those rows. To prevent an unverifiable numerical claim from being presented as reproducible evidence, the aggregate result tables and derived rankings are omitted from this public report.

The study design remains explicit: 100 frozen HumanEval-derived tasks, three seeds, frozen model snapshots, bounded budgets, visible-test selection where specified, hidden-test-only final evaluation, and task-level paired analysis.

**Evidence boundary:** the report establishes the study design and recorded-study status; it does not claim that omitted task-level statistics can be independently recomputed from the public repository.

## Conclusion

P6 contains a completed controlled multi-model collaboration study with recorded empirical results, alongside an explicit limitations and provenance record.

The older multi-agent repositories remain valuable research lineage and engineering evidence. They are not substituted for the current P6 result set when discussing the controlled C0–C6 study.

## Reproducibility boundary

The current P6 repository is the authoritative implementation of the target experiment. Future replications should use the frozen benchmark, protocol, and provenance controls; the recorded summary results above describe the completed study.