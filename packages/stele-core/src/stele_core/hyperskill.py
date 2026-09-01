"""HyperSkill-shaped hypergraph skill memory (stdlib; no LLM).

Shaped by HyperSkill (arXiv:2608.16114): subtask + skill nodes, trajectory
hyperedges, dual-path retrieve, co-occurrence rank, structure-informed
prune/merge. Proxies only — not HyperSkill paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hyperskill_add_subtask(*, label: str) -> dict[str, Any]:
    """Add a subtask node."""
    body = label.strip()
    if not body:
        raise SchemaError("label required")
    nid = hashlib.sha256(
        canonical_dumps({"t": "subtask", "l": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "kind": "subtask",
        "label": body[:80],
        "ok": True,
        "note": "hyperskill hyperskill_add_subtask",
    }


def hyperskill_add_skill(*, label: str) -> dict[str, Any]:
    """Add a reusable skill node."""
    body = label.strip()
    if not body:
        raise SchemaError("label required")
    nid = hashlib.sha256(
        canonical_dumps({"t": "skill", "l": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "kind": "skill",
        "label": body[:80],
        "ok": True,
        "note": "hyperskill hyperskill_add_skill",
    }


def hyperskill_add_hyperedge(
    *,
    subtask_ids: list[str],
    skill_ids: list[str],
    utility: float,
) -> dict[str, Any]:
    """Hyperedge linking subtasks + skills from one trajectory."""
    if not subtask_ids and not skill_ids:
        raise SchemaError("at least one subtask or skill id required")
    if not (0.0 <= utility <= 1.0):
        raise SchemaError("utility must be in [0, 1]")
    eid = hashlib.sha256(
        canonical_dumps(
            {"u": sorted(subtask_ids), "s": sorted(skill_ids), "y": utility}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hyperedge_id": eid,
        "subtask_count": len(subtask_ids),
        "skill_count": len(skill_ids),
        "utility": utility,
        "ok": True,
        "note": "hyperskill hyperskill_add_hyperedge",
    }


def hyperskill_dual_path_retrieve(
    *,
    subtask_hits: int,
    trajectory_hits: int,
) -> dict[str, Any]:
    """Dual-path: subtask + trajectory levels."""
    if subtask_hits < 0 or trajectory_hits < 0:
        raise SchemaError("hit counts must be >= 0")
    return {
        "subtask_hits": subtask_hits,
        "trajectory_hits": trajectory_hits,
        "combined": subtask_hits + trajectory_hits,
        "ok": True,
        "note": "hyperskill hyperskill_dual_path_retrieve",
    }


def hyperskill_rank_skills(
    *,
    cooccurrence: int,
    utility: float,
) -> dict[str, Any]:
    """Rank skill by co-occurrence × utility."""
    if cooccurrence < 0:
        raise SchemaError("cooccurrence must be >= 0")
    if not (0.0 <= utility <= 1.0):
        raise SchemaError("utility must be in [0, 1]")
    score = round(cooccurrence * utility, 4)
    return {
        "score": score,
        "cooccurrence": cooccurrence,
        "utility": utility,
        "ok": True,
        "note": "hyperskill hyperskill_rank_skills",
    }


def hyperskill_maintain_plan(
    *,
    utility: float,
    prune_below: float = 0.2,
    redundant: bool = False,
) -> dict[str, Any]:
    """Structure-informed maintenance: prune low utility / merge redundant."""
    if not (0.0 <= utility <= 1.0) or not (0.0 <= prune_below <= 1.0):
        raise SchemaError("utility and prune_below must be in [0, 1]")
    prune = utility < prune_below
    merge = redundant and not prune
    return {
        "prune": prune,
        "merge": merge,
        "apply": False,
        "ok": True,
        "note": "hyperskill hyperskill_maintain_plan",
    }


def hyperskill_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → retrieve → rank → maintain."""
    order = ("store", "retrieve", "rank", "maintain")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hyperskill hyperskill_loop_plan",
    }
