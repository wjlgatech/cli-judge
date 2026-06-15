"""Adapter for a CLI Printing Press '<api>-pp-cli' binary.

Status: TODO (WB6). Skeleton shows the intended shape.

Wiring strategy for replay:
  - pp-cli reads its base URL from config/env. Set the env var the generated
    CLI uses (commonly <API>_BASE_URL or a --base-url flag) to call.replay_base_url
    so the tool's REAL request code path hits the replay server.
  - Run the binary with subprocess, no TTY, capture stdout/stderr/exit.
"""
from __future__ import annotations
import os
import subprocess
import time
from cli_judge.adapter import Adapter, Call, Result

BINARY = os.environ.get("CLI_JUDGE_PP_BINARY", "")  # e.g. /path/to/linear-pp-cli


class PpCliAdapter:
    name = "pp-cli"

    def invoke(self, call: Call) -> Result:
        if not BINARY:
            return Result(exit_code=127, stdout="", stderr="CLI_JUDGE_PP_BINARY not set; skipping", duration_ms=0.0)
        env = dict(os.environ)
        env.update(call.env)
        if call.replay_base_url:
            # TODO (WB6): set the exact base-url env/flag the generated CLI honors.
            env["API_BASE_URL"] = call.replay_base_url
        t0 = time.time()
        proc = subprocess.run([BINARY, *call.argv], input=call.stdin,
                              capture_output=True, text=True, env=env)
        return Result(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      duration_ms=(time.time()-t0)*1000)


ADAPTER: Adapter = PpCliAdapter()
