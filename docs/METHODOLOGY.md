# Methodology: how fixtures are sourced (so the benchmark stays honest)

## The Reality Principle
Every scored point traces to (a) a real subprocess execution, (b) the tool's behavior replayed against a recorded **real** upstream payload, or (c) an independently verifiable property of the tool's declared capability envelope. Never to "a pattern exists in source."

## Fixture provenance
Fixtures are distilled from observed failures in the two leading factories' public issue trackers (CLI Printing Press: 877 closed issues; CLI-Anything: 68 closed + open security issues, mined directly). Each fixture's `provenance` field links to its origin. Fixtures with no real provenance are flagged `synthetic: true` and excluded from headline scores.

## Why this beats structural scorecards
- CLI Printing Press scorecard checks "path exists in spec", "table has read+write path". But specs lie; the bugs live in spec-vs-reality (pagination param names, JWT floors, compact map-leaks). Replay against the real payload catches them.
- CLI-Anything ships 2,461 tests, but they are written by the same generator that wrote the code and pass on the author's machine. Cross-platform/non-interactive fixtures catch what self-authored happy-path tests miss.

## Adding fixtures responsibly
1. Find a real failure (issue, retro, observed run).
2. Capture the minimal real payload / transcript that reproduces the correct-vs-wrong distinction.
3. Encode it per templates/, with provenance.
4. Write the task assertion against the REAL request/output, not against source.
5. Freeze point value within the minor version so scores stay comparable.

## Governance
- Additive within a minor version; never silently re-weight.
- New failure families enter as new tasks.
- A fixture PR without provenance (or a `synthetic:true` flag) is rejected.
