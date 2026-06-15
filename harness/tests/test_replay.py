"""Tests for the replay engine (WB3)."""
import json
import urllib.request

from cli_judge.replay import replay_for


def _get(url: str):
    with urllib.request.urlopen(url, timeout=3) as resp:
        return resp.status, resp.read().decode("utf-8")


def test_matching_request_gets_recorded_response_and_is_observed():
    fixture = {
        "type": "http_replay",
        "match": {"method": "GET", "path": "/v1/issues"},
        "response": {"status": 200, "headers": {"Content-Type": "application/json"},
                     "body": {"items": [{"id": "iss_1"}]}},
    }
    with replay_for(fixture) as sess:
        status, body = _get(sess.base_url + "/v1/issues?skip=50&limit=50")
        assert status == 200
        assert json.loads(body)["items"][0]["id"] == "iss_1"
    # The engine captured the REAL request the client made.
    assert sess.observation is not None
    assert sess.observation.query.get("skip") == ["50"]
    assert sess.observation.query.get("limit") == ["50"]


def test_nonmatching_path_returns_404_but_is_still_observed():
    fixture = {
        "type": "http_replay",
        "match": {"method": "GET", "path": "/v1/issues"},
        "response": {"status": 200, "body": {"items": []}},
    }
    with replay_for(fixture) as sess:
        try:
            _get(sess.base_url + "/v1/WRONG")
            raised = None
        except urllib.error.HTTPError as e:  # type: ignore[attr-defined]
            raised = e.code
    assert raised == 404, "wrong path must fail loudly, not get the recorded body"
    assert sess.observation.path == "/v1/WRONG"  # still recorded for D3 asserts


def test_multiple_sequential_requests_all_captured_in_order():
    fixture = {
        "type": "http_replay",
        "match": {"path": "/data"},
        "response": {"status": 200, "body": {"ok": True}},
    }
    with replay_for(fixture) as sess:
        _get(sess.base_url + "/data?page=1")
        _get(sess.base_url + "/data?page=2")
    assert len(sess.observations) == 2
    assert sess.observations[0].query["page"] == ["1"]
    assert sess.observations[1].query["page"] == ["2"]


def test_subprocess_transcript_exposes_transcript_no_server():
    fixture = {"type": "subprocess_transcript",
               "transcript": {"render --out x": {"stdout": "done", "exit": 0}}}
    with replay_for(fixture) as sess:
        assert sess.base_url is None
        assert sess.transcript["render --out x"]["exit"] == 0


def test_non_replay_fixture_yields_none():
    with replay_for({"type": "platform_variant"}) as sess:
        assert sess is None
