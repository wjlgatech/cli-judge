"""Five dimension scorers. Each: score(task, fixture, result) -> ScoreResult.

Status: WIRED (WB4). Each scorer follows the exact point tables in
../../RUBRIC.md and emits structured findings. Per RUBRIC, every rubric row is
its own task, so scoring is all-or-nothing PER TASK: award the task's full
points only when every assertion passes (no sub-task partial-credit layer is
needed — see plan KTD4). D4 is the exception (it has a hard-gate path).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Finding:
    severity: str   # blocker | friction | note
    code: str
    message: str
    evidence: str = ""


@dataclass
class ScoreResult:
    points: float
    max_points: float
    findings: list[Finding] = field(default_factory=list)


# Registry filled by each scorer module on import.
SCORERS: dict[str, Callable] = {}


def register(dimension: str):
    def deco(fn):
        SCORERS[dimension] = fn
        return fn
    return deco


def score_all_or_nothing(task, result, dimension: str) -> ScoreResult:
    """Shared scoring for the non-safety dimensions: every assertion must pass
    to earn the task's points; each failure becomes a friction finding tagged
    with the assertion kind so the scorecard is actionable."""
    from ._assertlib import run_assert

    max_p = float(task["points"])
    findings: list[Finding] = []
    ok_all = True
    for a in task["assert"]:
        ok, ev = run_assert(result, a)
        if not ok:
            ok_all = False
            findings.append(Finding("friction", f"{dimension}_{a['kind'].upper()}",
                                    f"{a['kind']} failed", ev))
    return ScoreResult(points=max_p if ok_all else 0.0, max_points=max_p, findings=findings)


# Import side-effect registration.
from . import d1_correctness, d2_noninteractive, d3_portability, d4_safety, d5_efficiency  # noqa: E402,F401
