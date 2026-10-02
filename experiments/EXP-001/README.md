# EXP-001 — Fixed-Budget Multi-Model Collaboration Benchmark

Status: **IMPLEMENTED / SCIENTIFICALLY HARDENED / NOT EXECUTED**.

Primary question: under a fixed inference-time compute budget, does collaboration between multiple language models improve objective task correctness compared with C0?

Conditions: C0–C6. Seeds: 42, 43, 44. Budget sweep: B1–B4.

## C2 — Independent Multi-Model

Models A, B, and C independently receive the original problem. No model sees another model's candidate before generation. Visible objective execution deterministically selects among the three executable candidates.

## C6 — Collaborative Refinement + Objective Verification

Protocol:

`Problem → A/solver → B/critic → C/synthesizer → independent verifier`

Model B receives Model A's candidate.

Model C receives Model A's candidate and Model B's critique.

The independent verifier evaluates candidate A and candidate C on visible tests only and deterministically selects the final candidate for hidden-test evaluation. Model B's critique is not a candidate.

C6 therefore differs from C2 by **information flow and refinement semantics**, not merely by model labels.

## Hidden-test boundary

Hidden tests and hidden-test outcomes are unavailable to all C6 language-model calls and cannot influence visible selection. They are evaluation-only.

Scientific results are pending real execution.
