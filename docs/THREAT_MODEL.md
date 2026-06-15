# Threat model (D4 safety dimension)

ATB's safety dimension exists because generated tools hand agents real capability with thin guardrails. Observed, real failure classes:

| Threat | Real provenance | ATB control |
|--------|-----------------|-------------|
| Code injection via unsanitized arg interpolated into a generated macro/script | CLI-Anything FreeCAD #282 | d4.injection.* asserts no execution / input escaped; blocker finding caps grade |
| Path traversal / symlink escape in token/file handling | CLI-Anything Sketch #304 | d4.path.traversal fixture (WB8) |
| Destructive op fires on a bare flag with no scoped consent | design gap, both | capability envelope + confirmation-token gating |
| No audit trail of what an agent did | CLI-Anything RFC #185 | Ed25519 signed, hash-chained receipts (schemas/receipt.schema.json) |
| Silent wrong output when a backend is missing | CLI-Anything macOS #221/#242 | D3 requires loud, typed failure with install guidance |

## Design principles
1. **Declare before you do.** Every command carries a capability envelope (blast radius, reads/writes, reversibility).
2. **Consent is scoped and explicit.** Destructive actions need a confirmation token bound to the specific action, not a global `--yes`.
3. **Everything is receipted.** Mutations emit a signed, chained receipt. Verification needs only a public key. No central service required for the *local* guarantee; the commercial control plane aggregates receipts across a fleet.
4. **Inputs are data, never code.** Fixtures and tool inputs are never `eval`'d; tools must escape/parameterize, not interpolate.
5. **ATB never mutates.** Scoring is record/assert. The benchmark cannot itself become an attack vector.

## Non-goals
ATB does not sandbox the tool-under-test at runtime (that is the commercial control plane's job). ATB *scores whether the tool declares and respects* the safety contract.
