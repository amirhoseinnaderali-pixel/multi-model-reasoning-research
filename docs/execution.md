# Execution

## Validation-only dry run
```bash
make test
make dry-run
make audit
```

The dry run uses deterministic mock adapters. Records are marked `validation_only` and never become scientific results.

## C2/C6 selection boundary

C2 is independent: A, B, and C each receive only the original problem before generation. Visible objective execution selects among the three executable candidates.

C6 is collaborative: A receives the original problem; B receives the original problem plus A; C receives the original problem plus A and B's critique. Visible objective execution compares only A-initial and C-revised candidates. B is critique metadata, not an executable candidate.

Hidden tests never enter generation, critique, refinement, synthesis, ranking, or candidate selection.

## C5 role boundary

C5 uses four frozen prompts:
- Solver: original problem.
- Critic: original problem + solver candidate.
- Verifier: original problem + candidate + critique.
- Synthesizer: original problem + candidate + critique + verifier notes.

The C5 verifier role is a language-model role and is separate from the independent execution evaluator.

## Budget boundary

Before every real model call, the engine reserves worst-case output tokens, wall time, and estimated cost. It settles against actual usage afterward and records reserved and actual quantities separately. Failed model calls are explicitly classified in the trace and in the result record.

## Real execution gate

1. Frozen 100-task benchmark and provenance pass validation.
2. Exact model IDs/snapshots and provider pricing are frozen.
3. All role prompts and hashes pass.
4. Docker immutable digest resolves correctly.
5. A one-task real smoke test passes for visible and hidden evaluation with the configured sandbox.
6. `OPENAI_API_KEY` is present in the execution environment.
7. Only then may `real_execution` be set to true.

There is no mock fallback in real mode.
