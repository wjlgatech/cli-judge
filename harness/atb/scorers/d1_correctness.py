"""D1 — Correctness-against-reality scorer.

All-or-nothing per task by default: award task['points'] if every assert passes.
TODO (WB4): support partial credit per RUBRIC where a task has weighted sub-checks.
"""
from __future__ import annotations
from . import register, ScoreResult, Finding
from ._assertlib import run_assert


@register("D1")
def score(task, fixture, result) -> ScoreResult:
    max_p = float(task["points"])
    findings = []
    ok_all = True
    for a in task["assert"]:
        ok, ev = run_assert(result, a)
        if not ok:
            ok_all = False
            findings.append(Finding("friction", "D1_ASSERT", f"{a['kind']} failed", ev))
    return ScoreResult(points=max_p if ok_all else 0.0, max_points=max_p, findings=findings)
