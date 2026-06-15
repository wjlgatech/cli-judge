# Changelog

## [Unreleased]
### Changed
- **Renamed the project from AgentTool-Bench (`atb`) to CLI-Judge (`cli-judge`).** Importable Python package `atb` → `cli_judge`; CLI command and distribution `atb` → `cli-judge`; schema `$id` host `agenttool-bench.dev` → `cli-judge.dev` (non-resolving identifier); adapter env vars `ATB_PP_BINARY`/`ATB_CA_COMMAND` → `CLI_JUDGE_PP_BINARY`/`CLI_JUDGE_CA_COMMAND`; confirmation token env `ATB_CONFIRM` → `CLI_JUDGE_CONFIRM`. Rationale: clearer product name; full rename keeps package/command/docs/schemas consistent. Removed the unused `yaml` optional extra (suites will be parsed by a stdlib subset parser, no pyyaml dependency).

## v0.1.0
- Initial package: SPEC, RUBRIC, JSON schemas, runnable harness skeleton (validate + selftest wired; replay/scorers/runner stubbed with TODOs), seed fixtures distilled from real issues across both leading factories, per-agent build instructions, strategy/threat-model/methodology/roadmap docs, CI workflow, Apache-2.0.
