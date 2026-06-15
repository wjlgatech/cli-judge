"""Tests for capability envelope + Ed25519 receipts (WB7).

Signing tests require the optional 'receipts' extra (cryptography); they skip
cleanly where it is absent (e.g. CI installing only [dev]). The crypto-absent
graceful path is tested unconditionally.
"""
import base64

import pytest

from cli_judge import envelope as E


def _make_signed_receipt(prev_hash="0" * 64, command="issues update", actor="agent:test"):
    """Mint a valid Ed25519-signed receipt for tests (needs cryptography)."""
    crypto = pytest.importorskip("cryptography")
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    from cryptography.hazmat.primitives import serialization
    pub_raw = pub.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)

    payload = {
        "tool": "linear-cli-judge",
        "command": command,
        "args_digest": E.args_digest([command]),
        "blast_radius": "reversible",
        "timestamp": "2026-01-01T00:00:00Z",
        "actor": actor,
        "prev_hash": prev_hash,
        "pubkey": base64.b64encode(pub_raw).decode(),
    }
    sig = priv.sign(E.canonical(payload))
    payload["signature"] = base64.b64encode(sig).decode()
    return payload


def test_valid_receipt_verifies():
    r = _make_signed_receipt()
    ok, ev = E.verify_receipt(r)
    assert ok, ev


def test_tampered_field_fails_verification():
    r = _make_signed_receipt()
    r["blast_radius"] = "destructive"  # tamper after signing
    ok, ev = E.verify_receipt(r)
    assert not ok


def test_chain_intact_and_broken():
    r0 = _make_signed_receipt(prev_hash="0" * 64)
    r1 = _make_signed_receipt(prev_hash=E.chain_hash(r0))
    ok, ev = E.verify_chain(r1, log=[r0, r1])
    assert ok, ev
    # Break the link.
    r1_bad = dict(r1, prev_hash="deadbeef")
    ok2, ev2 = E.verify_chain(r1_bad, log=[r0, r1_bad])
    assert not ok2


def test_crypto_absent_is_graceful_not_a_crash(monkeypatch):
    monkeypatch.setattr(E, "_ed25519_or_none", lambda: None)
    ok, ev = E.verify_receipt({"signature": "x", "pubkey": "y", "prev_hash": "0" * 64})
    assert ok is False
    assert "unverifiable" in ev


def test_validate_envelope_flags_inconsistencies():
    env = {
        "tool": "t", "version": "1",
        "commands": [
            {"name": "rm", "blast_radius": "destructive"},               # missing requires_confirmation
            {"name": "ls", "blast_radius": "read-only", "writes": ["x"]},  # writes but read-only
            {"name": "ok", "blast_radius": "destructive", "requires_confirmation": True},
        ],
    }
    errs = E.validate_envelope(env)
    assert any("rm" in e for e in errs)
    assert any("ls" in e for e in errs)
    assert not any("ok" in e for e in errs)
