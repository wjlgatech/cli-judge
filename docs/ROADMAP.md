# Roadmap

## v0.1 (this package)
Spec, rubric, schemas, runnable skeleton, seed fixtures, per-agent build briefs. Goal: a coding agent can complete the harness and score the echo adapter.

## v0.2 — Real adapters + full fixture coverage
- WB6 adapters scoring a real `*-pp-cli` and a real `cli-anything-*`.
- Expand every CATALOG row to a concrete fixture (WB8).
- Publish first comparative scorecard (both factories through ATB).

## v0.3 — The paper
arXiv submission: introduce ATB, methodology, and the comparative results. The benchmark's distribution mechanism.

## v0.4 — Verification layer (open core)
- Replay verifier as a standalone library both factories can run in their own CI.
- Capability envelope + signed receipts reference implementation (WB7 hardened).

## v1.0 — Control plane (commercial, separate repo)
- Hosted receipt audit, fleet policy enforcement, telemetry-driven regeneration signal, sandboxed/remote execution.
- Open-core boundary: local verifier + benchmark free; org-scale governance paid.

## Explicitly not on the roadmap
A code generator. A token/chain. Live scraping of third-party services for scoring.
