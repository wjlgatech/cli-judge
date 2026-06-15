"""Adapter for a CLI-Anything 'cli-anything-<software>' command.

Status: WIRED (WB6).

Notes:
  - Many cli-anything harnesses wrap a desktop backend; for D1/D2 scoring use the
    subprocess_transcript fixture type rather than http_replay.
  - Force non-interactive: stdin is fed call.stdin (default "") and closed, and
    we never allocate a TTY, so the tool cannot drop into its REPL or block on a
    prompt. A non-zero tool exit is captured, never raised.

Set CLI_JUDGE_CA_COMMAND to the command (e.g. cli-anything-blender) to score a
real tool; absent it, the adapter skips cleanly (exit 127).
"""
from __future__ import annotations
import os
import subprocess
import time
from cli_judge.adapter import Adapter, Call, Result

COMMAND = os.environ.get("CLI_JUDGE_CA_COMMAND", "")  # e.g. cli-anything-blender


class CliAnythingAdapter:
    name = "cli-anything"

    def invoke(self, call: Call) -> Result:
        if not COMMAND:
            return Result(exit_code=127, stdout="",
                          stderr="CLI_JUDGE_CA_COMMAND not set; skipping (set it to score a real cli-anything)",
                          duration_ms=0.0)
        env = dict(os.environ)
        env.update(call.env)
        if call.replay_base_url:
            env["CLI_JUDGE_REPLAY_BASE_URL"] = call.replay_base_url
        t0 = time.time()
        try:
            # input="" (default) closes stdin -> the tool runs one-shot, never
            # prompting; capture_output keeps machine output clean.
            proc = subprocess.run([COMMAND, *call.argv], input=call.stdin or "",
                                  capture_output=True, text=True, env=env)
        except OSError as e:
            return Result(exit_code=127, stdout="", stderr=f"failed to launch {COMMAND}: {e}",
                          duration_ms=(time.time() - t0) * 1000)
        return Result(exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr,
                      duration_ms=(time.time() - t0) * 1000)


ADAPTER: Adapter = CliAnythingAdapter()
