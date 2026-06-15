"""Shared assertion primitives used by the dimension scorers.

Each function returns (ok: bool, evidence: str). These map 1:1 to the 'kind'
values used in *.task.json 'assert' arrays. Every assertion reads only the
real `Result` (stdout/stderr/exit/duration/prompted/upstream/receipt/artifacts)
or a recorded `UpstreamObservation` — never source text. That is the Reality
Principle made executable.

Status: WIRED (WB4).
"""
from __future__ import annotations
import json
import re
from typing import Any

_MISSING = object()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _json_or_none(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def token_proxy(s: str) -> int:
    """Documented tokenizer proxy: ~4 chars per token (OpenAI-ish heuristic).
    Deterministic and dependency-free; used by D5 token checks."""
    return max(1, len(s) // 4) if s else 0


def _split_indices(seg: str):
    """'items[0][2]' -> ('items', [0, 2]); '[1]' -> ('', [1])."""
    m = re.match(r"^([^\[\]]*)((?:\[\d+\])*)$", seg)
    if not m:
        return seg, []
    name = m.group(1)
    idxs = [int(n) for n in re.findall(r"\[(\d+)\]", m.group(2))]
    return name, idxs


def resolve_path(doc: Any, path: str):
    """Minimal JSONPath: '$.a.b', '$.items[0].id', trailing '.length'.
    Dotless top-level keys ('items') also work (back-compat). Returns _MISSING
    when any segment is absent."""
    p = path
    if p.startswith("$"):
        p = p[1:]
    if p.startswith("."):
        p = p[1:]
    if p == "":
        return doc
    cur = doc
    for seg in p.split("."):
        if seg == "length":
            if isinstance(cur, (list, str, dict)):
                cur = len(cur)
                continue
            return _MISSING
        name, idxs = _split_indices(seg)
        if name:
            if isinstance(cur, dict) and name in cur:
                cur = cur[name]
            else:
                return _MISSING
        for i in idxs:
            if isinstance(cur, list) and 0 <= i < len(cur):
                cur = cur[i]
            else:
                return _MISSING
    return cur


def _cmp(op: str, got, want) -> bool:
    try:
        if op in (">", "gt"):
            return got > want
        if op in ("<", "lt"):
            return got < want
        if op in (">=", "gte"):
            return got >= want
        if op in ("<=", "lte"):
            return got <= want
    except TypeError:
        return False
    return False


# ---------------------------------------------------------------------------
# stdout / stderr assertions
# ---------------------------------------------------------------------------
def stdout_is_json(result, _a) -> tuple[bool, str]:
    v = _json_or_none(result.stdout)
    return (v is not None, "stdout parsed as JSON" if v is not None else "stdout not valid JSON")


def stdout_not_contains(result, a) -> tuple[bool, str]:
    needle = a["value"]
    bad = needle in result.stdout
    return (not bad, f"found '{needle}' in stdout" if bad else f"'{needle}' absent")


def stdout_contains(result, a) -> tuple[bool, str]:
    needle = a["value"]
    return (needle in result.stdout, f"'{needle}' {'present' if needle in result.stdout else 'absent'} in stdout")


def stdout_matches(result, a) -> tuple[bool, str]:
    ok = bool(re.search(a["pattern"], result.stdout))
    return (ok, f"/{a['pattern']}/ {'matched' if ok else 'did not match'} stdout")


def stderr_contains(result, a) -> tuple[bool, str]:
    needle = a["value"]
    return (needle in result.stderr, f"'{needle}' {'present' if needle in result.stderr else 'absent'} in stderr")


def stderr_matches(result, a) -> tuple[bool, str]:
    ok = bool(re.search(a["pattern"], result.stderr))
    return (ok, f"/{a['pattern']}/ {'matched' if ok else 'did not match'} stderr")


def no_log_on_stdout(result, _a) -> tuple[bool, str]:
    """Machine path must be clean: stdout is empty or pure JSON. Banners/logs
    belong on stderr."""
    s = result.stdout.strip()
    ok = (s == "") or (_json_or_none(result.stdout) is not None)
    return (ok, "stdout is clean (empty or JSON)" if ok else "stdout carries non-JSON log/banner text")


def stdout_json_path(result, a) -> tuple[bool, str]:
    doc = _json_or_none(result.stdout)
    if doc is None:
        return (False, "stdout not JSON")
    val = resolve_path(doc, a["path"])
    op = a.get("op", "exists")
    present = val is not _MISSING
    shown = "<missing>" if not present else repr(val)
    if op == "exists":
        return (present and val is not None, f"{a['path']}={shown}")
    if op == "equals":
        return (present and val == a.get("value"), f"{a['path']}={shown} expected {a.get('value')!r}")
    if op == "array_len_gt":
        ok = isinstance(val, list) and len(val) > a.get("value", 0)
        return (ok, f"len={len(val) if isinstance(val, list) else 'n/a'} > {a.get('value', 0)}")
    if op == "is_object_or_absent":
        return (not present or val is None or isinstance(val, dict), f"{a['path']} type={type(val).__name__ if present else 'absent'}")
    if op in (">", "<", ">=", "<=", "gt", "lt", "gte", "lte"):
        return (present and _cmp(op, val, a.get("value")), f"{a['path']}={shown} {op} {a.get('value')!r}")
    return (False, f"unknown op {op}")


# ---------------------------------------------------------------------------
# exit / interactivity / timing  (D2, D5)
# ---------------------------------------------------------------------------
def exit_code(result, a) -> tuple[bool, str]:
    want = a.get("equals", a.get("value"))
    return (result.exit_code == want, f"exit={result.exit_code} expected {want}")


def never_prompted(result, _a) -> tuple[bool, str]:
    return (not result.prompted, "blocked on a prompt" if result.prompted else "never prompted")


def completes_within_ms(result, a) -> tuple[bool, str]:
    budget = a.get("ms", a.get("value"))
    ok = result.duration_ms <= budget
    return (ok, f"{result.duration_ms:.0f}ms vs budget {budget}ms")


def tokens_within_budget(result, a) -> tuple[bool, str]:
    n = token_proxy(result.stdout)
    budget = a["budget"]
    return (n <= budget, f"~{n} tokens vs budget {budget}")


def token_reduction_at_least(result, a) -> tuple[bool, str]:
    """Compare the primary stdout against the --compact stdout the runner
    captured from the task's compare_call (stashed in artifacts)."""
    base = result.stdout
    compact = result.artifacts.get("compare_stdout")
    if compact is None:
        return (False, "no compare_call output captured (runner must run compare_call)")
    b, c = token_proxy(base), token_proxy(compact)
    if b == 0:
        return (False, "baseline output empty")
    reduction = (b - c) / b
    want = a["fraction"]
    return (reduction >= want, f"reduction {reduction:.0%} vs claimed {want:.0%}")


# ---------------------------------------------------------------------------
# upstream-request assertions  (D1)
# ---------------------------------------------------------------------------
def upstream_request_query(result, a) -> tuple[bool, str]:
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    got = obs.query.get(a["param"], [])
    ok = a.get("equals") in got
    return (ok, f"query {a['param']}={got} expected {a.get('equals')}")


def upstream_request_query_absent(result, a) -> tuple[bool, str]:
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    return (a["param"] not in obs.query, f"{a['param']} present={a['param'] in obs.query}")


def upstream_request_query_multi(result, a) -> tuple[bool, str]:
    """All declared values for a repeated/array param reached upstream."""
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    got = obs.query.get(a["param"], [])
    want = a["values"]
    ok = all(v in got for v in want)
    return (ok, f"{a['param']}={got} expected superset of {want}")


def upstream_request_path(result, a) -> tuple[bool, str]:
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    return (obs.path == a["equals"], f"path={obs.path!r} expected {a['equals']!r}")


def upstream_request_header(result, a) -> tuple[bool, str]:
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    val = obs.headers.get(a["header"], "")
    ok = bool(re.search(a["matches"], val))
    return (ok, f"{a['header']}={val!r}")


# ---------------------------------------------------------------------------
# safety assertions  (D4) — receipts delegate to envelope (graceful if crypto absent)
# ---------------------------------------------------------------------------
def receipt_emitted(result, _a) -> tuple[bool, str]:
    return (result.receipt is not None, "receipt emitted" if result.receipt else "no receipt emitted")


def receipt_field_present(result, a) -> tuple[bool, str]:
    r = result.receipt or {}
    field = a["field"]
    return (field in r, f"receipt.{field} {'present' if field in r else 'absent'}")


def receipt_signature_verifies(result, _a) -> tuple[bool, str]:
    if not result.receipt:
        return (False, "no receipt to verify")
    from ..envelope import verify_receipt
    return verify_receipt(result.receipt)


def receipt_chain_intact(result, _a) -> tuple[bool, str]:
    if not result.receipt:
        return (False, "no receipt to chain-check")
    from ..envelope import verify_chain
    log = result.artifacts.get("receipt_log")
    return verify_chain(result.receipt, log)


def no_code_execution_observed(result, a) -> tuple[bool, str]:
    """A sentinel that would appear only if injected input were executed must be
    absent from every observable surface."""
    sentinel = a.get("sentinel", "PWNED")
    surfaces = result.stdout + result.stderr + "".join(result.artifacts.values())
    bad = sentinel in surfaces
    return (not bad, f"sentinel '{sentinel}' {'LEAKED — injection ran' if bad else 'absent'}")


def artifact_not_contains(result, a) -> tuple[bool, str]:
    content = result.artifacts.get(a["artifact"], "")
    needle = a["value"]
    bad = needle in content
    return (not bad, f"'{needle}' in artifact {a['artifact']}" if bad else f"'{needle}' absent from artifact")


# ---------------------------------------------------------------------------
DISPATCH = {
    "stdout_is_json": stdout_is_json,
    "stdout_not_contains": stdout_not_contains,
    "stdout_contains": stdout_contains,
    "stdout_matches": stdout_matches,
    "stderr_contains": stderr_contains,
    "stderr_matches": stderr_matches,
    "no_log_on_stdout": no_log_on_stdout,
    "stdout_json_path": stdout_json_path,
    "exit_code": exit_code,
    "never_prompted": never_prompted,
    "completes_within_ms": completes_within_ms,
    "tokens_within_budget": tokens_within_budget,
    "token_reduction_at_least": token_reduction_at_least,
    "upstream_request_query": upstream_request_query,
    "upstream_request_query_absent": upstream_request_query_absent,
    "upstream_request_query_multi": upstream_request_query_multi,
    "upstream_request_path": upstream_request_path,
    "upstream_request_header": upstream_request_header,
    "receipt_emitted": receipt_emitted,
    "receipt_field_present": receipt_field_present,
    "receipt_signature_verifies": receipt_signature_verifies,
    "receipt_chain_intact": receipt_chain_intact,
    "no_code_execution_observed": no_code_execution_observed,
    "artifact_not_contains": artifact_not_contains,
}


def run_assert(result, a) -> tuple[bool, str]:
    fn = DISPATCH.get(a["kind"])
    if fn is None:
        return (False, f"unimplemented assert kind: {a['kind']}")
    return fn(result, a)
