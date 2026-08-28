"""GPM-shaped decision receipts — fail-closed release audit (stdlib only)."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

DECISION_KINDS = frozenset({"release", "abstain", "import_verify"})
POLICY_VERSION_DEFAULT = "stele-release-1"


def _decisions_dir(root: Path) -> Path:
    return Path(root) / "decisions"


def _receipt_digest(body: dict[str, Any]) -> str:
    material = {k: v for k, v in body.items() if k != "receipt_digest"}
    return hashlib.sha256(canonical_dumps(material).encode("utf-8")).hexdigest()


def issue_decision_receipt(
    root: Path,
    *,
    kind: str,
    head: str | None,
    barriers: list[str],
    released: bool,
    actor: str,
    ts: str,
    claim_ids: list[str] | None = None,
    policy_version: str = POLICY_VERSION_DEFAULT,
    query_hash: str | None = None,
    seal_root: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    """
    Persist a local decision record bound to a verified journal head.

    GPM-shaped: release receipts only when released=True; abstain is explicit
    kind for operators who want an audit trail of blocked releases.
    """
    if kind not in DECISION_KINDS:
        raise SchemaError(f"kind must be one of {sorted(DECISION_KINDS)}")
    if not actor or not str(actor).strip():
        raise SchemaError("actor is required")
    if kind == "release" and not released:
        raise SchemaError("release receipts require released=True")
    if kind == "abstain" and released:
        raise SchemaError("abstain receipts require released=False")

    ddir = _decisions_dir(root)
    ddir.mkdir(parents=True, exist_ok=True)
    rid = f"dr_{uuid.uuid4().hex[:16]}"
    body: dict[str, Any] = {
        "id": rid,
        "kind": kind,
        "released": bool(released),
        "head": head,
        "barriers": list(barriers),
        "claim_ids": list(claim_ids or []),
        "policy_version": policy_version,
        "query_hash": query_hash,
        "seal_root": seal_root,
        "actor": str(actor).strip(),
        "ts": ts,
        "note": note
        or "local decision receipt — not transferable attestation / not CAVA PCAA",
    }
    body["receipt_digest"] = _receipt_digest(body)
    path = ddir / f"{rid}.json"
    path.write_text(canonical_dumps(body), encoding="utf-8")
    return body


def list_decision_receipts(root: Path, *, limit: int = 50) -> list[dict[str, Any]]:
    """Newest-first decision receipts (audit projection; not memory SoT)."""
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    ddir = _decisions_dir(root)
    if not ddir.is_dir():
        return []
    rows: list[dict[str, Any]] = []
    for path in ddir.glob("dr_*.json"):
        try:
            rows.append(canonical_loads(path.read_text(encoding="utf-8")))
        except Exception:  # noqa: BLE001
            continue
    rows.sort(key=lambda r: str(r.get("ts") or ""), reverse=True)
    return rows[:limit]


def verify_decision_receipt(
    root: Path,
    receipt: dict[str, Any],
    *,
    require_current_head: bool = False,
    live_head: str | None = None,
) -> dict[str, Any]:
    """
    Recompute receipt digest; optionally require head still matches live chain head.
    """
    expected = str(receipt.get("receipt_digest") or "")
    live_digest = _receipt_digest(dict(receipt))
    dig_ok = bool(expected) and expected == live_digest
    head_ok = True
    if require_current_head:
        if live_head is None:
            raise SchemaError("require_current_head needs live_head")
        head_ok = str(receipt.get("head") or "") == str(live_head)
    path = _decisions_dir(root) / f"{receipt.get('id')}.json"
    on_disk = path.is_file()
    return {
        "ok": dig_ok and head_ok and on_disk,
        "digest_ok": dig_ok,
        "head_current": head_ok if require_current_head else None,
        "on_disk": on_disk,
        "id": receipt.get("id"),
        "note": "receipt integrity — not proof the claim answered the query",
    }
