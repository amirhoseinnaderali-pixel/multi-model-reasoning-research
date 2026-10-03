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

## Recorded EXP-001 results

The current P6 study reports the recorded C0–C6 measurements under the frozen protocol.

| Condition | Hidden pass rate | 95% uncertainty interval | Δ vs C0 |
|---|---:|---|---:|
| C0 | 0.900 | 0.85–0.94 | — |
| C1 | 0.905 | 0.86–0.94 | +0.5 pp |
| C2 | 0.920 | 0.88–0.95 | +2.0 pp |
| C3 | 0.900 | 0.85–0.93 | 0.0 pp |
| C4 | 0.880 | 0.82–0.92 | −2.0 pp |
| C5 | 0.880 | 0.82–0.92 | −2.0 pp |
| C6 | 0.915 | 0.87–0.95 | +1.5 pp |

Recorded secondary measurements include approximately 24,000 model calls across the full matrix, approximately 4.6M output tokens, and approximately $120 estimated total cost (80% interval $80–$180), with the study noting that the four budget levels are non-binding under the recorded protocol.

The paired uncertainty intervals and analysis plan are reported in the main README and preserved study documentation.

### Scope and limitations

The reported values describe this frozen benchmark, model set, prompting protocol, and budget regime. They should not be generalized automatically to other benchmarks, models, or collaboration designs. In particular, differences between conditions can reflect both collaboration structure and the identities of the participating models, and the HumanEval-derived benchmark has known contamination/ceiling limitations.

## Conclusion

P6 contains a completed controlled multi-model collaboration study with recorded empirical results, alongside an explicit limitations and provenance record.

The older multi-agent repositories remain valuable research lineage and engineering evidence. They are not substituted for the current P6 result set when discussing the controlled C0–C6 study.

## Reproducibility boundary

The current P6 repository is the authoritative implementation of the target experiment. Future replications should use the frozen benchmark, protocol, and provenance controls; the recorded summary results above describe the completed study.