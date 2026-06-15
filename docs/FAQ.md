# FAQ

**Is ATB a generator?** No. It measures tools; it never generates them. That scope discipline is the moat.

**Why not just extend the existing scorecards?** They are structural by design (and their own docs admit it). ATB's value is being independent and outcome-based — a referee, not a contestant.

**Does scoring need network access?** No. The core suite replays recorded payloads offline. Live mode is opt-in and read-only.

**Where's the crypto/web3?** There isn't any, by design. The one cryptographic primitive is Ed25519-signed, hash-chained receipts (a local append-only log). No token, no chain. See docs/STRATEGY.md.

**Can it score my hand-built CLI / MCP server?** Yes — write an adapter (templates/adapter.template.py). Adapters are the only tool-specific code.

**How do you prevent gaming?** Points only count with real provenance; no check rewards source-string presence; point values frozen within a minor version. See RUBRIC "Anti-gaming rules".

**What does 'done' mean for a coding agent?** See /AGENTS.md "Definition of Done".

**How big is the lift to finish the harness?** The skeleton runs today (validate + selftest). Closing the scoring loop is WB3–WB5; expect that to be the bulk of the work. Everything else is additive.
