"""Golden snapshot of the core scorecard (WB9).

Guards against unintended scoring regressions: the echo adapter through the
core suite must reproduce a committed scorecard byte-for-byte. The scorecard
carries only deterministic points/findings (no wall-clock latency, per KTD7),
so it is stable across runs and machines.

Regenerate intentionally after a deliberate scoring change:

    CLI_JUDGE_REGEN_GOLDEN=1 pytest tests/test_golden.py
"""
import os
from pathlib import Path

from cli_judge.runner import run_suite
from cli_judge.loader import ROOT

GOLDEN = Path(__file__).parent / "golden" / "core_scorecard.md"


def test_core_scorecard_matches_golden():
    adapter = str(ROOT / "harness" / "examples" / "echo_adapter.py")
    scorecard = run_suite(adapter, "core")["_scorecard_md"]

    if os.environ.get("CLI_JUDGE_REGEN_GOLDEN"):
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(scorecard, encoding="utf-8")

    assert GOLDEN.exists(), "golden missing; regenerate with CLI_JUDGE_REGEN_GOLDEN=1"
    assert scorecard == GOLDEN.read_text(encoding="utf-8"), (
        "core scorecard drifted from golden. If this change is intentional, "
        "regenerate: CLI_JUDGE_REGEN_GOLDEN=1 pytest tests/test_golden.py"
    )
