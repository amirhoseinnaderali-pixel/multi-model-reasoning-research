# EXP-001 Scientific Audit

## Audit state

**PROTOCOL AUDITED / FULL EMPIRICAL RESULT SET NOT VERIFIED**

## Verified in repository

- C0–C6 protocol definitions are present.
- The benchmark manifest is frozen at 100 HumanEval-derived tasks.
- Hidden-test isolation and visible-test selection boundaries are encoded.
- Role-specific prompts and model configuration are versioned.
- Budget reservation/settlement and failure classification are instrumented.
- The real execution path is fail-closed.
- Validation and mock execution are explicitly separated from scientific results.

## Evidence boundary

The repository does **not** currently contain a provenance-complete full EXP-001 raw result set sufficient to support measured accuracy, cost, significance, or strategy-ranking claims.

Therefore no benchmark numbers are recorded here as empirical findings.

Any earlier projection, placeholder, or README result table that lacks a corresponding preserved raw execution artifact is not treated as evidence.

## Required evidence for a future result claim

A real EXP-001 result should preserve, at minimum:

1. raw task/seed/condition records;
2. exact model and prompt provenance;
3. candidate identities and selection trace;
4. visible and hidden objective outcomes;
5. realized token/cost/latency telemetry where claimed;
6. the analysis output derived from those raw records.

## Conclusion

The experimental instrument is implemented and audited. The scientific result is **not yet established by a provenance-complete committed dataset**.
