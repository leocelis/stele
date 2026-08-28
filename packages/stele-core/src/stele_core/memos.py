"""MemOS-shaped MemCube OS (stdlib; no LLM).

Shaped by MemOS (arXiv:2507.03724 / 2505.22101): MemCube units across
plaintext / activation / parametric kinds, scheduler, lifecycle states,
compose/migrate/fuse. Proxies only — not MemOS paper scores. No parameter
writes on core path.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

KINDS = frozenset({"plaintext", "activation", "parametric"})
LIFECYCLE = frozenset({"active", "frozen", "migrating", "fused"})


def memos_create_cube(
    *,
    kind: str,
    content: str,
) -> dict[str, Any]:
    """Create a MemCube with provenance metadata proxy."""
    if kind not in KINDS:
        raise SchemaError(f"kind must be one of {sorted(KINDS)}")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    cid = hashlib.sha256(
        canonical_dumps({"k": kind, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cube_id": cid,
        "kind": kind,
        "content": body[:200],
        "state": "active",
        "ok": True,
        "note": "memos memos_create_cube",
    }


def memos_schedule(
    *,
    strategy: str,
    candidate_count: int,
) -> dict[str, Any]:
    """MemScheduler strategy over candidate cubes."""
    if strategy not in ("lru", "semantic", "label"):
        raise SchemaError("strategy must be lru, semantic, or label")
    if candidate_count < 0:
        raise SchemaError("candidate_count must be >= 0")
    selected = min(1, candidate_count) if candidate_count else 0
    return {
        "strategy": strategy,
        "selected": selected,
        "candidate_count": candidate_count,
        "ok": True,
        "note": "memos memos_schedule",
    }


def memos_lifecycle(
    *,
    state: str,
    action: str,
) -> dict[str, Any]:
    """Lifecycle state machine: freeze / thaw / migrate."""
    if state not in LIFECYCLE:
        raise SchemaError(f"state must be one of {sorted(LIFECYCLE)}")
    if action not in ("freeze", "thaw", "migrate", "fuse"):
        raise SchemaError("action must be freeze, thaw, migrate, or fuse")
    transitions = {
        ("active", "freeze"): "frozen",
        ("frozen", "thaw"): "active",
        ("active", "migrate"): "migrating",
        ("migrating", "fuse"): "fused",
        ("active", "fuse"): "fused",
    }
    nxt = transitions.get((state, action))
    return {
        "from_state": state,
        "action": action,
        "to_state": nxt,
        "ok": nxt is not None,
        "note": "memos memos_lifecycle",
    }


def memos_compose(
    *,
    cube_ids: list[str],
) -> dict[str, Any]:
    """Compose multiple MemCubes into one logical unit."""
    ids = [c.strip() for c in cube_ids if c.strip()]
    if len(ids) < 2:
        raise SchemaError("at least two cube_ids required")
    cid = hashlib.sha256(
        canonical_dumps({"ids": sorted(ids)}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "composed_id": cid,
        "parts": len(ids),
        "ok": True,
        "note": "memos memos_compose",
    }


def memos_migrate(
    *,
    from_kind: str,
    to_kind: str,
) -> dict[str, Any]:
    """Migrate between memory kinds (report-only; no param write)."""
    if from_kind not in KINDS or to_kind not in KINDS:
        raise SchemaError(f"kinds must be one of {sorted(KINDS)}")
    allowed = from_kind != to_kind
    return {
        "from_kind": from_kind,
        "to_kind": to_kind,
        "allowed": allowed,
        "apply": False,
        "ok": True,
        "note": "memos memos_migrate",
    }


def memos_fuse_gate(
    *,
    compatible: bool,
    conflict: bool,
) -> dict[str, Any]:
    """Fuse gate: compatible and not conflicted."""
    fuse = compatible and not conflict
    return {
        "fuse": fuse,
        "apply": False,
        "ok": True,
        "note": "memos memos_fuse_gate",
    }


def memos_loop_plan(*, phase: str) -> dict[str, Any]:
    """Create → schedule → lifecycle → compose."""
    order = ("create", "schedule", "lifecycle", "compose")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "create"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memos memos_loop_plan",
    }
