# EXP-001 — Fixed-Budget Multi-Model Collaboration Benchmark

Status: **IMPLEMENTED / NOT EXECUTED**.

Primary question: under a fixed inference-time compute budget, does collaboration between multiple language models improve objective task correctness compared with C0?

Conditions: C0–C6. Seeds: 42, 43, 44. Budget sweep: B1–B4.

## Protocol corrections

**C1 — Independent Multi-Sample**

Three independent samples use distinct deterministic seeds. Candidates are selected by objective execution on the visible tests; exact string majority is not used. Hidden tests remain reserved for final evaluation.

**C2 — Independent Multi-Model**

Three different model configurations independently generate candidates. Candidate selection again uses visible objective execution only. Hidden tests remain reserved for final evaluation.

**C5 — Role-Specialized Collaboration**

The protocol is explicitly:

`Solver → Critic → Verifier → Synthesizer`

with separate versioned prompts and explicit information visibility. The verifier role is an LLM analysis step, not the independent execution evaluator.

Scientific results are pending real execution.
