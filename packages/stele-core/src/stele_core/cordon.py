"""Cordon-shaped effect outbox for irreversible tool side effects (stdlib)."""

from __future__ import annotations

import secrets
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps, canonical_loads

EFFECTS_NAME = "effects.ndjson"
EFFECT_STATES = frozenset(
    {"pending", "ready", "dispatched", "cancelled", "compensated"}
)


def _path(root: Path) -> Path:
    return Path(root) / EFFECTS_NAME


def _eid() -> str:
    return f"fx_{secrets.token_hex(8)}"


def stage_effect(
    root: Path,
    *,
    txid: str | None,
    sink: str,
    payload: Mapping[str, Any],
    actor: str,
    ts: str,
    belief_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Stage an irreversible external effect in the outbox (Cordon-shaped).

    Not dispatched until release_effects marks ready after belief commit.
    """
    sink = str(sink or "").strip()
    actor = str(actor or "").strip()
    if not sink or not actor:
        raise SchemaError("sink and actor are required")
    row = {
        "effect_id": _eid(),
        "txid": txid,
        "sink": sink,
        "payload": dict(payload),
        "belief_ids": list(belief_ids or []),
        "state": "pending",
        "actor": actor,
        "ts": ts,
        "note": "Cordon-shaped outbox — local promote ≠ effect release",
    }
    path = _path(root)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(canonical_dumps(row) + "\n")
    return dict(row)


def _iter_effects(root: Path) -> list[dict[str, Any]]:
    path = _path(root)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(canonical_loads(line))
    return rows


def _rewrite_all(root: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    path = _path(root)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(canonical_dumps(dict(row)) + "\n")


def release_effects(
    root: Path,
    *,
    txid: str | None = None,
    effect_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Mark pending effects ready for dispatch after belief commit."""
    rows = _iter_effects(root)
    want_ids = {str(i) for i in (effect_ids or [])} if effect_ids is not None else None
    ready: list[str] = []
    for row in rows:
        if row.get("state") != "pending":
            continue
        if txid is not None and row.get("txid") != txid:
            continue
        if want_ids is not None and str(row.get("effect_id")) not in want_ids:
            continue
        row["state"] = "ready"
        ready.append(str(row.get("effect_id")))
    _rewrite_all(root, rows)
    return {
        "ok": True,
        "ready": ready,
        "count": len(ready),
        "note": "effects ready — caller dispatches; Stele does not call external sinks",
    }


def mark_dispatched(
    root: Path, effect_id: str, *, receipt: str | None = None
) -> dict[str, Any]:
    rows = _iter_effects(root)
    found = False
    for row in rows:
        if row.get("effect_id") != effect_id:
            continue
        if row.get("state") not in {"ready", "pending"}:
            raise SchemaError(f"cannot dispatch effect in state {row.get('state')}")
        row["state"] = "dispatched"
        if receipt:
            row["receipt"] = receipt
        found = True
        break
    if not found:
        raise SchemaError(f"unknown effect: {effect_id}")
    _rewrite_all(root, rows)
    return {"ok": True, "effect_id": effect_id, "state": "dispatched"}


def cancel_effect(root: Path, effect_id: str, *, reason: str = "cancel") -> dict[str, Any]:
    rows = _iter_effects(root)
    found = False
    for row in rows:
        if row.get("effect_id") != effect_id:
            continue
        if row.get("state") == "dispatched":
            raise SchemaError("dispatched effects need compensate, not cancel")
        row["state"] = "cancelled"
        row["cancel_reason"] = reason
        found = True
        break
    if not found:
        raise SchemaError(f"unknown effect: {effect_id}")
    _rewrite_all(root, rows)
    return {"ok": True, "effect_id": effect_id, "state": "cancelled"}


def compensate_effect(
    root: Path, effect_id: str, *, reason: str = "compensate"
) -> dict[str, Any]:
    """Mark dispatched effect as needing compensation (audit — caller executes)."""
    rows = _iter_effects(root)
    found = False
    for row in rows:
        if row.get("effect_id") != effect_id:
            continue
        if row.get("state") != "dispatched":
            raise SchemaError("compensate only applies to dispatched effects")
        row["state"] = "compensated"
        row["compensate_reason"] = reason
        found = True
        break
    if not found:
        raise SchemaError(f"unknown effect: {effect_id}")
    _rewrite_all(root, rows)
    return {
        "ok": True,
        "effect_id": effect_id,
        "state": "compensated",
        "note": "audit marker — caller performs external compensation",
    }


def list_effects(
    root: Path,
    *,
    state: str | None = None,
    txid: str | None = None,
    limit: int = 50,
) -> dict[str, Any]:
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    if state and state not in EFFECT_STATES:
        raise SchemaError(f"state must be one of {sorted(EFFECT_STATES)}")
    rows = _iter_effects(root)
    out: list[dict[str, Any]] = []
    for row in reversed(rows):
        if state and row.get("state") != state:
            continue
        if txid is not None and row.get("txid") != txid:
            continue
        out.append(row)
        if len(out) >= limit:
            break
    return {
        "effects": out,
        "count": len(out),
        "note": "Cordon-shaped effect outbox listing",
    }
