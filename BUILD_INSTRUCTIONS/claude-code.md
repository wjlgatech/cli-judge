# Build Instructions — Claude Code

1. Open this folder as your workspace. Run `/init` if you want a CLAUDE.md; then read `/AGENTS.md`, `/SPEC.md`, `/RUBRIC.md`.
2. Create a plan from the Work Breakdown in `/AGENTS.md` (WB0–WB9). Use a TODO list and work top-down.
3. Bootstrap & verify:
   ```
   cd harness && python3 -m venv .venv && . .venv/bin/activate && pip install -e .[dev]
   cli-judge validate ../fixtures && cli-judge selftest
   ```
4. Implement WB3->WB4->WB5 first (replay, scorers, runner). Run `pytest -q` after each.
5. Keep diffs small and tested. Prefer the standard library. Only `jsonschema` is required.
6. Respect the scope guard: CLI-Judge measures tools, never generates them. D4 is record/assert only.
7. Done when `/AGENTS.md` "Definition of Done" is fully satisfied and CI (`.github/workflows/cli-judge.yml`) is green.

Tip: the echo adapter (`harness/examples/echo_adapter.py`) lets you close the loop before any real tool exists — make `cli-judge selftest` meaningful first.
