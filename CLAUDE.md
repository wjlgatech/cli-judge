# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

**CLI-Judge** — a reality-grounded benchmark + verification harness that scores
agent-native CLIs, MCP servers, and software harnesses on *outcomes* (does the tool produce
correct, safe, token-efficient results against real captured payloads?) rather than *structure*
(does the source contain the right patterns?). The repo is shipped as a self-contained brief to
be handed to a coding agent, plus a runnable Python reference harness that is **still a skeleton**.

The authoritative documents, in reading order: `SPEC.md` (what it measures) → `RUBRIC.md` (exact
point allocations) → `AGENTS.md` (the build brief, work breakdown WB0–WB9, definition of done).
`AGENTS.md` is the source of truth for *what to build and in what order* — defer to it.

## Two non-negotiable invariants

1. **CLI-Judge measures tools; it never generates them.** Reject any change that drifts toward building
   a CLI/MCP generator — the entire thesis is being the referee, not a third player. (`AGENTS.md`
   "Out of scope", `README.md` "Scope discipline".)
2. **The Reality Principle (SPEC §2).** Every point a scorer awards must trace to (a) the tool's
   real stdout/stderr/exit-code from a subprocess run, (b) its behavior replayed against a
   *recorded real upstream payload*, or (c) an independently verifiable property of its declared
   capability envelope. **Never** award a point because "a string exists in source code" — that is
   the structural-scorecard trap CLI-Judge exists to escape. A check passable by editing a comment is a
   fixture bug.

## Build status (important — most of the harness is stubbed)

`cli-judge validate` and `cli-judge selftest` are wired and pass. The replay engine, the five scorers, the
full runner, the capability-envelope/receipt verifier, and real adapters are **TODO** (marked
inline with `Status:` headers and `WBn` tags). `cli-judge selftest` currently prints `F (26.1)` because
the scorers are stubs — that is expected until WB4 lands, not a regression. Each module's docstring
states its status; grep `TODO (WB` to find open work.

## Commands

All harness commands run **from the `harness/` directory** (it is a subdir; the package resolves
the repo root via `ROOT = parents[2]`, so paths like `../fixtures` are relative to `harness/`).

```bash
cd harness
python3 -m venv .venv && source .venv/bin/activate
pip install -e .            # hard dep: jsonschema only.  pip install -e .[dev] adds pytest/ruff/mypy
                            # optional extra: .[receipts] (cryptography, for D4 signed-receipt verification)

cli-judge validate ../fixtures   # validate every *.task.json / *.fixture.json against schemas/ (must exit 0)
cli-judge run --adapter examples/echo_adapter.py --suite core   # run a suite -> report.json + scorecard.md + Grade
cli-judge selftest               # echo adapter through the core suite; prints {grade, score}

pytest -q                  # unit tests (tests/test_loader.py, tests/test_selftest.py)
pytest -q tests/test_loader.py::<name>    # single test
```

CI (`.github/workflows/cli-judge.yml`) runs exactly: `cli-judge validate ../fixtures`, `cli-judge selftest`, `pytest -q`.

`cli-judge run` exit codes: `0` on grade A–D, `2` on F. The runner loads adapters by **executing the
adapter file and reading a module-level `ADAPTER` instance** — every adapter must define one.

## Architecture

Pipeline (one tool-specific seam, the adapter; everything else is generic):

```
adapter ──> runner ──> replay engine ──> scorers ──> report
 (per TUT)   loads suite+   serves recorded   5 dimension   report.json (machine)
             fixtures,      upstream payload   scorers       + scorecard.md (human)
             drives adapter  offline           (pts,max,findings)  + "Grade: X (n/100)"
```

- **Adapter** (`harness/cli_judge/adapter.py`, real ones in `harness/cli_judge/../adapters/`): the only
  tool-specific code. Implements `invoke(Call) -> Result` and optional `capability_envelope()`.
  `Call`/`Result`/`UpstreamObservation` are the frozen ABI dataclasses. `invoke` must **never raise
  on a non-zero tool exit** — capture it in `Result.exit_code`. When `Call.replay_base_url` is set,
  the adapter must route the tool's upstream traffic there so it runs its real code path offline.
- **Runner** (`runner.py`): resolves suite → tasks → fixtures, drives the adapter (through the
  replay engine for `http_replay`/`subprocess_transcript` fixtures), dispatches to scorers.
- **Replay engine** (`replay.py`): stdlib `http.server` only — returns the recorded response *and*
  records what the tool actually sent upstream, so D1 scorers assert on the real request. Keep it
  dependency-free and deterministic; no network in the core suite.
- **Scorers** (`scorers/`): one per dimension, registered via `@register("Dn")` into `SCORERS`.
  Each consumes `(task, fixture, result)` and returns a `ScoreResult(points, max, findings)`.
  `_assertlib.py` holds the shared assertion kinds (`upstream_request_query`, `stdout_json_path`, …).
- **Report** (`report.py`): aggregates, applies grade bands and the D4 hard gate, normalizes to 100.

### The five dimensions (RUBRIC has exact point tables — follow them precisely; points are frozen within a minor version)
D1 Correctness-against-reality (35) · D2 Non-interactive robustness (20) · D3 Cross-platform
survival (15) · **D4 Destructive-action safety (20, record/assert only)** · D5 Token & latency
efficiency (10). **D4 is a hard gate: any `blocker`-severity D4 finding caps the overall grade at
C** regardless of total points (`report._letter`).

## Data model & conventions

- **Tasks** (`*.task.json`) and **fixtures** (`*.fixture.json`) live under `fixtures/d1..d5/`,
  conform to `schemas/`, and each carry real `provenance` (e.g. `cli-printing-press#2961`). Fixtures
  are distilled from real observed failures across the two CLI-factory issue trackers; the backlog
  to convert is `fixtures/CATALOG.md`. Synthetic-only tasks must be marked `synthetic: true` and are
  excluded from headline scores.
- **Suites** (`suites/*.yaml`): currently the loader maps a suite *name* → dimension-prefix filter
  over task ids (`load_suite`'s `prefix_map`); it does **not yet parse the YAML** (WB1 TODO). The
  YAML files document intent; changing a suite's membership means editing both until the parser lands.
- **Fixtures are data, never code — never `eval` fixture content.** All randomness seeded, all
  fixture timestamps frozen, so reports are deterministic for a given (suite, adapter, fixture-set).
- **Findings are structured**: `{severity: blocker|friction|note, code, message, evidence}`.
- Python 3.10+, standard-library-first, every public function typed, `ruff`/`mypy` clean if present.
- Add a task/fixture/adapter from `templates/`. Per-agent entry notes are in `BUILD_INSTRUCTIONS/`.

## Repo-wide workflow rule (from global policy)

This repo keeps a `CHANGELOG.md` (Keep-a-Changelog). On any change to feature behavior, an API/CLI
surface (`cli-judge` subcommands, the adapter ABI, schemas), or a scoring rule, add an `## [Unreleased]`
changelog line (what + why) and sync the doc it touches — `SPEC.md`/`RUBRIC.md` for measurement
changes, `AGENTS.md` for build-order/DoD changes, this file for architecture/command changes.
