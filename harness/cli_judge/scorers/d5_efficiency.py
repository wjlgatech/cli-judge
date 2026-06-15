"""D5 — Token & latency efficiency scorer.

Asserts output payload (proxy-tokenized) stays within the archetype budget,
that --compact reduces tokens by the claimed margin without dropping required
fields, and that p50 local-path latency is within budget. All-or-nothing.

Note: latency assertions are wall-clock and non-deterministic; the runner
isolates measured latency from the golden snapshot (plan KTD7).
"""
from __future__ import annotations
from . import register, score_all_or_nothing


@register("D5")
def score(task, fixture, result):
    return score_all_or_nothing(task, result, "D5")
