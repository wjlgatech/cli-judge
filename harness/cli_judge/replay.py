"""Replay engine: serve recorded upstream payloads to the tool-under-test.

This is the heart of the 'reality' principle. For http_replay fixtures it
stands up a local HTTP server that (a) returns the recorded response when the
request matches fixture['match'] and (b) records what the TUT actually sent
upstream, so D1 scorers can assert on the REAL request the tool made. A
non-matching request gets a 404 — a tool that hits the wrong host/path fails
LOUDLY rather than silently receiving the recorded body (this powers the D1
per-endpoint-base-url check and the D3 backend-absent check).

For subprocess_transcript fixtures there is no network: the session exposes the
recorded argv->output transcript so an adapter/mock can serve it.

Status: WIRED (WB3). Standard library only — no third-party dependency.
"""
from __future__ import annotations
import contextlib
import json
import threading
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional
from urllib.parse import urlparse, parse_qs

from .adapter import UpstreamObservation


@dataclass
class ReplaySession:
    """Live view of a replay interaction.

    - http_replay: ``base_url`` points the TUT at the local server; after the
      run, ``observation`` is the first request the TUT made and
      ``observations`` is every request in order.
    - subprocess_transcript: ``base_url`` is None and ``transcript`` carries the
      recorded ``argv -> {stdout,stderr,exit}`` map.
    """
    base_url: Optional[str] = None
    observation: Optional[UpstreamObservation] = None
    observations: list[UpstreamObservation] = field(default_factory=list)
    transcript: Optional[dict] = None
    _server: Optional[HTTPServer] = None
    _thread: Optional[threading.Thread] = None

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=2)


def _request_matches(match: dict, method: str, path: str) -> bool:
    """True if an incoming request satisfies the fixture's match predicate.
    An empty/absent match matches everything (back-compat with seed fixtures)."""
    if not match:
        return True
    if "method" in match and str(match["method"]).upper() != method.upper():
        return False
    if "path" in match and match["path"] != path:
        return False
    return True


def start_http_replay(fixture: dict) -> ReplaySession:
    """Start a local replay server for an http_replay fixture.

    Binds to 127.0.0.1:0 (ephemeral port). Each incoming request is captured
    into an ordered list; matching requests receive fixture['response'], others
    receive a 404 so wrong-host/path requests fail loudly.
    """
    match = fixture.get("match", {})
    response = fixture.get("response", {"status": 200, "headers": {}, "body": {}})
    session = ReplaySession()  # populated live by the handler below

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def log_message(self, *a):  # silence
            return

        def _serve(self):
            parsed = urlparse(self.path)
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = self.rfile.read(length).decode("utf-8") if length else ""
            obs = UpstreamObservation(
                method=self.command,
                path=parsed.path,
                query={k: v for k, v in parse_qs(parsed.query).items()},
                headers={k: v for k, v in self.headers.items()},
                body=body,
            )
            # Populate the session LIVE so the runner can read the observation
            # immediately after the adapter call, before the context exits.
            session.observations.append(obs)
            if session.observation is None:
                session.observation = obs

            if _request_matches(match, self.command, parsed.path):
                status = response.get("status", 200)
                payload = response.get("body", {})
                headers = dict(response.get("headers") or {})
            else:
                status = 404
                payload = {"error": "no recorded response matches this request"}
                headers = {"Content-Type": "application/json"}

            data = (payload if isinstance(payload, str) else json.dumps(payload)).encode("utf-8")
            self.send_response(status)
            for k, v in headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        do_GET = _serve
        do_POST = _serve
        do_PUT = _serve
        do_PATCH = _serve
        do_DELETE = _serve

    server = HTTPServer(("127.0.0.1", 0), Handler)
    host, port = server.server_address
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    session.base_url = f"http://{host}:{port}"
    session._server = server
    session._thread = thread
    return session


@contextlib.contextmanager
def replay_for(fixture: dict):
    """Context manager yielding a ReplaySession for replayable fixtures, or
    None for fixtures that need no live replay (platform_variant /
    destructive_decl, which the scorer reads directly)."""
    ftype = fixture.get("type")
    if ftype == "http_replay":
        sess = start_http_replay(fixture)
        try:
            yield sess  # observations are populated live by the handler
        finally:
            sess.stop()
    elif ftype == "subprocess_transcript":
        yield ReplaySession(transcript=fixture.get("transcript", {}))
    else:
        yield None
