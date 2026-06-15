"""Adapter for a CLI-Anything 'cli-anything-<software>' command.

Status: TODO (WB6).

Notes:
  - Many cli-anything harnesses wrap a desktop backend; for D1/D2 scoring use the
    subprocess_transcript fixture type rather than http_replay.
  - Force non-interactive: pass the subcommand (not bare command) so it doesn't
    drop into the REPL; ensure stdin is closed.
"""
from __future__ import annotations
import os
import subprocess
import time
from atb.adapter import Adapter, Call, Result

COMMAND = os.environ.get("ATB_CA_COMMAND", "")  # e.g. cli-anything-blender


class CliAnythingAdapter:
    name = "cli-anything"

    def invoke(self, call: Call) -> Result:
        if not COMMAND:
            return Result(exit_code=127, stdout="", stderr="ATB_CA_COMMAND not set; skipping", duration_ms=0.0)
        env = dict(os.environ); env.update(call.env)
        t0 = time.time()
        proc = subprocess.run([COMMAND, *call.argv], input=call.stdin,
                              capture_output=True, text=True, env=env)
        return Result(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      duration_ms=(time.time()-t0)*1000)


ADAPTER: Adapter = CliAnythingAdapter()
