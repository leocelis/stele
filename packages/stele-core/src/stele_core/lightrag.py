"""LightRAG-shaped dual-level graph+vector retrieval (stdlib; no LLM).

Shaped by LightRAG (EMNLP 2025 Findings): entity/relation dual indexing,
low+high level retrieve, incremental update, graph-vector fuse.
Proxies only — not LightRAG paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lightrag_index_entity(*, name: str) -> dict[str, Any]:
    """Index an entity node (low-level knowledge)."""
    n = name.strip()
    if not n:
        raise SchemaError("name required")
    eid = hashlib.sha256(
        canonical_dumps({"e": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entity_id": eid,
        "name": n[:80],
        "ok": True,
        "note": "lightrag lightrag_index_entity",
    }


def lightrag_index_relation(*, src: str, dst: str, rel: str) -> dict[str, Any]:
    """Index a relation edge between entities."""
    s = src.strip()
    d = dst.strip()
    r = rel.strip()
    if not s or not d or not r:
        raise SchemaError("src, dst, and rel required")
    rid = hashlib.sha256(
        canonical_dumps({"s": s, "d": d, "r": r}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "relation_id": rid,
        "ok": True,
        "note": "lightrag lightrag_index_relation",
    }


def lightrag_dual_retrieve(*, query: str, level: str) -> dict[str, Any]:
    """Dual-level retrieve: low (entities) or high (themes/relations)."""
    q = query.strip()
    lv = level.strip().lower()
    if not q:
        raise SchemaError("query required")
    if lv not in ("low", "high", "both"):
        raise SchemaError("level must be low|high|both")
    return {
        "query": q[:120],
        "level": lv,
        "ok": True,
        "note": "lightrag lightrag_dual_retrieve",
    }


def lightrag_incremental_update(*, new_docs: int) -> dict[str, Any]:
    """Incremental index update without full rebuild."""
    if new_docs < 0:
        raise SchemaError("new_docs must be >= 0")
    return {
        "new_docs": new_docs,
        "incremental": True,
        "ok": True,
        "note": "lightrag lightrag_incremental_update",
    }


def lightrag_graph_vector_fuse(
    *,
    graph_hits: int,
    vector_hits: int,
) -> dict[str, Any]:
    """Fuse graph and vector retrieval results."""
    if graph_hits < 0 or vector_hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "total": graph_hits + vector_hits,
        "ok": True,
        "note": "lightrag lightrag_graph_vector_fuse",
    }


def lightrag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Index → dual → fuse → update."""
    order = ("index", "dual", "fuse", "update")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "index"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lightrag lightrag_loop_plan",
    }
