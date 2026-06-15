"""Adapter ABI: how CLI-Judge talks to any tool-under-test (TUT).

An adapter is the ONLY tool-specific code in CLI-Judge. It normalizes a tool
(a Go pp-cli binary, a Python cli-anything harness, an MCP server, a mock)
into CLI-Judge's call/result protocol.

Status: WIRED. Real adapters live under adapters/ (WB6).
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol, Optional


@dataclass
class Call:
    """One invocation request for a tool-under-test."""
    argv: list[str]
    env: dict[str, str] = field(default_factory=dict)
    stdin: str = ""
    no_tty: bool = True
    # When set by the runner, the adapter MUST route upstream traffic to this
    # replay endpoint (e.g. set HTTP(S)_PROXY or a tool-specific base-url env)
    # so the TUT executes its real code path against a recorded payload.
    replay_base_url: Optional[str] = None


@dataclass
class UpstreamObservation:
    """What the replay engine observed the TUT send upstream (for D1 asserts)."""
    method: str = ""
    path: str = ""
    query: dict[str, list[str]] = field(default_factory=dict)
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""


@dataclass
class Result:
    """The outcome of a Call."""
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    prompted: bool = False          # did it block on a prompt? (D2)
    upstream: Optional[UpstreamObservation] = None  # filled by replay engine
    receipt: Optional[dict] = None  # parsed signed receipt, if emitted (D4)
    envelope: Optional[dict] = None  # tool's declared capability envelope (D4); filled by runner
    artifacts: dict[str, str] = field(default_factory=dict)  # any generated files


class Adapter(Protocol):
    """Implement this for each tool family."""
    name: str

    def invoke(self, call: Call) -> Result:
        """Run the tool for one Call and return a Result. Must never raise on
        a non-zero tool exit; capture it in Result.exit_code instead."""
        ...

    def capability_envelope(self) -> Optional[dict]:
        """Return the tool's declared capability envelope, or None if absent.
        Used by the D4 safety scorer."""
        return None
