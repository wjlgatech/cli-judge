"""Runner: orchestrate adapter + replay + scorers -> report.

Status: WIRED (WB5). Drives each task through the replay engine, attaches the
adapter's capability envelope and any compare_call output, scores, and applies
the D4 safety blocker signal.
"""
from __future__ import annotations
import importlib.util
from typing import Any

from .adapter import Call, Adapter
from .loader import load_suite, load_task, load_fixture_for
from .replay import replay_for
from .scorers import SCORERS
from .report import build_report


def load_adapter(path: str) -> Adapter:
    spec = importlib.util.spec_from_file_location("cli_judge_adapter", path)
    assert spec is not None and spec.loader is not None, f"cannot load adapter from {path}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "ADAPTER"):
        raise SystemExit(f"{path} must define a module-level ADAPTER instance")
    return mod.ADAPTER


def run_suite(adapter_path: str, suite: str) -> dict[str, Any]:
    adapter = load_adapter(adapter_path)
    task_paths = load_suite(suite)
    results = []
    safety_blocker = False

    for tp in task_paths:
        task = load_task(tp)
        fixture = load_fixture_for(task)
        result = _invoke(adapter, task, fixture, "call")

        # Attach the tool's declared capability envelope (D4) if it offers one.
        if result.envelope is None and hasattr(adapter, "capability_envelope"):
            try:
                result.envelope = adapter.capability_envelope()
            except Exception:  # noqa: BLE001 — a broken envelope is the tool's fault, not ours
                result.envelope = None

        # For token-reduction tasks (D5), run the --compact variant and stash
        # its output so the token_reduction_at_least assert can compare.
        if "compare_call" in task:
            cmp_result = _invoke(adapter, task, fixture, "compare_call")
            result.artifacts["compare_stdout"] = cmp_result.stdout

        scorer = SCORERS.get(task["dimension"])
        sr = scorer(task, fixture, result) if scorer else None
        if sr:
            for f in sr.findings:
                if task["dimension"] == "D4" and f.severity == "blocker":
                    safety_blocker = True
        results.append({"task": task, "fixture": fixture, "result": result, "score": sr})

    return build_report(suite, adapter.name, results, safety_blocker)


def _invoke(adapter: Adapter, task: dict[str, Any], fixture: dict, call_key: str):
    """Drive the adapter for one call (call or compare_call), routing upstream
    traffic through the replay engine and attaching the observed request."""
    spec = task[call_key]
    with replay_for(fixture) as sess:
        call = Call(
            argv=spec["argv"],
            env=dict(spec.get("env", {})),
            stdin=spec.get("stdin", ""),
            no_tty=spec.get("no_tty", True),
            replay_base_url=(sess.base_url if sess else None),
        )
        result = adapter.invoke(call)
        if sess is not None and getattr(sess, "observation", None) is not None:
            result.upstream = sess.observation
    return result
