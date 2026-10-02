# Execution

## Validation-only dry run
```bash
make test
make dry-run
make audit
```

The dry run uses deterministic mock adapters. Records are marked `validation_only` and never become scientific results.

## C1/C2 selection boundary

C1 and C2 generate independent candidates and then use an independent objective verifier on the **visible** test set for candidate selection. Exact string equality is not used to define agreement.

The hidden test set is reserved for the final evaluator and is not supplied to any model or to visible-test selection.

## C5 role boundary

C5 uses four independent role prompts:

- Solver — original problem only.
- Critic — original problem + candidate.
- Verifier — original problem + candidate + critique.
- Synthesizer — original problem + candidate + critique + verifier notes.

The C5 verifier is a language-model role. It is distinct from the independent execution evaluator used where objective verification is specified.

Every C5 model call records semantic role, model role, model ID, seed, and prompt version in the execution trace.

## Real execution gate

1. Frozen EXP-001 benchmark material is materialized and hash-verified.
2. Exact model IDs/snapshots and pricing are frozen.
3. Role-specific prompt artifacts and configuration hashes are frozen.
4. Docker and an immutable image digest are available.
5. Credentials are present.
6. `scripts/preflight.py` passes.

Missing credentials, models, Docker, benchmark data, or network access do not trigger mock fallback.
