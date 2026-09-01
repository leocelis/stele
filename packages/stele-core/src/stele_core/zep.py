"""Zep/Graphiti-shaped temporal knowledge graph memory (stdlib; no LLM).

Shaped by Zep (arXiv:2501.13956): Graphiti temporal KG, bi-temporal edges,
conversation + business data synthesis, cross-session retrieve. Proxies
only — not Zep paper scores. No live Graphiti broker on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def zep_add_episode(*, content: str, valid_at: str) -> dict[str, Any]:
    """Ingest an episode into the temporal graph."""
    body = content.strip()
    ts = valid_at.strip()
    if not body or not ts:
        raise SchemaError("content and valid_at required")
    eid = hashlib.sha256(
        canonical_dumps({"c": body, "v": ts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "episode_id": eid,
        "valid_at": ts[:40],
        "ok": True,
        "note": "zep zep_add_episode",
    }


def zep_link_entities(
    *,
    entity_a: str,
    entity_b: str,
    relation: str,
) -> dict[str, Any]:
    """Create a graph edge between entities."""
    a = entity_a.strip()
    b = entity_b.strip()
    r = relation.strip()
    if not a or not b or not r:
        raise SchemaError("entity_a, entity_b, and relation required")
    lid = hashlib.sha256(
        canonical_dumps({"a": a, "b": b, "r": r}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edge_id": lid,
        "relation": r[:64],
        "ok": True,
        "note": "zep zep_link_entities",
    }


def zep_bitemporal(
    *,
    valid_at: str,
    transaction_at: str,
) -> dict[str, Any]:
    """Bi-temporal stamp: valid time vs transaction time."""
    v = valid_at.strip()
    t = transaction_at.strip()
    if not v or not t:
        raise SchemaError("valid_at and transaction_at required")
    return {
        "valid_at": v[:40],
        "transaction_at": t[:40],
        "ok": True,
        "note": "zep zep_bitemporal",
    }


def zep_synthesize(
    *,
    conversation_facts: int,
    business_facts: int,
) -> dict[str, Any]:
    """Synthesize unstructured conversation + structured business data."""
    if conversation_facts < 0 or business_facts < 0:
        raise SchemaError("counts must be >= 0")
    return {
        "total_facts": conversation_facts + business_facts,
        "ok": True,
        "note": "zep zep_synthesize",
    }


def zep_cross_session(
    *,
    sessions: int,
    min_sessions: int = 2,
) -> dict[str, Any]:
    """Cross-session information synthesis gate."""
    if sessions < 0 or min_sessions < 1:
        raise SchemaError("sessions >= 0 and min_sessions >= 1")
    synthesize = sessions >= min_sessions
    return {
        "synthesize": synthesize,
        "sessions": sessions,
        "ok": True,
        "note": "zep zep_cross_session",
    }


def zep_loop_plan(*, phase: str) -> dict[str, Any]:
    """Episode → link → bitemporal → retrieve."""
    order = ("episode", "link", "bitemporal", "retrieve")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "episode"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "zep zep_loop_plan",
    }
