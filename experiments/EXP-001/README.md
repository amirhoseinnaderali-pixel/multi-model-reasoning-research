# EXP-001 — Fixed-Budget Multi-Model Collaboration Benchmark

Status: **COMPLETED / SCIENTIFICALLY HARDENED / EXECUTED / RESULTS RECORDED**.

Primary question: under a fixed inference-time compute budget, does collaboration between multiple language models improve objective task correctness compared with C0?

Conditions: C0-C6. Seeds: 42, 43, 44. Budget sweep: B1-B4.

## Frozen models

A = `gpt-5.5-2026-04-23`  
B = `gpt-5.4-2026-03-05`  
C = `gpt-5.4-mini-2026-03-17`  
D = `gpt-5.2-2025-12-11`

Exact model IDs, endpoint, generation parameters, and provider pricing are recorded in `configs/models/models.json`.

## C2

Models A, B, and C independently receive the original problem. No candidate-to-candidate information is available during generation. Visible objective execution selects among the three executable candidates.

## C6

`Problem -> A/solver -> B/critic -> C/synthesizer -> visible objective selection`

Model B receives A's candidate. Model C receives A's candidate and B's critique. Visible selection compares only A-initial and C-revised candidates. B remains critique metadata.

## Hidden-test boundary

Hidden tests and hidden-test outcomes are unavailable to all model calls and to visible selection. They are evaluation-only and are run only after candidate selection.

## Execution gate

The repository remains fail-closed for independent reruns, and no mock output can enter `results/raw/EXP-001`. The completed study results are maintained separately from validation outputs.
