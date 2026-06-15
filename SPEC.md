# CLI-Judge — Specification v0.1

## 0. Purpose & non-goals

CLI-Judge scores how well an *agent-native tool* (a generated CLI, an MCP server, or a software harness) performs against **reality**, not against its own spec. It is a benchmark and a verification harness. It is **not** a generator and never wraps a model.

Non-goals: generating tools; ranking the underlying LLMs; live-scraping third-party services; anything on-chain.

## 1. Definitions

- **Tool-under-test (TUT)**: the thing being scored — e.g. `linear-pp-cli`, `cli-anything-blender`, an MCP server.
- **Adapter**: tool-specific glue that normalizes a TUT into CLI-Judge's call ABI (`Call -> Result`).
- **Task**: one scored unit of work. Has an input call (or call sequence), a fixture binding, expected outcome assertions, and a dimension tag.
- **Fixture**: committed, real-world data used to make a task deterministic — a recorded upstream HTTP interaction, a recorded subprocess transcript, a platform/encoding variant, or a destructive-action declaration. Fixtures are **distilled from real, observed failures** (see `fixtures/CATALOG.md`).
- **Suite**: a named ordered set of tasks (`suites/core.yaml`, `suites/safety.yaml`, ...).
- **Replay**: serving a recorded upstream response to the TUT so it executes its real code path against a real payload, offline.

## 2. The reality principle

Every point CLI-Judge awards must be traceable to one of:
(a) the TUT's actual stdout/stderr/exit-code from a real subprocess execution, or
(b) the TUT's behavior when replayed against a **recorded real upstream payload**, or
(c) a static property of the TUT's **declared capability envelope** that is independently verifiable.

A point may **never** be awarded for "a pattern exists in source code." That is the structural-scorecard trap CLI-Judge exists to escape.

## 3. The five dimensions

### D1. Correctness-against-reality (35 pts)
Replay the TUT against a recorded real upstream response and assert the *typed* output is correct. Targets the Printing Press failure family:
- Pagination param fidelity (offset vs cursor; `skip`/`limit` vs `after`).
- Auth token classification (no false JWT positives on short opaque tokens).
- Output fidelity: `--compact` / `--json` must not leak raw `map[...]` / nested objects as strings; multi-value query params preserved.
- Serialization correctness: NDJSON vs JSON array where the contract demands one.
- Field-selection (`--select`) returns exactly the requested typed fields.

### D2. Non-interactive robustness (20 pts)
The TUT must work as an agent would call it. Targets the CLI-Anything failure family:
- Runs with no TTY / piped stdin/stdout; never blocks on a prompt.
- `--json` (or auto-JSON when piped) returns valid, parseable JSON.
- Correct, typed exit codes (success / usage / not-found / auth / upstream / rate-limit).
- `--dry-run` performs no mutation and returns a plan.
- No banner/log text contaminates machine output on stdout.

### D3. Cross-platform survival (15 pts)
Fixtures encode platform/locale/encoding variants. Targets macOS/Windows breakage:
- Path handling (Windows backslash escaping, spaces, unicode paths).
- No hard-coded library/exe paths that only resolve on the author's OS.
- Locale/encoding: UTF-8 in/out, non-integer-decimal locales, CRLF vs LF.
- Graceful, typed failure with install guidance when an upstream binary is absent (must FAIL loudly, never silently degrade to wrong output).

### D4. Destructive-action safety (20 pts)
Record/assert only — CLI-Judge never actually mutates a live target.
- TUT declares a **capability envelope** classifying each command's blast radius (read-only / reversible / destructive).
- Destructive ops require an explicit confirmation token, not a bare `--yes`.
- TUT emits a **signed receipt** (Ed25519) of what it did, to an append-only log.
- No injection footguns: command/path/template inputs are sanitized (targets FreeCAD macro injection, Sketch path traversal classes).

### D5. Token & latency efficiency (10 pts)
- Tokens-per-successful-task (measured on output payload size with a documented tokenizer proxy) vs a per-archetype budget.
- p50 wall-clock latency for the local/offline path vs a budget.
- `--compact` actually reduces token count by the claimed margin without losing required fields.

## 4. Task format

A task is a JSON file (`*.task.json`) conforming to `schemas/task.schema.json`. Minimal shape:

```json
{
  "id": "d1.pagination.offset_param_fidelity",
  "dimension": "D1",
  "title": "Offset paginator must use spec param names, not cursor names",
  "fixture": "fixtures/d1/pagination_offset.fixture.json",
  "call": { "argv": ["issues", "list", "--limit", "50", "--page", "2", "--json"] },
  "assert": [
    { "kind": "upstream_request_query", "param": "skip", "equals": "50" },
    { "kind": "upstream_request_query", "param": "limit", "equals": "50" },
    { "kind": "stdout_json_path", "path": "$.items.length", "op": ">", "value": 0 }
  ],
  "points": 7,
  "provenance": "cli-printing-press#2961"
}
```

## 5. Fixture format

A fixture (`*.fixture.json`, schema `schemas/fixture.schema.json`) carries the recorded reality. Types:
- `http_replay`: a recorded request matcher + response (status, headers, body) for the replay engine.
- `subprocess_transcript`: recorded argv -> {stdout, stderr, exit} for tools whose backend is another CLI.
- `platform_variant`: declares OS/locale/encoding and the expected normalized behavior.
- `destructive_decl`: the expected capability classification + required confirmation contract.

Every fixture has `provenance` linking to the real issue/observation it was distilled from, so the benchmark is auditable and non-fabricated in spirit.

## 6. Suites

- `core`: D1+D2 (correctness + non-interactive) — the everyday quality bar.
- `safety`: D4 — the trust gate (must pass for any production claim).
- `portability`: D3.
- `efficiency`: D5.
- `full`: all of the above.

## 7. Grading

Score = sum of awarded points across the tasks in the suite, normalized to 100 per the RUBRIC weights. Letter grade: A>=85, B>=70, C>=55, D>=40, F<40. A **hard gate**: any `blocker` finding in D4 (safety) caps the overall grade at C regardless of points — an unsafe tool is not shippable no matter how correct.

## 8. Reporting

`report.json` (full machine record: per-task points, findings, evidence) and `scorecard.md` (human summary table + top findings). Both are deterministic for a given (suite, adapter, fixture-set).

## 9. Versioning & governance

CLI-Judge is versioned (`vMAJOR.MINOR`). Fixtures are additive within a minor version. A task's point value never silently changes within a minor version. New failure families enter as new tasks, never by re-weighting old ones — so historical scores stay comparable. Governance: a fixture is only admitted with real provenance; synthetic-only tasks are marked `synthetic: true` and excluded from headline scores.
