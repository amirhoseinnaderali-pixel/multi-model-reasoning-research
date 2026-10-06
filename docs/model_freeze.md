# EXP-001 model freeze

Freeze date: **2026-10-02**.

The experiment uses only OpenAI Chat Completions and freezes exact model identifiers. The freeze policy prefers provider-dated snapshots, excludes `latest` aliases and models currently marked deprecated, and records the provider pricing page used for the freeze.

| Role | Frozen identifier | Role usage | Input / 1K | Output / 1K |
|---|---|---|---:|---:|
| A | `gpt-5.5-2026-04-23` | primary solver | $0.005 | $0.030 |
| B | `gpt-5.4-2026-03-05` | secondary solver / critic | $0.0025 | $0.015 |
| C | `gpt-5.4-mini-2026-03-17` | tertiary solver / verifier / synthesizer | $0.00075 | $0.0045 |
| D | `gpt-5.2-2025-12-11` | synthesizer | $0.00175 | $0.014 |

All roles use: temperature 0, top_p 1, reasoning_effort none, service_tier default, max 512 completion tokens, max 8192 input tokens, and the experiment seed.

Pricing is stored as USD per 1,000 tokens. The recorded pricing verification date is 2026-10-02; it is the date on which the provider page was checked for this freeze, not a claim about the historical date on which the provider introduced that price.

Official sources:
- https://developers.openai.com/api/docs/models/gpt-5.5
- https://developers.openai.com/api/docs/models/gpt-5.4
- https://developers.openai.com/api/docs/models/gpt-5.4-mini
- https://developers.openai.com/api/docs/models/gpt-5.2

Seed is a best-effort reproducibility control rather than a mathematical determinism guarantee. The OpenAI response fingerprint, when available, is stored in the execution trace.
