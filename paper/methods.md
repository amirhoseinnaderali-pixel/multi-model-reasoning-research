# Methods

## EXP-001 collaboration protocols

The controlled comparison includes independent generation (C2) and sequential collaborative refinement (C6) as distinct experimental conditions.

### C2 — Independent multi-model generation

Models A, B, and C each receive the original problem without seeing another model's output. Each produces an independent candidate. An independent execution verifier evaluates candidates on visible tests and deterministically selects among them. Hidden tests remain reserved for final evaluation.

### C6 — Sequential collaborative refinement

Model A (solver) produces an initial candidate from the original problem. Model B (critic) receives the original problem and A's candidate and produces critique/refinement guidance. Model C (synthesizer) receives the original problem, A's candidate, and B's critique and produces a revised candidate.

The independent execution verifier then performs visible-test selection between the executable A and C candidates. B's critique is not itself a candidate. Hidden tests are withheld from every model and from visible selection until after the selected candidate is fixed.

Each C6 call uses a versioned role-specific prompt artifact, and the run trace records role, model identity, prompt version, round/order, token usage, latency, and cost accounting.

No empirical result is claimed here until EXP-001 is actually executed and analyzed.
