# Fixture Catalog — distilled from real observed failures

Every fixture below is distilled from a **real, observed failure** in one of the two leading agent-CLI generators, mined from their public issue trackers (CLI Printing Press: 877 closed issues; CLI-Anything: 68 closed issues, plus open security issues). The catalog is the authoritative list; `*.fixture.json` + `*.task.json` pairs are the machine-readable encodings. Seeds are provided; WB8 expands the rest.

Provenance keys:
- `pp#N` = mvanhorn/cli-printing-press issue N
- `ca#N` = HKUDS/CLI-Anything issue N

## D1 — Correctness-against-reality

| ID | Failure observed | Provenance | Seed provided |
|----|------------------|-----------|---------------|
| d1.pagination.offset_param_fidelity | Offset paginators got cursor-style param name instead of spec's skip/limit | pp#2961, pp#2949 | YES |
| d1.auth.jwt_no_length_floor | `looksLikeJWT` had no length floor -> short opaque tokens misclassified as JWT | pp#1598 | YES |
| d1.compact.no_raw_map_leak | `--compact` leaked nested objects/arrays as raw `map[...]` strings | pp#2950 | YES |
| d1.query.multi_value_preserved | MCP envelope dropped multi-value query params | pp#2965 | no (WB8) |
| d1.serialize.json_vs_ndjson | `workflow archive --json` emitted NDJSON, failed json_fidelity | pp#1254 | no (WB8) |
| d1.routing.per_endpoint_base_url | sync ignored per-endpoint base_url override -> wrong host -> 403 | pp#2966 | no (WB8) |

## D2 — Non-interactive robustness

| ID | Failure observed | Provenance | Seed provided |
|----|------------------|-----------|---------------|
| d2.noninteractive.kdenlive_mode | Non-interactive mode not working | ca#214 | YES |
| d2.json.empty_result | `--json fs ls` yielded no return results | ca#217 | no (WB8) |
| d2.repl.banner_signature | `print_banner()` called with arg it doesn't accept -> TypeError on startup | ca#278 | no (WB8) |
| d2.dryrun.no_mutation | `sync --dry-run` mutated sync_state on dependent resources | pp#2935 | no (WB8) |

## D3 — Cross-platform survival

| ID | Failure observed | Provenance | Seed provided |
|----|------------------|-----------|---------------|
| d3.path.windows_escape | Windows path escape bug in render script | ca-blender#343 | YES |
| d3.binary.macos_libpath | LibreOffice headless crashes on macOS: missing library path | ca#221, ca#242 | no (WB8) |
| d3.exe.windows_suffix | ValidationBinary missing .exe suffix on Windows | pp#877 | no (WB8) |

## D4 — Destructive-action safety

| ID | Failure observed | Provenance | Seed provided |
|----|------------------|-----------|---------------|
| d4.injection.macro_output_path | Code injection via unsanitized output_path in macro generation | ca-freecad#282 | YES |
| d4.receipt.signed_command | Community RFC: signed receipts for CLI agent commands (absent today) | ca#185 | YES |
| d4.confirm.destructive_token | Destructive op proceeded on bare flag, no scoped confirmation | (design gap, both) | no (WB8) |
| d4.path.traversal | Token-file path traversal / symlink escape | ca-sketch#304 | no (WB8) |

## D5 — Token & latency efficiency

| ID | Failure observed | Provenance | Seed provided |
|----|------------------|-----------|---------------|
| d5.context.generation_overflow | Generation agent blew its own context window on large target | ca#192 | YES (as efficiency note) |
| d5.compact.token_reduction | `--compact` claims 60-80% reduction; verify against real payload | pp (claimed) | no (WB8) |

## How to add a fixture
See `templates/fixture.template.json` and `templates/task.template.json`. Each new fixture MUST carry real provenance or be flagged `"synthetic": true`.
