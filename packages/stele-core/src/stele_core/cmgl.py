"""CMGL-shaped procedural admit/block receipts (stdlib; no LLM).

Certified Memory Governance Layer proxy: fail-closed admissibility before a
protected write reaches SoT. Local receipts only — not CMGL product conformance.
"""

from __future__ import annotations

import hashlib
import secrets
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

ADMIT_LEDGER = "governance_admissions.ndjson"
PROTECTED_ACTIONS = frozenset(
    {
        "add",
        "promote",
        "supersede",
        "delete",
        "revoke",
        "withdraw_cascade",
        "export",
        "hydrate",
    }
)


def _ledger_path(root: Path) -> Path:
    return Path(root) / ADMIT_LEDGER


def _digest(row: Mapping[str, Any]) -> str:
    material = {k: v for k, v in row.items() if k != "receipt_digest"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def admit_gate(
    root: Path,
    *,
    action: str,
    actor: str,
    ts: str,
    authority_bundle: Mapping[str, Any] | None = None,
    entry_id: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """
    Fail-closed procedural admit for protected actions.

    Requires authority_bundle with non-empty `roles` containing `operator` or
    `oracle`, and matching `actor`. Natural-language-only auth is rejected.
    """
    action = str(action or "").strip().lower()
    actor = str(actor or "").strip()
    if not action or not actor:
        raise SchemaError("action and actor are required")
    if action not in PROTECTED_ACTIONS:
        raise SchemaError(
            f"action must be one of {sorted(PROTECTED_ACTIONS)}"
        )
    barriers: list[str] = []
    bundle = dict(authority_bundle or {})
    # Reject NL-only authorization (CMGL thesis)
    if bundle.get("natural_language_only") is True:
        barriers.append("natural_language_only_auth")
    roles = bundle.get("roles")
    if not isinstance(roles, (list, tuple)) or not roles:
        barriers.append("missing_roles")
    else:
        role_set = {str(r).strip().lower() for r in roles}
        if not role_set & {"operator", "oracle", "admin"}:
            barriers.append("insufficient_role")
    bundle_actor = str(bundle.get("actor") or "").strip()
    if bundle_actor and bundle_actor != actor:
        barriers.append("actor_mismatch")
    if not bundle_actor:
        barriers.append("missing_bundle_actor")
    expires = str(bundle.get("expires_at") or "").strip()
    if expires and expires < ts:
        barriers.append("authority_expired")

    admitted = len(barriers) == 0
    row: dict[str, Any] = {
        "receipt_id": f"ar_{secrets.token_hex(8)}",
        "action": action,
        "actor": actor,
        "ts": ts,
        "entry_id": entry_id,
        "admitted": admitted,
        "barriers": barriers,
        "roles": list(roles) if isinstance(roles, (list, tuple)) else [],
        "note": note
        or (
            "admitted — external adapter may proceed"
            if admitted
            else "blocked — do not call memory adapter (CMGL-shaped)"
        ),
    }
    row["receipt_digest"] = _digest(row)
    path = _ledger_path(root)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_dumps(row) + "\n")
    return {
        "ok": admitted,
        "admitted": admitted,
        "barriers": barriers,
        "receipt": row,
        "note": "CMGL-shaped fail-closed admit — local receipt, not product CMGL",
    }


def list_admit_receipts(
    root: Path, *, limit: int = 50
) -> dict[str, Any]:
    path = _ledger_path(root)
    rows: list[dict[str, Any]] = []
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            rows.append(canonical_loads(line))
    rows = list(reversed(rows))[: max(1, int(limit))]
    return {
        "receipts": rows,
        "count": len(rows),
        "note": "newest first — CMGL-shaped governance admissions",
    }


def verify_admit_receipt(receipt: Mapping[str, Any]) -> dict[str, Any]:
    expected = _digest(receipt)
    got = str(receipt.get("receipt_digest") or "")
    ok = bool(got) and got == expected
    return {
        "ok": ok,
        "expected": expected,
        "got": got,
        "note": "local digest verify — not transferable attestation",
    }
