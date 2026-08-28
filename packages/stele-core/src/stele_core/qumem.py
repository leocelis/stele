"""QUMem-shaped query-conditioned user-state memory (stdlib; no LLM).

Shaped by QUMem (arXiv:2608.16168): semantic-continuity episodes, typed
factual/preference/insight decomposition, multi-query plan, temporal
user-state inference. Proxies only — not QUMem paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

QUMEM_TYPES = frozenset({"factual", "preference", "insight"})


def qumem_segment_episode(*, content: str, continuity: float) -> dict[str, Any]:
    """Segment history into a variable-length episode by semantic continuity."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    if not (0.0 <= continuity <= 1.0):
        raise SchemaError("continuity must be in [0, 1]")
    eid = hashlib.sha256(
        canonical_dumps({"c": body, "k": continuity}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "episode_id": eid,
        "continuity": round(continuity, 4),
        "ok": True,
        "note": "qumem qumem_segment_episode",
    }


def qumem_decompose(*, episode_id: str, mem_type: str) -> dict[str, Any]:
    """Decompose episode into factual / preference / insight memory."""
    ep = episode_id.strip()
    mt = mem_type.strip().lower()
    if not ep:
        raise SchemaError("episode_id required")
    if mt not in QUMEM_TYPES:
        raise SchemaError(f"mem_type must be one of {sorted(QUMEM_TYPES)}")
    mid = hashlib.sha256(
        canonical_dumps({"ep": ep, "t": mt}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "episode_id": ep[:64],
        "mem_type": mt,
        "ok": True,
        "note": "qumem qumem_decompose",
    }


def qumem_plan_queries(*, task: str, needs: int) -> dict[str, Any]:
    """Plan multi-query retrieval over typed stores for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if needs < 1:
        raise SchemaError("needs must be >= 1")
    return {
        "task": t[:120],
        "query_count": needs,
        "ok": True,
        "note": "qumem qumem_plan_queries",
    }


def qumem_infer_user_state(
    *,
    factual: int,
    preference: int,
    insight: int,
) -> dict[str, Any]:
    """Jointly infer user state from typed memory counts."""
    if factual < 0 or preference < 0 or insight < 0:
        raise SchemaError("counts must be >= 0")
    ready = factual > 0 and preference >= 0
    return {
        "ready": ready,
        "evidence": factual + preference + insight,
        "ok": True,
        "note": "qumem qumem_infer_user_state",
    }


def qumem_temporal_valid(
    *,
    event_ts: str,
    query_ts: str,
    stale: bool,
) -> dict[str, Any]:
    """Temporal validity: reject stale preference evidence."""
    et = event_ts.strip()
    qt = query_ts.strip()
    if not et or not qt:
        raise SchemaError("event_ts and query_ts required")
    return {
        "valid": not stale,
        "event_ts": et[:32],
        "query_ts": qt[:32],
        "ok": True,
        "note": "qumem qumem_temporal_valid",
    }


def qumem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Segment → decompose → plan → infer."""
    order = ("segment", "decompose", "plan", "infer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "segment"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qumem qumem_loop_plan",
    }
