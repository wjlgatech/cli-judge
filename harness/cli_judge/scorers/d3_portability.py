"""D3 — Cross-platform survival scorer.

Asserts the TUT handles path/OS/locale/encoding variants encoded in fixtures
(Windows backslash/space/unicode paths, no hard-coded OS-only binary paths,
UTF-8/CRLF tolerance) and fails LOUDLY with install guidance when an upstream
binary is absent rather than silently emitting wrong output. All-or-nothing.
"""
from __future__ import annotations
from . import register, score_all_or_nothing


@register("D3")
def score(task, fixture, result):
    return score_all_or_nothing(task, result, "D3")
