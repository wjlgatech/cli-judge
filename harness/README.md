# CLI-Judge reference harness (skeleton)

This is the runnable skeleton of the CLI-Judge harness. It is **intentionally incomplete**: the replay engine and scorers contain enumerated TODOs for a coding agent to finish (see ../AGENTS.md "Work Breakdown").

## Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
cli-judge --help
```

## Commands
- `cli-judge validate <dir>` — validate every task/fixture against the JSON schemas.
- `cli-judge run --adapter <file.py> --suite <name>` — run a suite against an adapter, emit report.json + scorecard.md.
- `cli-judge selftest` — run the echo adapter through the core suite to prove the pipeline wires up.

## Layout
- `cli_judge/cli.py` — argument parsing + command dispatch (wired)
- `cli_judge/loader.py` — load suites/tasks/fixtures (partially wired; TODOs)
- `cli_judge/adapter.py` — Call/Result/Adapter ABI (wired)
- `cli_judge/replay.py` — replay engine (TODO: WB3)
- `cli_judge/runner.py` — orchestration (TODO: WB5)
- `cli_judge/scorers/` — five dimension scorers (TODO: WB4)
- `cli_judge/report.py` — report.json + scorecard.md (partially wired)
- `examples/echo_adapter.py` — trivial adapter for self-test (wired enough to run)
- `adapters/` — real adapters for pp-cli and cli-anything (TODO: WB6)
- `tests/` — pytest suite (add as you implement)
