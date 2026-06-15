# Strategy: why benchmark-first, and what it unlocks

## The bet
The agent-tool space already has two excellent *factories* — CLI Printing Press (web APIs -> Go CLIs + MCP) and CLI-Anything (desktop software -> Python CLIs). Generation is no longer the bottleneck. The bottleneck is everything downstream: verifying tools against reality, running them safely, composing them, and improving them from real use.

Competing as a third factory means out-engineering two mature, fast-moving projects on their home turf. Low ROI. Instead, become the **referee**: define how agent-tool quality is measured, and own the verification + trust layer that both ecosystems plug into.

## Why a benchmark is the highest-ROI first move
- **Cheap relative to leverage.** You build a measuring stick, not a better generator.
- **Category-defining.** Whoever defines the metric shapes the field's incentives (cf. ImageNet, SWE-bench, MMLU).
- **Evidence-backed.** Both factories' own scorecards are *structural*; their issue trackers prove real-world correctness leaks (pagination params, JWT misclassification, macOS crashes, broken non-interactive modes). CLI-Judge measures exactly those gaps.
- **Lowest-capital thesis test.** If the field ignores the benchmark, you spent weeks, not years, and learned the trust-layer thesis is premature.

## Sequencing (highest ROI -> lower)
1. **Benchmark + paper (bundle them).** The paper is the benchmark's distribution. One arXiv artifact: introduce CLI-Judge, run both factories through it, publish the gap.
2. **Open-source the harness (this repo).** Make it trivial for both factories to score themselves. When they cite CLI-Judge scores, you are the referee.
3. **Open-core runtime/verification layer.** The replay verifier + capability envelope + signed receipts. Individually useful, organizationally necessary.
4. **Commercial control plane (last).** Hosted audit of receipts, fleet policy enforcement, telemetry-driven regeneration signal, sandboxed/remote execution. The operationally-heavy part nobody open-sources.

## On crypto/web3 (explicitly cut)
The only defensible primitive is tamper-evident audit of agent actions. That is plain Ed25519 + a hash-chained append-only log (see schemas/receipt.schema.json). No token, no chain, no wallet. A web3 framing here is a credibility tax that repels the exact infra/enterprise buyers who want a trust layer. Do not add it.

## One-line positioning
We are not building a better tool factory — we are building the trust layer for the agent-tool economy, starting with the benchmark that proves it's needed.
