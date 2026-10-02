# Methodology

## Scientific question
Can collaboration between multiple language models improve reasoning performance compared with a single language model, and which collaboration strategy provides the best correctness–compute trade-off?

No outcome is assumed.

## Conditions
C0 one generation; C1 repeated same-model samples; C2 independent different-model answers; C3 solver/critic/revision; C4 sequential refinement; C5 explicit role-specialized solver/critic/verifier/synthesizer; C6 collaborative candidates plus independent objective verification.

## C1/C2 candidate selection
C1 and C2 do **not** aggregate complete code by exact string equality. Each candidate is independently executed against the visible test set. Selection uses only visible-test objective evidence and never hidden-test outcomes.

C1 uses one frozen model configuration with distinct deterministic seeds for the independent samples. C2 uses distinct model configurations for the independent candidates.

The hidden test set remains reserved for final evaluation after candidate selection.

## C5 information visibility
C5 uses four semantic roles with independent prompt artifacts:

1. Solver — original problem only.
2. Critic — original problem + solver candidate.
3. Verifier — original problem + candidate + critique. This is a language-model analysis role, not the independent execution evaluator.
4. Synthesizer — original problem + candidate + critique + verifier notes.

Hidden tests and hidden-test outcomes are never supplied to any C5 role.

Each role has an explicit model-role mapping and is recorded in the execution trace with model identity, seed, and prompt version.

## Confound controls
Compute is bounded during generation. Model identities and snapshots are frozen. C1 separates repeated sampling from model diversity. Prompts are versioned artifacts. Hidden tests never enter strategy context or candidate selection. Round-by-round information visibility is explicit.

## Metrics
Primary: objective correctness.
Secondary: calls, generated tokens, latency, estimated cost, and failure classes.
Derived: correctness/call, correctness/token, correctness/cost, correctness/second.
