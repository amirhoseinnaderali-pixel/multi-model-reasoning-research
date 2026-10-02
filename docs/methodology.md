# Methodology

## Scientific question
Can collaboration between multiple language models improve reasoning performance compared with a single language model, and which collaboration strategy provides the best correctness–compute trade-off?

No outcome is assumed.

## Conditions
C0 one generation; C1 repeated same-model samples; C2 independent different-model answers; C3 solver/critic/revision; C4 sequential refinement; C5 role specialization; C6 collaborative candidates plus independent objective verification.

## Confound controls
Compute is bounded during generation. Model identities and snapshots are frozen. C1 separates sampling from diversity. Prompts are versioned artifacts. Hidden tests never enter strategy context. Round-by-round information visibility is explicit.

## Metrics
Primary: objective correctness.
Secondary: calls, generated tokens, latency, estimated cost, and failure classes.
Derived: correctness/call, correctness/token, correctness/cost, correctness/second.
