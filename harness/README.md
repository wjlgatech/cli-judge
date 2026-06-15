# CLI-Judge reference harness

The runnable CLI-Judge harness. The full pipeline is implemented (replay engine,
five scorers, signed receipts, suite resolution, runner, report); `cli-judge run`
produces a real, deterministic, reality-grounded grade.

## Install
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .                 # hard dep: jsonschema
pip install -e '.[receipts]'     # optional: cryptography, for D4 Ed25519 receipt verification
cli-judge --help
```

## Commands
- `cli-judge validate <dir>` — validate every task/fixture against the JSON schemas.
- `cli-judge run --adapter <file.py> --suite <name>` — run a suite against an adapter, emit report.json + scorecard.md + a grade.
- `cli-judge selftest` — run the echo adapter through the core suite to prove the pipeline wires up.

## Layout
- `cli_judge/cli.py` — argument parsing + command dispatch
- `cli_judge/loader.py` — load + validate suites/tasks/fixtures; parse suite YAML with `include:` composition
- `cli_judge/adapter.py` — Call/Result/Adapter ABI
- `cli_judge/replay.py` — replay engine (request matching, live upstream capture, 404 loud-fail, transcript)
- `cli_judge/runner.py` — orchestration (replay + envelope + compare_call + scoring)
- `cli_judge/scorers/` — five dimension scorers + `_assertlib.py` (the assertion kinds)
- `cli_judge/envelope.py` — capability-envelope validation + Ed25519 signed-receipt verification
- `cli_judge/report.py` — report.json + scorecard.md with per-dimension rollup
- `examples/echo_adapter.py` — trivial adapter for self-test
- `adapters/` — real adapters for pp-cli (`CLI_JUDGE_PP_BINARY`) and cli-anything (`CLI_JUDGE_CA_COMMAND`)
- `tests/` — pytest suite, including `tests/golden/core_scorecard.md` (regenerate: `CLI_JUDGE_REGEN_GOLDEN=1 pytest tests/test_golden.py`)
