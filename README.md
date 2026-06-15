# AgentTool-Bench (ATB)

**A reality-grounded benchmark and verification harness for agent-native CLIs, MCP servers, and software harnesses.**

> Existing generators (CLI Printing Press, CLI-Anything) score tools on *structure* — does the code contain the right patterns? ATB scores tools on *outcomes* — does the tool produce correct, safe, token-efficient results against **real** captured payloads, in non-interactive mode, across platforms?

This repository is a **complete, self-contained brief** designed to be handed to a coding agent (Hermes, Claude Code, Codex, Gemini CLI, etc.). It contains the benchmark specification, scoring rubric, a runnable reference harness skeleton, real-world failure fixtures distilled from 945+ closed issues across the two leading generators, and per-agent build instructions.

## Why this exists (the one-paragraph thesis)

Both leading agent-CLI factories fail in the gap between what a tool *claims* (its spec / its README) and what it *does* against reality. CLI Printing Press's recurring bugs cluster on spec-vs-reality mismatch (pagination param names, JWT misclassification, `--compact` leaking raw maps, multi-value query drops). CLI-Anything's recurring bugs cluster on environment fragility (macOS/Windows breakage, broken non-interactive mode, generation context overflow) and generated-code security (path traversal, command injection). Neither project's own scorecard catches these, because both scorecards are structural. ATB is the missing measuring stick: replay real interactions, score real outcomes.

## What's in this package

| Path | Purpose |
|------|---------|
| `SPEC.md` | The full benchmark specification — dimensions, task format, fixture format |
| `RUBRIC.md` | The 100-point scoring rubric with exact point allocations and pass gates |
| `AGENTS.md` | **Start here if you are a coding agent.** Build order, conventions, definition of done |
| `BUILD_INSTRUCTIONS/` | Per-agent entry instructions (Claude Code, Codex, Gemini, Hermes, generic) |
| `fixtures/` | Real-world failure fixtures distilled from the two issue trackers |
| `harness/` | Runnable Python reference harness skeleton (replay engine, scorer, CLI) |
| `schemas/` | JSON Schemas for tasks, fixtures, capability envelope, signed receipts |
| `docs/` | Strategy, threat model, methodology, roadmap, FAQ |
| `templates/` | Templates for adding a new task / fixture / adapter |
| `LICENSE` | Apache-2.0 |

## Quick start (for a human)

```bash
cd harness
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
atb --help
atb validate ./fixtures            # validate all fixtures against schema
atb run --adapter examples/echo_adapter.py --suite core   # run the core suite
```

## Quick start (for a coding agent)

Read `AGENTS.md`, then `BUILD_INSTRUCTIONS/<your-agent>.md`. Build in the order listed. The reference harness is a **skeleton with TODOs** — your job is to complete the replay engine and scorers so that `atb run` produces a scored report. Every TODO is enumerated in `AGENTS.md` under "Work Breakdown."

## Scope discipline (read this)

ATB measures tools. ATB is **not** another generator and must never become one. If a contribution adds a code generator, it's out of scope. The defensible position is being the referee, not a third player.

## License

Apache-2.0. See `LICENSE`.
