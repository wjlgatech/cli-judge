# Build Instructions — Gemini CLI

1. Load the repo. Read `/AGENTS.md`, `/SPEC.md`, `/RUBRIC.md` (in that order).
2. Bootstrap: `cd harness && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev]`.
3. Confirm the skeleton runs: `cli-judge validate ../fixtures` then `cli-judge selftest`.
4. Build WB3->WB4->WB5 first to close the scoring loop; then WB6–WB9.
5. Keep changes minimal and typed; run `pytest -q` continuously.
6. Hard rules: no generator scope-creep; D4 is record/assert only; reality-traceable points only; stdlib-first.
7. Finish at `/AGENTS.md` Definition of Done; ensure CI green.
