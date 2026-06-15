"""Adapter for a CLI Printing Press '<api>-pp-cli' binary.

Status: WIRED (WB6).

Wiring strategy for replay:
  - A pp-cli reads its base URL from config/env. We export several common
    base-url env names pointed at call.replay_base_url so the tool's REAL
    request code path hits the replay server. Override the exact name for a
    given CLI with CLI_JUDGE_PP_BASE_URL_ENV.
  - Run the binary with subprocess, no TTY (stdin is fed call.stdin and closed),
    capturing stdout/stderr/exit. A non-zero tool exit is captured in
    Result.exit_code — never raised.

Set CLI_JUDGE_PP_BINARY to the binary path to score a real tool; absent it, the
adapter skips cleanly (exit 127) so the suite still runs.
"""
from __future__ import annotations
import os
import subprocess
import time
from cli_judge.adapter import Adapter, Call, Result

BINARY = os.environ.get("CLI_JUDGE_PP_BINARY", "")  # e.g. /path/to/linear-pp-cli
# Comma-separated extra env var names that should receive the replay base URL.
_EXTRA_BASE_URL_ENV = os.environ.get("CLI_JUDGE_PP_BASE_URL_ENV", "")
_DEFAULT_BASE_URL_ENVS = ["API_BASE_URL", "BASE_URL", "PP_BASE_URL"]


class PpCliAdapter:
    name = "pp-cli"

    def invoke(self, call: Call) -> Result:
        if not BINARY:
            return Result(exit_code=127, stdout="",
                          stderr="CLI_JUDGE_PP_BINARY not set; skipping (set it to score a real pp-cli)",
                          duration_ms=0.0)
        env = dict(os.environ)
        env.update(call.env)
        if call.replay_base_url:
            names = list(_DEFAULT_BASE_URL_ENVS)
            if _EXTRA_BASE_URL_ENV:
                names += [n.strip() for n in _EXTRA_BASE_URL_ENV.split(",") if n.strip()]
            for name in names:
                env[name] = call.replay_base_url
        t0 = time.time()
        try:
            proc = subprocess.run([BINARY, *call.argv], input=call.stdin,
                                  capture_output=True, text=True, env=env)
        except OSError as e:
            return Result(exit_code=127, stdout="", stderr=f"failed to launch {BINARY}: {e}",
                          duration_ms=(time.time() - t0) * 1000)
        return Result(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      duration_ms=(time.time() - t0) * 1000)


ADAPTER: Adapter = PpCliAdapter()
