# Multi-Model Reasoning Research

**Fixed-Budget Multi-Model Collaboration under Objective Execution-Based Evaluation**

> **Portfolio status:** CONTROLLED STUDY IMPLEMENTED — EMPIRICAL RESULT SET NOT COMMITTED
>
> The repository contains a frozen research protocol, executable instrumentation, validation paths, and an evidence audit. No unsupported benchmark accuracy numbers are presented as results.

## 1. Research question

Under a fixed inference-time budget, can collaboration among multiple language models improve objective program-synthesis correctness compared with single-model and simpler multi-sample strategies?

The study is designed around seven conditions (C0–C6), objective execution-based evaluation, visible-test selection, hidden-test isolation, fixed model snapshots, and explicit budget accounting.

## 2. Experimental design

### Conditions

| ID | Strategy | Calls / task | Main distinction |
|---|---|---:|---|
| C0 | Single model | 1 | baseline |
| C1 | Independent same-model sampling | 3 | sampling diversity without inter-candidate communication |
| C2 | Independent multi-model sampling | 3 | model diversity without inter-candidate communication |
| C3 | Debate / critique / revision | 3 | sequential critique without candidate execution feedback |
| C4 | Sequential refinement | 3 | multi-model sequential generation |
| C5 | Role-specialized collaboration | 4 | solver / critic / verifier / synthesizer roles |
| C6 | Collaborative refinement + objective verification | 3 | A→B→C information flow plus executable visible-test selection |

### Frozen benchmark and controls

- 100 HumanEval-derived Python tasks are defined by a source-locked manifest.
- Visible tests may be used for selection; hidden tests are reserved for final evaluation.
- Candidate selection is execution-based rather than LLM-as-judge.
- Model IDs, decoding settings, prompts, hashes, and budget accounting are versioned.
- Real execution is fail-closed when required credentials or infrastructure are unavailable.
- Validation / mock runs are explicitly separated from scientific evidence.

## 3. Evidence status

The current repository contains the **experimental instrument**, not a provenance-complete full C0–C6 result dataset.

The repository's audit therefore supports claims about:

- research-question formalization;
- implementation of the seven conditions;
- candidate-generation and selection logic;
- hidden-test isolation;
- budget and provenance instrumentation;
- validation and audit procedures.

It does **not** currently support a defensible claim that any C0–C6 condition achieved a particular accuracy, cost, significance level, or overall performance ranking.

## 4. Historical lineage

Earlier repositories in this portfolio contain real multi-agent and reasoning development, including multi-agent generation and sequential refinement prototypes. Those artifacts are kept as lineage rather than being promoted into this controlled benchmark because they do not share the same frozen task set, matched budget, condition matrix, and objective evaluation protocol.

In particular, `multi-agent-react-sandbox` contains a real historical 24-candidate execution trace, but its original correctness signal was later found to be invalid. It is therefore treated as a separate historical case study.

## 5. Reproduction

Validation-only checks:

```bash
make test
make dry-run
make audit
```

A real scientific run requires the frozen benchmark, model credentials, Docker execution environment, and the real-execution gate described in `docs/execution.md`.

## 6. Reporting rule

No number is considered an empirical result merely because it appears in a configuration, projection, smoke test, or README. A full benchmark result is reported only when the corresponding raw result artifact and provenance record are preserved.

See `docs/research_report.md` and `docs/exp001_audit.md` for the evidence boundary and audit history.

## License

MIT.
