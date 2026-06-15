# Build Instructions — Hermes (CLI-Anything orchestration skill) & other SKILL agents

Hermes/SKILL-compatible agents: this package is a self-contained brief, not a CLI-Anything harness — do NOT run it through /cli-anything. Build it directly.

1. Read `/AGENTS.md` (authoritative), then `/SPEC.md` and `/RUBRIC.md`.
2. Set up the Python harness: `cd harness && pip install -e .[dev]`.
3. Baseline check: `cli-judge validate ../fixtures` and `cli-judge selftest` must pass unmodified.
4. Execute the Work Breakdown WB0–WB9 in order; close the loop with WB3–WB5 first.
5. If you also maintain a CLI-Anything or Printing Press tool, wire `adapters/cli_anything_adapter.py` / `adapters/pp_cli_adapter.py` (WB6) and score your own tool — that is the intended dogfood loop.
6. Constraints: measure-don't-generate; record/assert-only safety; reality-traceable scoring; minimal deps.
7. Done = `/AGENTS.md` Definition of Done + green CI.
