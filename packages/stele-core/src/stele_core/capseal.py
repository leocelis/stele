"""CapSeal-shaped non-exportable action capabilities (stdlib; no LLM).

Shaped by CapSeal (arXiv:2604.16762): grant narrowly scoped action handles
instead of handing the model a bearer secret. Handles never embed secret
material; export probes must fail closed.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.credguard import credential_scan
from stele_core.schema import SchemaError, canonical_dumps

_METHODS = frozenset({"http_get", "http_post", "ssh_exec", "tool_call"})


def issue_action_capability(
    *,
    intent: str,
    method: str,
    host: str,
    session_id: str,
    max_calls: int = 1,
    expires_at: str,
) -> dict[str, Any]:
    """
    Issue a non-exportable action capability handle (digest attestation).

    Never includes raw secrets — only intent constraints.
    """
    intent = str(intent or "").strip()
    method = str(method or "").strip().lower()
    host = str(host or "").strip().lower()
    session_id = str(session_id or "").strip()
    expires_at = str(expires_at or "").strip()
    if not intent or not host or not session_id or not expires_at:
        raise SchemaError("intent, host, session_id, and expires_at are required")
    if method not in _METHODS:
        raise SchemaError(f"method must be one of {sorted(_METHODS)}")
    if max_calls < 1:
        raise SchemaError("max_calls must be >= 1")
    # Fail closed if intent itself looks like a secret dump
    scan = credential_scan(intent)
    if scan["count"] > 0:
        raise SchemaError("intent must not contain credential patterns")
    payload = {
        "intent": intent,
        "method": method,
        "host": host,
        "session_id": session_id,
        "max_calls": int(max_calls),
        "expires_at": expires_at,
        "exportable": False,
    }
    handle = hashlib.sha256(canonical_dumps(payload).encode("utf-8")).hexdigest()
    return {
        "handle": handle,
        "payload": payload,
        "ok": True,
        "note": "capseal issue_action_capability — non-exportable handle proxy",
    }


def capability_export_probe(
    handle: str,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Probe whether a capability can be exported / revealed as a bearer secret.

    CapSeal invariant: exportable must be false; payload must not contain secrets.
    """
    handle = str(handle or "").strip().lower()
    expected = hashlib.sha256(
        canonical_dumps(dict(payload)).encode("utf-8")
    ).hexdigest()
    if handle != expected:
        return {
            "export_allowed": False,
            "reason": "handle_mismatch",
            "ok": True,
            "note": "capseal capability_export_probe",
        }
    if payload.get("exportable") is not False:
        return {
            "export_allowed": False,
            "reason": "exportable_flag_not_false",
            "ok": True,
            "note": "capseal capability_export_probe",
        }
    blob = canonical_dumps(dict(payload))
    scan = credential_scan(blob)
    if scan["count"] > 0:
        return {
            "export_allowed": False,
            "reason": "secret_in_payload",
            "hits": scan["hits"],
            "ok": True,
            "note": "capseal capability_export_probe",
        }
    return {
        "export_allowed": False,
        "reason": "non_exportable_by_design",
        "ok": True,
        "note": "capseal capability_export_probe — always deny export",
    }


def check_action_capability(
    handle: str,
    payload: Mapping[str, Any],
    *,
    method: str,
    host: str,
    session_id: str,
    call_count: int = 0,
    now: str | None = None,
) -> dict[str, Any]:
    """Authorize one mediated invocation against a capability handle."""
    handle = str(handle or "").strip().lower()
    method = str(method or "").strip().lower()
    host = str(host or "").strip().lower()
    session_id = str(session_id or "").strip()
    expected = hashlib.sha256(
        canonical_dumps(dict(payload)).encode("utf-8")
    ).hexdigest()
    if handle != expected:
        return {
            "allowed": False,
            "reason": "handle_mismatch",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    if str(payload.get("session_id") or "") != session_id:
        return {
            "allowed": False,
            "reason": "session_mismatch",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    if str(payload.get("method") or "") != method:
        return {
            "allowed": False,
            "reason": "method_mismatch",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    if str(payload.get("host") or "").lower() != host:
        return {
            "allowed": False,
            "reason": "host_mismatch",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    max_calls = int(payload.get("max_calls") or 0)
    if call_count >= max_calls:
        return {
            "allowed": False,
            "reason": "quota_exhausted",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    exp = str(payload.get("expires_at") or "")
    if now and exp and now > exp:
        return {
            "allowed": False,
            "reason": "expired",
            "ok": True,
            "note": "capseal check_action_capability",
        }
    return {
        "allowed": True,
        "reason": "ok",
        "remaining_calls": max_calls - call_count - 1,
        "ok": True,
        "note": "capseal check_action_capability",
    }


def action_capability_inventory(
    capabilities: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Summarize issued capability payloads (no secrets expected)."""
    rows: list[dict[str, Any]] = []
    for c in capabilities:
        if not isinstance(c, Mapping):
            continue
        payload = c.get("payload") if isinstance(c.get("payload"), Mapping) else c
        rows.append(
            {
                "handle": c.get("handle"),
                "method": payload.get("method"),
                "host": payload.get("host"),
                "session_id": payload.get("session_id"),
                "max_calls": payload.get("max_calls"),
                "exportable": payload.get("exportable"),
            }
        )
    return {
        "capabilities": rows,
        "count": len(rows),
        "ok": True,
        "note": "capseal action_capability_inventory",
    }
