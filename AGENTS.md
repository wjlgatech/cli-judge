# AGENTS.md — Build Brief for Coding Agents

You are building **AgentTool-Bench (ATB)**, a reality-grounded benchmark + verification harness for agent-native CLIs / MCP servers / software harnesses. This file is your single source of truth for *what to build and in what order*. Read `SPEC.md` and `RUBRIC.md` for the *what it measures*, then return here for the *work*.

## Prime directives

1. **ATB measures tools; it does not generate them.** Reject any task that drifts toward building a code generator.
2. **Reality over structure.** Every score must trace to a real captured payload or a real subprocess execution — never to "this string exists in a file."
3. **Deterministic and offline by default.** The core suite runs against recorded fixtures with no network. Live mode is opt-in and read-only.
4. **Safe by construction.** The harness must never execute a destructive command against a live system during scoring. Destructive-action tests run in record/assert mode only.
5. **Small, typed, tested.** Prefer standard library. The only hard dependency is `jsonschema`. Keep the dependency surface tiny.

## Architecture (target)

```
adapter (per tool-under-test)  ->  ATB runner  ->  replay engine  ->  scorers  ->  report
        |                              |               |               |            |
   normalizes a tool          loads suite +     matches tool I/O    5 dimension   JSON + md
   into ATB's call ABI        fixtures          to fixtures         scorers       scorecard
```

- **Adapter**: a small Python file exposing `invoke(call) -> Result`. It is how ATB talks to *any* tool (a Go pp-cli binary, a Python cli-anything harness, an MCP server, a mock). Adapters are the only tool-specific code.
- **Runner**: loads a suite (`suites/*.yaml`), resolves its tasks + fixtures, drives the adapter, collects raw results.
- **Replay engine**: for record/replay fixtures, serves the recorded upstream response so the tool-under-test runs against *real captured payloads* with zero network.
- **Scorers**: five dimension scorers (see RUBRIC). Each returns `(points, max, findings[])`.
- **Report**: writes `report.json` (machine) and `scorecard.md` (human), plus a one-line grade.

## The five scoring dimensions (see RUBRIC.md for points)

1. **Correctness-against-reality (35)** — does the tool produce the right typed output when replayed against a real captured upstream payload?
2. **Non-interactive robustness (20)** — does it work piped, with `--json`, no TTY, no prompts, exit codes correct?
3. **Cross-platform survival (15)** — does it behave correctly across path/OS/locale/encoding variations encoded in fixtures?
4. **Destructive-action safety (20)** — does it gate, declare, and make reversible any mutating/destructive operation? (record/assert only)
5. **Token & latency efficiency (10)** — tokens-per-successful-task and p50 latency vs. a budget.

## Work Breakdown (build in this order)

- [ ] **WB0 — Bootstrap.** Create the Python package per `harness/` skeleton. `pip install -e harness` must succeed and `atb --help` must run. (Skeleton provided; wire up entrypoints.)
- [ ] **WB1 — Schema validation.** Implement `atb validate <dir>`: load every `*.task.json` and `*.fixture.json`, validate against `schemas/`. Provided fixtures must pass.
- [ ] **WB2 — Adapter ABI.** Finalize `harness/atb/adapter.py`: the `Call`, `Result` dataclasses and the `Adapter` protocol. Implement `examples/echo_adapter.py` (a trivial adapter that lets the harness self-test end-to-end without any real tool).
- [ ] **WB3 — Replay engine.** Implement `harness/atb/replay.py`: given a fixture with a recorded upstream interaction, expose it to the adapter (env var pointing at a local replay socket/file, or injected response). Deterministic, no network.
- [ ] **WB4 — Scorers.** Implement the five scorers in `harness/atb/scorers/`. Each consumes (task, fixture, result) and emits `(points, max, findings)`. Follow RUBRIC point tables exactly.
- [ ] **WB5 — Runner + report.** Implement `atb run --adapter <file> --suite <name>`: orchestrate WB2–WB4, write `report.json` + `scorecard.md`, print `Grade: <A-F> (<score>/100)`.
- [ ] **WB6 — Real adapters.** Implement `adapters/pp_cli_adapter.py` (wraps a Printing Press `<api>-pp-cli` binary) and `adapters/cli_anything_adapter.py` (wraps a `cli-anything-<software>` command). These let ATB score the two real ecosystems.
- [ ] **WB7 — Capability envelope + receipts.** Implement `harness/atb/envelope.py`: parse/emit the capability envelope (schemas/capability_envelope.schema.json) and verify signed receipts (Ed25519 via `cryptography` — optional extra). This powers the Destructive-action safety scorer.
- [ ] **WB8 — Fixture expansion.** Convert every entry in `fixtures/CATALOG.md` into a concrete `*.fixture.json` + `*.task.json` pair following `templates/`. The provided ones are seeds; expand to full coverage.
- [ ] **WB9 — CI + golden report.** Add a GitHub Actions workflow that runs `atb validate` and `atb run --adapter examples/echo_adapter.py` on push, and snapshots a golden `scorecard.md`.

## Definition of Done

- `atb validate ./fixtures` exits 0 on all provided fixtures.
- `atb run --adapter examples/echo_adapter.py --suite core` produces a `report.json` and `scorecard.md` and a printed grade, deterministically (same input -> same output).
- All five scorers implemented with unit tests; `pytest` green.
- At least one real adapter (WB6) runs end-to-end against a real tool if a binary is provided; otherwise it skips cleanly with a clear message.
- No network access in the core suite. No destructive command ever executed against a live target.

## Conventions

- Python 3.10+. Standard library first. Hard deps: `jsonschema`. Optional extras: `cryptography` (receipts), `pyyaml` (suites — or ship a tiny YAML subset parser to stay dependency-free; your choice, document it).
- Every public function typed. `ruff`/`mypy` clean if available.
- Fixtures are data, never code. Never `eval` fixture content.
- All randomness seeded. All timestamps in fixtures are frozen.
- Findings are structured: `{severity: blocker|friction|note, code: str, message: str, evidence: str}`.

## Out of scope (do not build)

- A CLI/MCP generator of any kind.
- Anything requiring a blockchain, token, or wallet. (Signed receipts use plain Ed25519 + an append-only log file. That is the only cryptography.)
- Scraping live third-party services during scoring. Fixtures are pre-recorded and committed.
