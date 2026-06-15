"""Tests for the real adapters (WB6).

Use throwaway /bin/sh stubs as stand-in tools so no real binary is required.
The adapters read their binary path from a module global, which we set directly.
"""
import importlib.util

from cli_judge.adapter import Call
from cli_judge.loader import ROOT

PP = ROOT / "harness" / "adapters" / "pp_cli_adapter.py"
CA = ROOT / "harness" / "adapters" / "cli_anything_adapter.py"


def _load(modname, path):
    spec = importlib.util.spec_from_file_location(modname, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _stub(tmp_path, name, body):
    p = tmp_path / name
    p.write_text("#!/bin/sh\n" + body)
    p.chmod(0o755)
    return str(p)


def test_pp_skips_cleanly_when_binary_unset():
    mod = _load("pp_skip", PP)
    mod.BINARY = ""
    r = mod.ADAPTER.invoke(Call(argv=["issues", "list"]))
    assert r.exit_code == 127
    assert "not set" in r.stderr


def test_pp_runs_stub_and_wires_replay_base_url(tmp_path):
    stub = _stub(tmp_path, "fake-pp", 'echo "args:$@"\necho "base:$API_BASE_URL"\nexit 0\n')
    mod = _load("pp_run", PP)
    mod.BINARY = stub
    r = mod.ADAPTER.invoke(Call(argv=["issues", "list"], replay_base_url="http://127.0.0.1:9999"))
    assert r.exit_code == 0
    assert "args:issues list" in r.stdout
    assert "base:http://127.0.0.1:9999" in r.stdout  # base-url reached the tool's env


def test_pp_captures_nonzero_exit_without_raising(tmp_path):
    stub = _stub(tmp_path, "fail-pp", "echo boom >&2\nexit 4\n")
    mod = _load("pp_fail", PP)
    mod.BINARY = stub
    r = mod.ADAPTER.invoke(Call(argv=["x"]))
    assert r.exit_code == 4
    assert "boom" in r.stderr


def test_ca_skips_and_runs_non_interactively(tmp_path):
    mod = _load("ca_skip", CA)
    mod.COMMAND = ""
    assert mod.ADAPTER.invoke(Call(argv=["render"])).exit_code == 127

    # `cat` would block forever if stdin were left open; input="" closes it, so
    # completing proves the adapter runs the tool one-shot (non-interactive).
    stub = _stub(tmp_path, "fake-ca", "cat\necho done\nexit 0\n")
    mod2 = _load("ca_run", CA)
    mod2.COMMAND = stub
    r = mod2.ADAPTER.invoke(Call(argv=["render", "--out", "x"]))
    assert r.exit_code == 0
    assert "done" in r.stdout
