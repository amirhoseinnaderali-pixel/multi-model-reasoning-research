# Execution

## Validation-only dry run
```bash
make test
make dry-run
make audit
```

The dry run uses deterministic mock adapters. Records are marked `validation_only` and never become scientific results.

## Real execution gate
1. Frozen EXP-001 benchmark material is materialized and hash-verified.
2. Exact model IDs/snapshots and pricing are frozen.
3. Prompt/configuration hashes are frozen.
4. Docker and an immutable image digest are available.
5. Credentials are present.
6. `scripts/preflight.py` passes.

Missing credentials, models, Docker, benchmark data, or network access do not trigger mock fallback.
