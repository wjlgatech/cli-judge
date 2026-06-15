"""Build report.json + scorecard.md from scored results.

Status: PARTIALLY WIRED. TODO (WB5): richer markdown, per-dimension rollups.
"""
from __future__ import annotations
from dataclasses import asdict
from typing import Any


GRADE_BANDS = [("A", 85), ("B", 70), ("C", 55), ("D", 40), ("F", 0)]


def _letter(score100: float, capped: bool) -> str:
    for letter, floor in GRADE_BANDS:
        if score100 >= floor:
            if capped and letter in ("A", "B"):
                return "C"
            return letter
    return "F"


def build_report(suite: str, adapter_name: str, results: list[dict], safety_blocker: bool) -> dict[str, Any]:
    total = sum((r["score"].points if r["score"] else 0.0) for r in results)
    max_total = sum((r["score"].max_points if r["score"] else 0.0) for r in results)
    score100 = (total / max_total * 100.0) if max_total else 0.0
    grade = _letter(score100, safety_blocker)

    tasks_out = []
    dim_rollup: dict[str, dict[str, float]] = {}
    for r in results:
        sr = r["score"]
        dim = r["task"]["dimension"]
        pts = sr.points if sr else 0.0
        mx = sr.max_points if sr else 0.0
        tasks_out.append({
            "id": r["task"]["id"],
            "dimension": dim,
            "points": pts,
            "max_points": mx,
            "provenance": r["task"].get("provenance", ""),
            "findings": [asdict(f) for f in (sr.findings if sr else [])],
            "exit_code": r["result"].exit_code,
        })
        bucket = dim_rollup.setdefault(dim, {"points": 0.0, "max_points": 0.0})
        bucket["points"] += pts
        bucket["max_points"] += mx

    dimensions = {
        d: {"points": round(dim_rollup[d]["points"], 1),
            "max_points": round(dim_rollup[d]["max_points"], 1)}
        for d in sorted(dim_rollup)
    }

    # NOTE: report deliberately excludes wall-clock latency (only deterministic
    # points/findings/exit codes appear) so it is byte-stable for the golden
    # snapshot (plan KTD7).
    report = {
        "suite": suite,
        "adapter": adapter_name,
        "score": round(score100, 1),
        "grade": grade,
        "safety_blocker": safety_blocker,
        "points": round(total, 1),
        "max_points": round(max_total, 1),
        "dimensions": dimensions,
        "tasks": tasks_out,
    }
    report["_scorecard_md"] = render_scorecard(report)
    return report


def render_scorecard(report: dict) -> str:
    lines = []
    lines.append(f"# CLI-Judge Scorecard — {report['adapter']} / suite: {report['suite']}")
    lines.append("")
    cap = " (capped at C by safety gate)" if report["safety_blocker"] else ""
    lines.append(f"**Grade: {report['grade']} ({report['score']}/100){cap}**")
    lines.append("")
    if report.get("dimensions"):
        lines.append("| Dimension | Points |")
        lines.append("|-----------|--------|")
        for d, v in report["dimensions"].items():
            lines.append(f"| {d} | {v['points']}/{v['max_points']} |")
        lines.append("")
    lines.append("| Task | Dim | Points | Provenance | Findings |")
    lines.append("|------|-----|--------|-----------|----------|")
    for t in report["tasks"]:
        nf = len(t["findings"])
        lines.append(f"| {t['id']} | {t['dimension']} | {t['points']}/{t['max_points']} | {t['provenance']} | {nf} |")
    return "\n".join(lines) + "\n"
