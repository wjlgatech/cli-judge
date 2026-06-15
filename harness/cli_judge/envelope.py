"""Capability envelope + Ed25519 signed receipts (the only crypto in CLI-Judge).

NO blockchain. A receipt is an append-only, hash-chained JSON-lines log, each
line signed with Ed25519. Verification needs only the public key embedded in
the receipt (trust-on-first-use / append-only-log model). The optional extra
'receipts' provides `cryptography`; absent it, verification degrades to a clear
'unverifiable' result rather than crashing — and that is a NOTE, never a
safety blocker (a missing verifier is not proof of an unsafe tool).

Status: WIRED (WB7).
"""
from __future__ import annotations
import base64
import hashlib
import json
from typing import Any, Optional


def canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def args_digest(argv: list[str]) -> str:
    return hashlib.sha256(("\x00".join(argv)).encode("utf-8")).hexdigest()


def receipt_hash(receipt_wo_sig: dict[str, Any]) -> str:
    """sha256 of the canonical signed payload (all fields except 'signature')."""
    return hashlib.sha256(canonical(receipt_wo_sig)).hexdigest()


def chain_hash(receipt: dict[str, Any]) -> str:
    """sha256 of a receipt's full canonical form — what the next receipt's
    `prev_hash` must equal to chain the log."""
    return hashlib.sha256(canonical(receipt)).hexdigest()


def _ed25519_or_none():
    """Return the Ed25519PublicKey class, or None when `cryptography` is absent.
    Indirected through a function so tests can monkeypatch the crypto-absent path."""
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        return Ed25519PublicKey
    except Exception:
        return None


def verify_receipt(receipt: dict[str, Any]) -> tuple[bool, str]:
    """Verify the Ed25519 signature over the canonical non-signature fields.

    Returns (ok, evidence). When `cryptography` is unavailable, returns
    (False, "...unverifiable...") — callers treat this as a NOTE, not a failure.
    """
    pub_cls = _ed25519_or_none()
    if pub_cls is None:
        return (False, "cryptography not installed; receipt unverifiable (install extra 'receipts')")
    sig_b64 = receipt.get("signature")
    pub_b64 = receipt.get("pubkey")
    if not sig_b64 or not pub_b64:
        return (False, "receipt missing signature or pubkey")
    try:
        payload = {k: v for k, v in receipt.items() if k != "signature"}
        message = canonical(payload)
        pub = pub_cls.from_public_bytes(base64.b64decode(pub_b64))
        pub.verify(base64.b64decode(sig_b64), message)
        return (True, "Ed25519 signature valid")
    except Exception as e:  # noqa: BLE001
        return (False, f"signature verification failed: {e.__class__.__name__}")


def verify_chain(receipt: dict[str, Any], log: Optional[list[dict[str, Any]]] = None) -> tuple[bool, str]:
    """Verify hash-chain integrity.

    With a full `log` (ordered receipts): each receipt's `prev_hash` must equal
    the chain_hash of its predecessor, and every signature must verify (when
    crypto is available). With only a single `receipt`: a structural genesis
    check that `prev_hash` is present (the strong check needs the full log).
    """
    if log:
        for i in range(1, len(log)):
            expected = chain_hash(log[i - 1])
            if log[i].get("prev_hash") != expected:
                return (False, f"chain broken at index {i}: prev_hash mismatch")
        if _ed25519_or_none() is not None:
            for i, r in enumerate(log):
                ok, msg = verify_receipt(r)
                if not ok:
                    return (False, f"receipt {i} signature invalid: {msg}")
        return (True, f"chain of {len(log)} receipts intact")
    ph = receipt.get("prev_hash")
    if not isinstance(ph, str) or not ph:
        return (False, "receipt missing prev_hash")
    return (True, "prev_hash present (single-receipt structural check)")


def validate_envelope(envelope: dict[str, Any]) -> list[str]:
    """Structural consistency checks beyond JSON Schema (e.g. blast_radius
    consistency: a command that 'writes' must not be classified read-only;
    a destructive command must require confirmation). Returns error strings."""
    errs = []
    for c in envelope.get("commands", []):
        if c.get("writes") and c.get("blast_radius") == "read-only":
            errs.append(f"command {c.get('name')} declares writes but blast_radius=read-only")
        if c.get("blast_radius") == "destructive" and not c.get("requires_confirmation"):
            errs.append(f"destructive command {c.get('name')} must require confirmation")
    return errs
