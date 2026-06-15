"""Shared assertion primitives used by the dimension scorers.

Each function returns (ok: bool, evidence: str). Implement TODOs (WB4).
These map 1:1 to the 'kind' values used in *.task.json 'assert' arrays.
"""
from __future__ import annotations
import json
import re
from typing import Any


def _json_or_none(s: str):
    try:
        return json.loads(s)
    except Exception:
        return None


def stdout_is_json(result, _a) -> tuple[bool, str]:
    v = _json_or_none(result.stdout)
    return (v is not None, "stdout parsed as JSON" if v is not None else "stdout not valid JSON")


def stdout_not_contains(result, a) -> tuple[bool, str]:
    needle = a["value"]
    bad = needle in result.stdout
    return (not bad, f"found '{needle}' in stdout" if bad else f"'{needle}' absent")


def stdout_json_path(result, a) -> tuple[bool, str]:
    # Minimal dotless path: top-level key only for the skeleton.
    # TODO (WB4): support real JSONPath ($.items.length, etc.).
    doc = _json_or_none(result.stdout)
    if doc is None:
        return (False, "stdout not JSON")
    val = doc.get(a["path"]) if isinstance(doc, dict) else None
    op = a.get("op", "exists")
    if op == "exists":
        return (val is not None, f"{a['path']}={val!r}")
    if op == "equals":
        return (val == a.get("value"), f"{a['path']}={val!r} expected {a.get('value')!r}")
    if op == "array_len_gt":
        ok = isinstance(val, list) and len(val) > a.get("value", 0)
        return (ok, f"len={len(val) if isinstance(val,list) else 'n/a'}")
    if op == "is_object_or_absent":
        return (val is None or isinstance(val, dict), f"{a['path']} type={type(val).__name__}")
    return (False, f"unknown op {op}")


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


def upstream_request_header(result, a) -> tuple[bool, str]:
    obs = result.upstream
    if obs is None:
        return (False, "no upstream observation")
    val = obs.headers.get(a["header"], "")
    ok = bool(re.search(a["matches"], val))
    return (ok, f"{a['header']}={val!r}")


# TODO (WB4): exit_code, completes_within_ms, never_prompted, token_reduction_at_least,
# receipt_emitted, receipt_signature_verifies, no_code_execution_observed, etc.

DISPATCH = {
    "stdout_is_json": stdout_is_json,
    "stdout_not_contains": stdout_not_contains,
    "stdout_json_path": stdout_json_path,
    "upstream_request_query": upstream_request_query,
    "upstream_request_query_absent": upstream_request_query_absent,
    "upstream_request_header": upstream_request_header,
}


def run_assert(result, a) -> tuple[bool, str]:
    fn = DISPATCH.get(a["kind"])
    if fn is None:
        return (False, f"unimplemented assert kind: {a['kind']} (WB4)")
    return fn(result, a)
