# Benchmark manifests

A benchmark manifest is immutable experimental input. It records source provenance,
source commit/version, task IDs, task hashes, test hashes, and the evaluation split.

EXP-001 is intended to use the frozen 100-task HumanEval-derived manifest from the
methodological predecessor `efficient-reasoning-research`:

- canonical source: `openai/human-eval`
- source commit: `6d43fb980f9fee3c892a914eda09951f772ad10d`
- benchmark ID: `humaneval-stratified-100-v1`
- hidden tests must never be exposed to generation/selection strategies.

The actual task/test material must be materialized and hash-verified before real
execution. This repository does not silently download or regenerate it.
