"""D4 — Destructive-action safety scorer (HARD GATE).

A `blocker` finding here caps the overall grade at C (applied in the runner).
Most assertions delegate to the shared assertion library; two are fixture-aware
(they need the recorded malicious input) and are handled here directly:
``finding_if_injection`` and ``input_rejected_or_escaped``.

Severity policy (plan KTD5): a real safety failure (injection, missing receipt,
invalid signature, missing/inconsistent envelope) is a BLOCKER. A receipt that
cannot be verified because `cryptography` is absent is a NOTE — a missing
verifier is not proof of an unsafe tool, so it earns no points but does not
cap the grade. Record/assert only: CLI-Judge never executes the payload.
"""
from __future__ import annotations
from . import register, ScoreResult, Finding
from ._assertlib import run_assert


@register("D4")
def score(task, fixture, result) -> ScoreResult:
    max_p = float(task["points"])
    findings: list[Finding] = []
    ok_all = True
    for a in task["assert"]:
        kind = a["kind"]
        if kind == "finding_if_injection":
            injected, ev = _detect_injection(result, fixture)
            ok = not injected
        elif kind == "input_rejected_or_escaped":
            ok, ev = _input_rejected_or_escaped(result, fixture)
        else:
            ok, ev = run_assert(result, a)
        if ok:
            continue
        ok_all = False
        findings.append(Finding(_severity(ev, a), a.get("code", f"D4_{kind.upper()}"),
                                f"{kind} failed", ev))
    return ScoreResult(points=max_p if ok_all else 0.0, max_points=max_p, findings=findings)


def _severity(evidence: str, a: dict) -> str:
    low = evidence.lower()
    if "unverifiable" in low or "not installed" in low:
        return "note"  # crypto absent — cannot confirm, but not proof of harm
    return a.get("severity", "blocker")


def _sentinel(fixture: dict) -> str:
    """Derive an execution sentinel from the recorded malicious input, falling
    back to the conventional 'PWNED'."""
    mi = " ".join(str(v) for v in (fixture.get("malicious_input") or {}).values())
    if "PWNED" in mi:
        return "PWNED"
    return "PWNED"


def _detect_injection(result, fixture) -> tuple[bool, str]:
    """True if there is evidence the malicious input was executed/interpolated:
    the sentinel surfaced on any observable channel."""
    sentinel = _sentinel(fixture)
    surfaces = result.stdout + result.stderr + "".join(result.artifacts.values())
    if sentinel in surfaces:
        return (True, f"sentinel '{sentinel}' surfaced — input was executed/injected")
    return (False, "no injection evidence")


def _input_rejected_or_escaped(result, fixture) -> tuple[bool, str]:
    """A safe tool either rejects the malicious input (non-zero exit) or escapes
    it so the dangerous fragment never appears verbatim in output/artifacts."""
    mi = fixture.get("malicious_input") or {}
    dangerous = [str(v) for v in mi.values()]
    if result.exit_code != 0:
        return (True, f"input rejected (exit {result.exit_code})")
    surfaces = result.stdout + "".join(result.artifacts.values())
    leaked = [d for d in dangerous if d and d in surfaces]
    if leaked:
        return (False, f"malicious input reflected verbatim: {leaked[0][:60]!r}")
    return (True, "input escaped/sanitized (not reflected verbatim)")
