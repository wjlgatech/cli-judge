# ATB reference harness (skeleton)

This is the runnable skeleton of the AgentTool-Bench harness. It is **intentionally incomplete**: the replay engine and scorers contain enumerated TODOs for a coding agent to finish (see ../AGENTS.md "Work Breakdown").

## Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
atb --help
```

## Commands
- `atb validate <dir>` — validate every task/fixture against the JSON schemas.
- `atb run --adapter <file.py> --suite <name>` — run a suite against an adapter, emit report.json + scorecard.md.
- `atb selftest` — run the echo adapter through the core suite to prove the pipeline wires up.

## Layout
- `atb/cli.py` — argument parsing + command dispatch (wired)
- `atb/loader.py` — load suites/tasks/fixtures (partially wired; TODOs)
- `atb/adapter.py` — Call/Result/Adapter ABI (wired)
- `atb/replay.py` — replay engine (TODO: WB3)
- `atb/runner.py` — orchestration (TODO: WB5)
- `atb/scorers/` — five dimension scorers (TODO: WB4)
- `atb/report.py` — report.json + scorecard.md (partially wired)
- `examples/echo_adapter.py` — trivial adapter for self-test (wired enough to run)
- `adapters/` — real adapters for pp-cli and cli-anything (TODO: WB6)
- `tests/` — pytest suite (add as you implement)
