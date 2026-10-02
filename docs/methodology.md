# Methodology

## Scientific question

Can collaboration between multiple language models improve reasoning performance compared with a single language model, and which collaboration strategy provides the best correctness–compute trade-off?

No outcome is assumed.

## Conditions

C0 one generation; C1 repeated same-model samples; C2 independent different-model answers; C3 solver/critic/revision; C4 sequential refinement; C5 explicit solver/critic/verifier/synthesizer specialization; C6 sequential solver/critic/synthesizer collaboration followed by independent visible objective verification.

## C2: independent multi-model generation

C2 deliberately prevents candidate-to-candidate information flow. Models A, B, and C each receive the original problem and independently generate a solution. The visible objective verifier then selects among those independent executable candidates.

## C6: sequential collaborative refinement

C6 explicitly creates inter-model information flow:

1. **Model A / solver** receives the original problem and produces an initial candidate.
2. **Model B / critic** receives the original problem plus Model A's candidate and produces critique/refinement guidance.
3. **Model C / synthesizer** receives the original problem, Model A's candidate, and Model B's critique and produces a revised candidate.
4. An **independent execution verifier** evaluates candidate A and candidate C on visible tests only and deterministically selects the visible-test result.
5. Hidden tests are used only after selection for final scientific evaluation.

B's critique is not executed as a candidate. The independent verifier is not an LLM judge.

## Hidden-test isolation

Hidden tests and hidden-test outcomes are not passed to Model A, B, or C and are not included in any C6 prompt. The visible-selection operation receives only executable candidate artifacts and the visible test set. Hidden-test evaluation occurs afterward on the selected final candidate.

## Traceability

Every C6 model call records condition, model role, semantic role, model ID, seed, round, order, prompt version/path, input tokens, output tokens, latency, and estimated cost. This allows the collaboration information flow to be reconstructed from a run manifest.

## Confound controls

Compute is bounded during generation. Model identities and snapshots are frozen. C1 separates repeated sampling from model diversity. C2 prevents information sharing; C6 deliberately introduces information sharing. Prompts are versioned artifacts. Hidden tests are reserved for final evaluation.

## Metrics

Primary: objective correctness.

Secondary: calls, generated tokens, latency, estimated cost, and failure classes.

Derived: correctness/call, correctness/token, correctness/cost, correctness/second.
