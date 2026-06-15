"""Replay engine: serve recorded upstream payloads to the tool-under-test.

This is the heart of the 'reality' principle. For http_replay fixtures it
stands up a local HTTP server that (a) returns the recorded response and
(b) records what the TUT actually sent upstream, so D1 scorers can assert on
the REAL request the tool made.

Status: TODO (WB3). A minimal http.server-based implementation is sketched.
Keep it dependency-free (standard library only).
"""
from __future__ import annotations
import contextlib
import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import urlparse, parse_qs

from .adapter import UpstreamObservation


@dataclass
class ReplaySession:
    base_url: str
    observation: Optional[UpstreamObservation]
    _server: HTTPServer
    _thread: threading.Thread

    def stop(self) -> None:
        self._server.shutdown()
        self._thread.join(timeout=2)


def start_http_replay(fixture: dict) -> ReplaySession:
    """Start a local replay server for an http_replay fixture.

    TODO (WB3):
      - Match incoming request against fixture['match']; on match, return
        fixture['response'] (status/headers/body).
      - Capture method/path/query/headers/body into UpstreamObservation and
        store it on the session so the runner can attach it to Result.upstream.
      - Support multiple sequential requests if a task issues more than one.
      - Make the server bind to 127.0.0.1:0 (ephemeral port) and expose base_url.
    The skeleton below captures the first request and returns the recorded body.
    """
    captured: dict = {"obs": None}
    response = fixture.get("response", {"status": 200, "headers": {}, "body": {}})

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):  # silence
            return

        def _serve(self):
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length).decode("utf-8") if length else ""
            captured["obs"] = UpstreamObservation(
                method=self.command,
                path=parsed.path,
                query={k: v for k, v in parse_qs(parsed.query).items()},
                headers={k: v for k, v in self.headers.items()},
                body=body,
            )
            status = response.get("status", 200)
            self.send_response(status)
            for k, v in (response.get("headers") or {}).items():
                self.send_header(k, v)
            self.end_headers()
            payload = response.get("body", {})
            data = payload if isinstance(payload, str) else json.dumps(payload)
            self.wfile.write(data.encode("utf-8"))

        do_GET = _serve
        do_POST = _serve
        do_PUT = _serve
        do_PATCH = _serve
        do_DELETE = _serve

    server = HTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    sess = ReplaySession(
        base_url=f"http://{host}:{port}",
        observation=None,
        _server=server,
        _thread=thread,
    )
    # NOTE: observation is read from 'captured' after the TUT runs.
    sess._captured = captured  # type: ignore[attr-defined]
    return sess


@contextlib.contextmanager
def replay_for(fixture: dict):
    """Context manager yielding a ReplaySession for replayable fixtures, or
    None for non-replay fixtures (platform_variant / destructive_decl)."""
    if fixture.get("type") == "http_replay":
        sess = start_http_replay(fixture)
        try:
            yield sess
        finally:
            sess.observation = sess._captured.get("obs")  # type: ignore[attr-defined]
            sess.stop()
    else:
        yield None
