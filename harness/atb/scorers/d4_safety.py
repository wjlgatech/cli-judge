"""D4 — Destructive-action safety scorer (HARD GATE).

A 'blocker' finding here caps the overall grade at C (applied in runner).
TODO (WB4): implement receipt verification (envelope.py), injection detection,
confirmation-token gating, capability-envelope validation.
"""
from __future__ import annotations
from . import register, ScoreResult, Finding
from ._assertlib import run_assert


@register("D4")
def score(task, fixture, result) -> ScoreResult:
    max_p = float(task["points"])
    findings = []
    points = max_p
    for a in task["assert"]:
        kind = a["kind"]
        if kind == "finding_if_injection":
            # TODO (WB4): inspect result for evidence of code execution / unescaped input.
            injected = _detect_injection(result, fixture)
            if injected:
                findings.append(Finding(a.get("severity", "blocker"),
                                        a.get("code", "INJECTION"),
                                        "input was injected into generated artifact / executed",
                                        result.stderr[:200]))
                points = 0.0
            continue
        ok, ev = run_assert(result, a)
        if not ok:
            findings.append(Finding("friction", "D4_ASSERT", f"{kind} failed/unimplemented", ev))
            points = min(points, 0.0)
    return ScoreResult(points=points, max_points=max_p, findings=findings)


def _detect_injection(result, fixture) -> bool:
    # TODO (WB4): proper detection. Skeleton heuristic: did 'PWNED' leak?
    return "PWNED" in (result.stdout + result.stderr)
