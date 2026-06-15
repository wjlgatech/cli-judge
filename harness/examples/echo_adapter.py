"""Echo adapter: a trivial, deterministic TUT so the harness can self-test
end-to-end with NO real tool installed.

It fabricates plausible 'correct' behavior for the seed D1/D2 tasks by reading
the replay base_url, making the recorded request, and echoing a shaped result.
This proves the pipeline wires up; it is NOT a real tool under test.

Status: WIRED enough for 'atb selftest'.
"""
from __future__ import annotations
import json
import time
import urllib.request
from atb.adapter import Adapter, Call, Result


class EchoAdapter:
    name = "echo"

    def invoke(self, call: Call) -> Result:
        t0 = time.time()
        stdout = "{}"
        # If a replay endpoint is present, actually call it so the replay engine
        # records a real upstream observation (demonstrates D1 plumbing).
        if call.replay_base_url:
            try:
                # Build a naive query that a 'correct' tool would send.
                url = call.replay_base_url + "/v1/issues?skip=50&limit=50"
                with urllib.request.urlopen(url, timeout=3) as resp:
                    body = resp.read().decode("utf-8")
                stdout = body
            except Exception as e:  # noqa: BLE001
                return Result(exit_code=5, stdout="", stderr=str(e),
                              duration_ms=(time.time()-t0)*1000)
        dur = (time.time() - t0) * 1000
        return Result(exit_code=0, stdout=stdout, stderr="", duration_ms=dur, prompted=False)

    def capability_envelope(self):
        return {"tool": "echo", "version": "0.0.0",
                "commands": [{"name": "issues list", "blast_radius": "read-only"}]}


ADAPTER: Adapter = EchoAdapter()
