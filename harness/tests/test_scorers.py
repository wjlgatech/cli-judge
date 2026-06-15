"""Tests for the dimension scorers (WB4). D4 has its own section appended in U6."""
from cli_judge.adapter import Result, UpstreamObservation
from cli_judge.scorers import SCORERS


def _res(**kw):
    base = dict(exit_code=0, stdout="", stderr="", duration_ms=1.0)
    base.update(kw)
    return Result(**base)


def _task(dimension, asserts, points=5):
    return {"id": f"{dimension.lower()}.x", "dimension": dimension,
            "assert": asserts, "points": points}


def test_d1_full_points_when_all_pass():
    obs = UpstreamObservation(method="GET", path="/v1/issues",
                              query={"skip": ["50"], "limit": ["50"]})
    r = _res(stdout='{"items": [1, 2]}', upstream=obs)
    task = _task("D1", [
        {"kind": "upstream_request_query", "param": "skip", "equals": "50"},
        {"kind": "upstream_request_query_absent", "param": "after"},
        {"kind": "stdout_json_path", "path": "$.items.length", "op": ">", "value": 0},
    ], points=7)
    sr = SCORERS["D1"](task, {}, r)
    assert sr.points == 7.0
    assert sr.findings == []


def test_d1_zero_and_finding_when_one_assert_fails():
    obs = UpstreamObservation(method="GET", path="/v1/issues", query={"after": ["cursor"]})
    r = _res(stdout="{}", upstream=obs)
    task = _task("D1", [{"kind": "upstream_request_query_absent", "param": "after"}], points=7)
    sr = SCORERS["D1"](task, {}, r)
    assert sr.points == 0.0
    assert len(sr.findings) == 1
    assert sr.findings[0].code == "D1_UPSTREAM_REQUEST_QUERY_ABSENT"
    assert sr.findings[0].severity == "friction"


def test_d2_noninteractive_pass():
    r = _res(stdout='{"ok": true}', exit_code=0, prompted=False, duration_ms=10.0)
    task = _task("D2", [
        {"kind": "completes_within_ms", "value": 5000},
        {"kind": "never_prompted"},
        {"kind": "exit_code", "equals": 0},
        {"kind": "stdout_is_json"},
    ])
    assert SCORERS["D2"](task, {}, r).points == 5.0


def test_d3_loud_failure_is_correct_behavior():
    # Backend absent: tool exits non-zero with install guidance on stderr.
    r = _res(exit_code=3, stdout="", stderr="LibreOffice not found; install it")
    task = _task("D3", [
        {"kind": "exit_code", "equals": 3},
        {"kind": "stderr_contains", "value": "install"},
        {"kind": "stdout_not_contains", "value": "ERROR-WRONG-OUTPUT"},
    ])
    assert SCORERS["D3"](task, {}, r).points == 5.0


def test_d5_token_budget():
    r = _res(stdout="x" * 40)
    task = _task("D5", [{"kind": "tokens_within_budget", "budget": 20}], points=4)
    assert SCORERS["D5"](task, {}, r).points == 4.0
    task_fail = _task("D5", [{"kind": "tokens_within_budget", "budget": 5}], points=4)
    assert SCORERS["D5"](task_fail, {}, r).points == 0.0
