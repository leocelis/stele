"""VikingMem-shaped Memory Base (stdlib; no LLM).

Shaped by VikingMem (arXiv:2605.29640): event–entity paradigm, entity
update from events, topic timeline compression, time-weighted recall,
multi-vector rerank proxy. Proxies only — not VikingMem paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def viking_extract_event(*, content: str, high_value: bool) -> dict[str, Any]:
    """Selective event extraction from an information stream."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    eid = hashlib.sha256(
        canonical_dumps({"e": body, "h": high_value}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "event_id": eid,
        "kept": high_value,
        "ok": True,
        "note": "vikingmem viking_extract_event",
    }


def viking_update_entity(*, entity: str, event_id: str) -> dict[str, Any]:
    """Stateful entity evolution driven by an event."""
    ent = entity.strip()
    ev = event_id.strip()
    if not ent or not ev:
        raise SchemaError("entity and event_id required")
    uid = hashlib.sha256(
        canonical_dumps({"en": ent, "ev": ev}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "update_id": uid,
        "entity": ent[:80],
        "event_id": ev[:64],
        "ok": True,
        "note": "vikingmem viking_update_entity",
    }


def viking_timeline_compress(*, topic: str, items: int) -> dict[str, Any]:
    """Topic-wise timeline temporal compression."""
    t = topic.strip()
    if not t:
        raise SchemaError("topic required")
    if items < 0:
        raise SchemaError("items must be >= 0")
    return {
        "topic": t[:80],
        "compressed": items > 1,
        "items": items,
        "ok": True,
        "note": "vikingmem viking_timeline_compress",
    }


def viking_time_weighted_recall(
    *,
    query: str,
    recency_weight: float,
) -> dict[str, Any]:
    """Time-weighted recall prioritizing recent items."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if not (0.0 <= recency_weight <= 1.0):
        raise SchemaError("recency_weight must be in [0, 1]")
    return {
        "query": q[:120],
        "recency_weight": round(recency_weight, 4),
        "ok": True,
        "note": "vikingmem viking_time_weighted_recall",
    }


def viking_rerank(*, candidates: int, top_k: int) -> dict[str, Any]:
    """Multi-vector rerank proxy over candidates."""
    if candidates < 0 or top_k < 1:
        raise SchemaError("candidates >= 0 and top_k >= 1")
    selected = min(candidates, top_k)
    return {
        "selected": selected,
        "top_k": top_k,
        "ok": True,
        "note": "vikingmem viking_rerank",
    }


def viking_loop_plan(*, phase: str) -> dict[str, Any]:
    """Extract → update → compress → recall."""
    order = ("extract", "update", "compress", "recall")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "extract"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "vikingmem viking_loop_plan",
    }
