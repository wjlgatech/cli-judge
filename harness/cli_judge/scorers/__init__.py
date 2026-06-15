"""Five dimension scorers. Each: score(task, fixture, result) -> ScoreResult.

Status: SKELETON. Implement the TODOs (WB4). Each scorer must follow the exact
point tables in ../../RUBRIC.md and emit structured findings.
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


# Import side-effect registration.
from . import d1_correctness, d2_noninteractive, d3_portability, d4_safety, d5_efficiency  # noqa: E402,F401
