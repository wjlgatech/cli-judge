from cli_judge.runner import run_suite
from cli_judge.loader import ROOT


def test_selftest_runs():
    adapter = str(ROOT / "harness" / "examples" / "echo_adapter.py")
    report = run_suite(adapter, "core")
    assert "grade" in report
    assert "score" in report
    # Deterministic: running twice yields same score.
    report2 = run_suite(adapter, "core")
    assert report["score"] == report2["score"]
