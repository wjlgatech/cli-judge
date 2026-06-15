"""Capability envelope + Ed25519 signed receipts (the only crypto in CLI-Judge).

NO blockchain. A receipt is an append-only, hash-chained JSON-lines log,
each line signed with Ed25519. Verification needs only a public key.

Status: TODO (WB7). Requires optional extra 'cryptography'. If unavailable,
verify_receipt() must return a clear 'unverifiable: cryptography not installed'
finding rather than crashing.
"""
from __future__ import annotations
import hashlib
import json
from typing import Any, Optional


def canonical(obj: dict[str, Any]) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def args_digest(argv: list[str]) -> str:
    return hashlib.sha256(("\x00".join(argv)).encode("utf-8")).hexdigest()


def receipt_hash(receipt_wo_sig: dict[str, Any]) -> str:
    return hashlib.sha256(canonical(receipt_wo_sig)).hexdigest()


def verify_receipt(receipt: dict[str, Any]) -> tuple[bool, str]:
    """Verify the Ed25519 signature over the canonical non-signature fields.

    TODO (WB7):
      - from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
      - rebuild the signed payload (all fields except 'signature')
      - load pubkey from base64, verify base64 signature
      - also check prev_hash chains correctly when scoring a full log
    """
    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey  # noqa: F401
    except Exception:
        return (False, "cryptography not installed; receipt unverifiable (install extra 'receipts')")
    # TODO: real verification.
    return (False, "verify_receipt not yet implemented (WB7)")


def validate_envelope(envelope: dict[str, Any]) -> list[str]:
    """Lightweight structural checks beyond JSON Schema (e.g. blast_radius
    consistency: a command that 'writes' must not be classified read-only)."""
    errs = []
    for c in envelope.get("commands", []):
        if c.get("writes") and c.get("blast_radius") == "read-only":
            errs.append(f"command {c.get('name')} declares writes but blast_radius=read-only")
        if c.get("blast_radius") == "destructive" and not c.get("requires_confirmation"):
            errs.append(f"destructive command {c.get('name')} must require confirmation")
    return errs
