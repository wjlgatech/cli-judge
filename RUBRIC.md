# CLI-Judge Scoring Rubric v0.1

Total: **100 points**, distributed across five dimensions. Each dimension lists scored checks with exact point values. A scorer awards points only on evidence per the Reality Principle (SPEC §2).

Letter grades: **A** >= 85, **B** >= 70, **C** >= 55, **D** >= 40, **F** < 40.
**Hard safety gate:** any `blocker`-severity finding in D4 caps the final grade at **C**.

---

## D1 — Correctness-against-reality (35 pts)

| Check | Pts | Awarded when |
|------|-----|--------------|
| Pagination param fidelity | 7 | Replayed request uses the spec's real param names/shape (offset/cursor) for next-page; provenance: pp#2961, pp#2949 |
| Auth token classification | 5 | No false JWT-positive on short opaque token; no length-floor bug; provenance: pp#1598 |
| `--compact`/`--json` no raw-map leak | 6 | Nested objects/arrays serialize as JSON, never `map[...]` strings; provenance: pp#2950 |
| Multi-value query preserved | 4 | Repeated/array query params all reach upstream; provenance: pp#2965 |
| Serialization contract (JSON vs NDJSON) | 4 | Output matches the declared shape; provenance: pp#1254 |
| `--select` field fidelity | 5 | Returns exactly requested typed fields, correct types (string IDs not ints) |
| Per-endpoint base_url honored | 4 | Replayed request hits the correct host when an override exists; provenance: pp#2966 |

## D2 — Non-interactive robustness (20 pts)

| Check | Pts | Awarded when |
|------|-----|--------------|
| Runs with no TTY, never prompts | 5 | Piped invocation completes without blocking on input; provenance: ca#214 |
| Valid JSON in `--json`/piped mode | 5 | stdout is parseable JSON; no banner contamination; provenance: ca#217 |
| Typed exit codes | 4 | success/usage/not-found/auth/upstream/rate-limit map to distinct documented codes |
| `--dry-run` mutates nothing, returns plan | 3 | No state change; structured plan returned; provenance: pp#2935 |
| No log/banner on stdout machine path | 3 | Diagnostics go to stderr only |

## D3 — Cross-platform survival (15 pts)

| Check | Pts | Awarded when |
|------|-----|--------------|
| Windows/space/unicode path handling | 5 | Paths with backslashes/spaces/unicode handled correctly; provenance: ca-blender#343 |
| No hard-coded OS-only binary paths | 4 | Resolves upstream binary via discovery, not a fixed path; provenance: ca#221, ca#242 |
| Encoding/locale correctness | 3 | UTF-8 round-trips; non-integer-decimal locale safe; CRLF/LF tolerant |
| Loud typed failure when backend absent | 3 | Fails with install guidance + correct exit code; never silently emits wrong output |

## D4 — Destructive-action safety (20 pts)  *(hard gate)*

| Check | Pts | Awarded when |
|------|-----|--------------|
| Capability envelope present & valid | 5 | Each command declares blast radius per schema |
| Destructive ops gated by explicit token | 5 | Mutation requires a scoped confirmation token, not bare `--yes` |
| Signed receipt emitted | 4 | Ed25519-signed append-only receipt of the action; provenance: ca#185 |
| Input sanitization (no injection) | 6 | Path/template/command inputs sanitized; provenance: ca-freecad#282 (command injection), ca-sketch (path traversal) |

## D5 — Token & latency efficiency (10 pts)

| Check | Pts | Awarded when |
|------|-----|--------------|
| Tokens-per-task within archetype budget | 4 | Output payload (proxy-tokenized) <= budget for the task archetype |
| `--compact` reduces tokens as claimed | 3 | Measured reduction >= claimed margin, no required field dropped |
| p50 local-path latency within budget | 3 | Offline/local read path p50 <= budget |

---

## Scoring procedure

1. Load suite -> resolve tasks -> bind fixtures.
2. For each task: drive adapter (with replay engine if fixture is `http_replay`/`subprocess_transcript`), collect `Result`.
3. Run the dimension scorer; it emits `(points, max, findings[])` per check.
4. Aggregate; apply D4 hard gate; normalize to 100 by suite weights.
5. Emit `report.json` + `scorecard.md` + `Grade: X (n/100)`.

## Anti-gaming rules

- A check is **only** scored if its fixture has real `provenance`. Synthetic checks are excluded from headline scores and labeled.
- No check rewards source-string presence. If a check can be passed by editing a comment, it is mis-specified — file a fixture bug.
- Point values are frozen within a minor version so scores stay comparable over time.
