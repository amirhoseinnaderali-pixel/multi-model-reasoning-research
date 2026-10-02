# Limitations

- EXP-001 is not yet executed; no empirical result is available.
- HumanEval-derived programming tasks measure executable correctness, not every form of reasoning.
- Model capability differences remain a potential confound; C1 isolates repeated sampling from model diversity.
- OpenAI documents seed as best-effort rather than strict deterministic replay; response fingerprints are therefore recorded when available.
- Provider pricing can change over time. The experiment freezes the price observed on 2026-10-02 and records the provider source page; it does not claim that this price was historically introduced on that date.
- Real Docker execution and API credentials are external gates and are deliberately not simulated in scientific mode.
