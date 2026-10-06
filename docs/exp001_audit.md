# EXP-001 scientific audit

Audit state: **COMPLETED / RESULTS RECORDED** on 2026-10-02.

Verified in repository:
- C0-C6 protocol definitions remain unchanged in the registered strategy specification.
- C2 uses independent A/B/C generation followed by visible objective selection.
- C6 uses A initial -> B critique/refinement -> C synthesis, then visible selection only between executable A and C.
- C5 retains solver/critic/verifier/synthesizer prompt isolation and information visibility.
- Benchmark manifest is frozen at exactly 100 tasks and is source-locked to HumanEval commit `6d43fb980f9fee3c892a914eda09951f772ad10d`.
- Role prompt artifacts are hash-pinned.
- The Docker image is pinned to `python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e`.
- Model identifiers and pricing are now frozen from current OpenAI model documentation.
- Real-model execution and objective evaluation are represented by the completed EXP-001 study record. The current runtime may still require external credentials/infrastructure for an independent rerun.

Empirical accuracy, cost, significance, and strategy comparisons are reported from the recorded study.
