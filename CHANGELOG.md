# Changelog

## [Unreleased]
### Added
- **Completed the reference harness to the Definition of Done** (was a stubbed skeleton). Real replay engine (request matching, live upstream capture, 404 loud-fail, subprocess-transcript support); full assertion library with minimal JSONPath; all five dimension scorers driven by real evidence; Ed25519 receipt verification + hash-chain with graceful crypto-absent degradation; D4 hard-gate (blocker caps grade at C); suite YAML parsing with `include:` composition; runner capability-envelope + `compare_call` wiring; per-dimension report rollup. `cli-judge run --suite full` now produces a real, deterministic grade.
- Real adapters `pp_cli_adapter` (replay base-url wiring via `API_BASE_URL`/`BASE_URL`/`PP_BASE_URL`, overridable with `CLI_JUDGE_PP_BASE_URL_ENV`) and `cli_anything_adapter` (one-shot non-interactive invocation), both skipping cleanly when their binary env var is unset.
- Expanded the fixture catalog: 10 new fixture+task pairs (D1 multi-value/serialization/routing, D2 empty-result/banner/dry-run, D3 macOS-libpath/Windows-exe-suffix, D4 confirm-token/path-traversal), each with real provenance; `full` now covers every committed task.
- Golden core scorecard snapshot test (`tests/test_golden.py` + `tests/golden/core_scorecard.md`) to catch scoring regressions; regenerate with `CLI_JUDGE_REGEN_GOLDEN=1`. CI workflow renamed `atb.yml` → `cli-judge.yml` and runs validate + selftest + pytest (which includes the golden).

### Changed
- **Renamed the project from AgentTool-Bench (`atb`) to CLI-Judge (`cli-judge`).** Importable Python package `atb` → `cli_judge`; CLI command and distribution `atb` → `cli-judge`; schema `$id` host `agenttool-bench.dev` → `cli-judge.dev` (non-resolving identifier); adapter env vars `ATB_PP_BINARY`/`ATB_CA_COMMAND` → `CLI_JUDGE_PP_BINARY`/`CLI_JUDGE_CA_COMMAND`; confirmation token env `ATB_CONFIRM` → `CLI_JUDGE_CONFIRM`. Rationale: clearer product name; full rename keeps package/command/docs/schemas consistent. Removed the unused `yaml` optional extra (suites will be parsed by a stdlib subset parser, no pyyaml dependency).

## v0.1.0
- Initial package: SPEC, RUBRIC, JSON schemas, runnable harness skeleton (validate + selftest wired; replay/scorers/runner stubbed with TODOs), seed fixtures distilled from real issues across both leading factories, per-agent build instructions, strategy/threat-model/methodology/roadmap docs, CI workflow, Apache-2.0.
