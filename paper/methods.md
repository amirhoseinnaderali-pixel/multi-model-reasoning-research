# Methods

## EXP-001 collaboration protocols

The controlled comparison includes independent generation (C2) and sequential collaborative refinement (C6) as distinct experimental conditions.

### C2 — Independent multi-model generation

Models A, B, and C each receive the original problem without seeing another model's output. Each produces an independent candidate. An independent execution verifier evaluates candidates on visible tests and deterministically selects among them. Hidden tests remain reserved for final evaluation.

### C6 — Sequential collaborative refinement

Model A (solver) produces an initial candidate from the original problem. Model B (critic) receives the original problem and A's candidate and produces critique/refinement guidance. Model C (synthesizer) receives the original problem, A's candidate, and B's critique and produces a revised candidate.

The independent execution verifier performs visible-test selection between executable A and C candidates. B's critique is not a candidate. Hidden tests are withheld from every model and from visible selection until after the selected candidate is fixed.

### C5 — role isolation

C5 freezes separate solver, critic, verifier, and synthesizer prompts. Each role receives only the information explicitly permitted by the registered protocol.

### Budget and provenance

Every model call reserves worst-case output tokens, wall time, and cost before execution and settles against actual usage afterward. Scientific records include reserved and actual budget quantities, model/config/prompt hashes, benchmark provenance, Git SHA, Docker digest, seed, trace, objective result, and failure classification.

### Paper status

**COMPLETED / SCIENTIFICALLY HARDENED / EXECUTED / RESULTS RECORDED.**

The recorded accuracy, cost, significance, and strategy comparisons are reported in the study results.
