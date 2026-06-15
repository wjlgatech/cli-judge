"""Runner: orchestrate adapter + replay + scorers -> report.

Status: PARTIALLY WIRED (enough to self-test with the echo adapter). TODOs WB5.
"""
from __future__ import annotations
import importlib.util
from pathlib import Path
from typing import Any

from .adapter import Call, Adapter
from .loader import load_suite, load_task, load_fixture_for
from .replay import replay_for
from .scorers import SCORERS
from .report import build_report


def load_adapter(path: str) -> Adapter:
    spec = importlib.util.spec_from_file_location("atb_adapter", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
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
        with replay_for(fixture) as sess:
            call = Call(
                argv=task["call"]["argv"],
                env=dict(task["call"].get("env", {})),
                stdin=task["call"].get("stdin", ""),
                no_tty=task["call"].get("no_tty", True),
                replay_base_url=(sess.base_url if sess else None),
            )
            result = adapter.invoke(call)
            if sess is not None and getattr(sess, "observation", None) is not None:
                result.upstream = sess.observation

        scorer = SCORERS.get(task["dimension"])
        sr = scorer(task, fixture, result) if scorer else None
        if sr:
            for f in sr.findings:
                if task["dimension"] == "D4" and f.severity == "blocker":
                    safety_blocker = True
        results.append({"task": task, "fixture": fixture, "result": result, "score": sr})

    return build_report(suite, adapter.name, results, safety_blocker)
