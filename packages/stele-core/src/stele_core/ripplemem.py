"""RippleMem-shaped associative recollection (stdlib; no LLM).

Shaped by RippleMem (arXiv:2608.13334): episodic units, entity-centric
memory graph, seed retrieval then adaptive associative ripple expansion.
Proxies only — not RippleMem paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ripple_store_episode(*, content: str) -> dict[str, Any]:
    """Store an episodic memory unit."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    eid = hashlib.sha256(
        canonical_dumps({"e": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "episode_id": eid,
        "content": body[:200],
        "ok": True,
        "note": "ripplemem ripple_store_episode",
    }


def ripple_link_entity(*, episode_id: str, entity: str) -> dict[str, Any]:
    """Attach an entity node to an episode in the memory graph."""
    ep = episode_id.strip()
    ent = entity.strip()
    if not ep or not ent:
        raise SchemaError("episode_id and entity required")
    lid = hashlib.sha256(
        canonical_dumps({"ep": ep, "en": ent}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "link_id": lid,
        "episode_id": ep[:64],
        "entity": ent[:80],
        "ok": True,
        "note": "ripplemem ripple_link_entity",
    }


def ripple_seed_retrieve(*, query: str, seed_hits: int) -> dict[str, Any]:
    """Seed retrieval: first-shot isolated hits."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if seed_hits < 0:
        raise SchemaError("seed_hits must be >= 0")
    return {
        "query": q[:120],
        "seed_hits": seed_hits,
        "ok": True,
        "note": "ripplemem ripple_seed_retrieve",
    }


def ripple_expand(
    *,
    seeds: int,
    hop: int,
    max_hops: int = 2,
) -> dict[str, Any]:
    """Adaptive associative ripple: expand from seeds by hop."""
    if seeds < 0 or hop < 0 or max_hops < 1:
        raise SchemaError("seeds/hop >= 0 and max_hops >= 1")
    expand = seeds > 0 and hop <= max_hops
    return {
        "expand": expand,
        "hop": hop,
        "max_hops": max_hops,
        "ok": True,
        "note": "ripplemem ripple_expand",
    }


def ripple_recollect_gate(
    *,
    seed_hits: int,
    associated: int,
) -> dict[str, Any]:
    """Recollection completeness: seeds + associated evidence."""
    if seed_hits < 0 or associated < 0:
        raise SchemaError("counts must be >= 0")
    complete = seed_hits > 0 and associated >= seed_hits
    return {
        "complete": complete,
        "total": seed_hits + associated,
        "ok": True,
        "note": "ripplemem ripple_recollect_gate",
    }


def ripple_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → seed → expand → recollect."""
    order = ("store", "seed", "expand", "recollect")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ripplemem ripple_loop_plan",
    }
