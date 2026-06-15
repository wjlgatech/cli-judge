"""D2 — Non-interactive robustness scorer.

Asserts the TUT works as an agent calls it: runs with no TTY without prompting,
emits valid JSON on the machine path with no banner contamination, returns
typed exit codes, and honors --dry-run. All-or-nothing per task.
"""
from __future__ import annotations
from . import register, score_all_or_nothing


@register("D2")
def score(task, fixture, result):
    return score_all_or_nothing(task, result, "D2")
