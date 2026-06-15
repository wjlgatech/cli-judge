# Build Instructions — Generic Coding Agent

You have been handed the **CLI-Judge** package. Your job: complete the reference harness so `cli-judge run` produces a scored report against real-world failure fixtures.

## Step 0 — Orient (do this first)
1. Read `/AGENTS.md` (root) end to end. It contains the authoritative Work Breakdown (WB0–WB9) and Definition of Done.
2. Read `/SPEC.md` and `/RUBRIC.md` for what is being measured and the exact point tables.
3. Skim `/fixtures/CATALOG.md` — every fixture is distilled from a real issue; preserve that discipline.

## Step 1 — Make it run
```
cd harness
python3 -m venv .venv && . .venv/bin/activate
pip install -e .[dev]
cli-judge validate ../fixtures      # must pass on provided fixtures (WB1)
cli-judge selftest                  # must produce a grade via the echo adapter
```
If either fails, fix WB0/WB1 before anything else.

## Step 2 — Implement in WB order
Do **WB3 (replay) -> WB4 (scorers) -> WB5 (runner/report)** first; that closes the loop. Then WB6 (real adapters), WB7 (receipts), WB8 (expand fixtures), WB9 (CI).

## Step 3 — Prove it
- `pytest -q` green.
- `cli-judge run --adapter examples/echo_adapter.py --suite core` is deterministic.
- Add at least 6 more fixtures from `fixtures/CATALOG.md` rows marked "no (WB8)", each with real provenance.

## Hard rules
- Never turn CLI-Judge into a generator.
- Never execute a destructive command against a live system. D4 is record/assert only.
- Standard library first; only `jsonschema` is a hard dep. Document any addition.
- Every awarded point must trace to a real execution or a recorded real payload (Reality Principle, SPEC §2).

## Definition of Done
See `/AGENTS.md` "Definition of Done". Stop when all boxes are checked and the golden scorecard is committed.
