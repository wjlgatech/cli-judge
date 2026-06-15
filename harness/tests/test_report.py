"""Tests for report aggregation, per-dimension rollup, and determinism (WB5)."""
import json

from cli_judge.adapter import Result
from cli_judge.scorers import ScoreResult, Finding
from cli_judge.report import build_report
from cli_judge.runner import run_suite
from cli_judge.loader import ROOT


def _res():
    return Result(exit_code=0, stdout="{}", stderr="", duration_ms=1.0)


def test_per_dimension_rollup_sums_match_task_totals():
    results = [
        {"task": {"id": "d1.a", "dimension": "D1"}, "result": _res(), "score": ScoreResult(7.0, 7.0, [])},
        {"task": {"id": "d1.b", "dimension": "D1"}, "result": _res(), "score": ScoreResult(0.0, 5.0, [])},
        {"task": {"id": "d2.a", "dimension": "D2"}, "result": _res(), "score": ScoreResult(5.0, 5.0, [])},
    ]
    report = build_report("core", "t", results, safety_blocker=False)
    assert report["dimensions"]["D1"] == {"points": 7.0, "max_points": 12.0}
    assert report["dimensions"]["D2"] == {"points": 5.0, "max_points": 5.0}
    assert report["points"] == 12.0 and report["max_points"] == 17.0


def test_safety_cap_annotation_rendered():
    results = [{"task": {"id": "d4.a", "dimension": "D4"}, "result": _res(),
               "score": ScoreResult(0.0, 6.0, [Finding("blocker", "X", "m", "")])}]
    report = build_report("safety", "t", results, safety_blocker=True)
    assert "capped at C by safety gate" in report["_scorecard_md"]


def test_run_suite_is_deterministic():
    adapter = str(ROOT / "harness" / "examples" / "echo_adapter.py")
    r1 = run_suite(adapter, "core")
    r2 = run_suite(adapter, "core")
    r1.pop("_scorecard_md")
    r2.pop("_scorecard_md")
    # report.json carries no volatile latency -> byte-identical across runs
    assert json.dumps(r1, sort_keys=True) == json.dumps(r2, sort_keys=True)
