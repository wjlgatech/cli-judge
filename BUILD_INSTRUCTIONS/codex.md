# Build Instructions — Codex / OpenAI coding agents

1. Treat `/AGENTS.md` as the spec of record (Codex reads AGENTS.md natively). Then read `/SPEC.md` + `/RUBRIC.md`.
2. Environment: Python 3.10+. `cd harness && pip install -e .[dev]`.
3. Verify baseline: `cli-judge validate ../fixtures` and `cli-judge selftest` must pass before you change logic.
4. Implement the Work Breakdown in order; prioritize WB3 (replay), WB4 (scorers), WB5 (runner).
5. Write a pytest for each scorer as you implement it. CI runs `cli-judge validate`, `cli-judge selftest`, `pytest -q`.
6. Constraints: stdlib-first; `jsonschema` only hard dep; `cryptography` optional for WB7 receipts; no network in core suite; no destructive execution.
7. Stop at the Definition of Done in `/AGENTS.md`.
