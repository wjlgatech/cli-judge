"""D1 — Correctness-against-reality scorer.

Replays the TUT against a recorded real upstream payload and asserts the typed
output and the REAL upstream request are correct (pagination params, no JWT
false-positive, no raw-map leak, multi-value query, serialization, base_url).
All-or-nothing per task (see scorers package docstring / plan KTD4).
"""
from __future__ import annotations
from . import register, score_all_or_nothing


@register("D1")
def score(task, fixture, result):
    return score_all_or_nothing(task, result, "D1")
