"""Tests for the assertion library (WB4)."""
from cli_judge.adapter import Result, UpstreamObservation
from cli_judge.scorers import _assertlib as A


def _res(**kw):
    base = dict(exit_code=0, stdout="", stderr="", duration_ms=1.0)
    base.update(kw)
    return Result(**base)


def test_resolve_path_nested_index_and_length():
    doc = {"items": [{"id": "a"}, {"id": "b"}], "meta": {"total": 9}}
    assert A.resolve_path(doc, "$.items[0].id") == "a"
    assert A.resolve_path(doc, "$.items.length") == 2
    assert A.resolve_path(doc, "meta.total") == 9
    assert A.resolve_path(doc, "$.missing.key") is A._MISSING


def test_stdout_json_path_ops():
    r = _res(stdout='{"items": [1, 2, 3], "name": "x"}')
    assert A.run_assert(r, {"kind": "stdout_json_path", "path": "$.items.length", "op": ">", "value": 0})[0]
    assert A.run_assert(r, {"kind": "stdout_json_path", "path": "name", "op": "equals", "value": "x"})[0]
    assert not A.run_assert(r, {"kind": "stdout_json_path", "path": "nope", "op": "exists"})[0]


def test_stdout_json_path_on_non_json_does_not_raise():
    r = _res(stdout="not json at all")
    ok, ev = A.run_assert(r, {"kind": "stdout_json_path", "path": "x", "op": "exists"})
    assert ok is False and "not JSON" in ev


def test_exit_code_and_never_prompted():
    assert A.run_assert(_res(exit_code=4), {"kind": "exit_code", "equals": 4})[0]
    assert not A.run_assert(_res(exit_code=0), {"kind": "exit_code", "equals": 4})[0]
    assert A.run_assert(_res(prompted=False), {"kind": "never_prompted"})[0]
    assert not A.run_assert(_res(prompted=True), {"kind": "never_prompted"})[0]


def test_no_log_on_stdout():
    assert A.run_assert(_res(stdout='{"ok": true}'), {"kind": "no_log_on_stdout"})[0]
    assert A.run_assert(_res(stdout=""), {"kind": "no_log_on_stdout"})[0]
    assert not A.run_assert(_res(stdout="INFO booting...\n{}"), {"kind": "no_log_on_stdout"})[0]


def test_timing_and_tokens():
    assert A.run_assert(_res(duration_ms=10.0), {"kind": "completes_within_ms", "ms": 50})[0]
    assert not A.run_assert(_res(duration_ms=99.0), {"kind": "completes_within_ms", "ms": 50})[0]
    assert A.run_assert(_res(stdout="x" * 40), {"kind": "tokens_within_budget", "budget": 20})[0]


def test_token_reduction():
    r = _res(stdout="x" * 100, artifacts={"compare_stdout": "x" * 30})
    assert A.run_assert(r, {"kind": "token_reduction_at_least", "fraction": 0.6})[0]
    assert not A.run_assert(r, {"kind": "token_reduction_at_least", "fraction": 0.9})[0]


def test_upstream_multi_value_and_path():
    obs = UpstreamObservation(method="GET", path="/v1/items",
                              query={"tag": ["a", "b", "c"]})
    r = _res(upstream=obs)
    assert A.run_assert(r, {"kind": "upstream_request_query_multi", "param": "tag", "values": ["a", "c"]})[0]
    assert A.run_assert(r, {"kind": "upstream_request_path", "equals": "/v1/items"})[0]


def test_receipt_emitted_and_field():
    r = _res(receipt={"tool": "t", "blast_radius": "reversible"})
    assert A.run_assert(r, {"kind": "receipt_emitted"})[0]
    assert A.run_assert(r, {"kind": "receipt_field_present", "field": "blast_radius"})[0]
    assert not A.run_assert(_res(), {"kind": "receipt_emitted"})[0]


def test_no_code_execution_observed():
    assert A.run_assert(_res(stdout="all good"), {"kind": "no_code_execution_observed", "sentinel": "PWNED"})[0]
    assert not A.run_assert(_res(stderr="...PWNED..."), {"kind": "no_code_execution_observed", "sentinel": "PWNED"})[0]


def test_unknown_kind_is_explicit_not_exception():
    ok, ev = A.run_assert(_res(), {"kind": "totally_made_up"})
    assert ok is False and "unimplemented" in ev
