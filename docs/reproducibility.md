# Reproducibility contract

Every scientific result records experiment/run IDs, condition, task ID, seed, Git SHA, experiment configuration hash, benchmark manifest hash, task hash, frozen model configuration hash, prompt hash, immutable Docker digest, budget declaration and consumption, execution trace, objective verdict, and failure classification.

Model traces also record model role, exact model identifier returned by the provider, semantic role, prompt version, token usage, latency, pricing-based cost, API endpoint, service tier, and provider system fingerprint when available.

Seed is a best-effort reproducibility control. Hidden evaluation never participates in generation or candidate selection.

The completed EXP-001 study was executed under the frozen protocol. The real execution path remains fail-closed for future reruns: credentials, the immutable Docker environment, and all frozen provenance gates must be satisfied before another run is allowed.
