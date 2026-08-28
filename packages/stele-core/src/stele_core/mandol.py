"""Mandol-shaped agglomerative memory (stdlib; no LLM).

Shaped by Mandol (arXiv:2606.29778): basic + abstract hierarchy, SemanticMap /
SemanticGraph hybrid, query-adaptive routing, token-constrained context.
Proxies only — not Mandol paper scores. No live multi-DB I/O on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mandol_basic_unit(*, content: str) -> dict[str, Any]:
    """Store a basic-layer memory unit."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    uid = hashlib.sha256(
        canonical_dumps({"l": "basic", "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "unit_id": uid,
        "layer": "basic",
        "content": body[:200],
        "ok": True,
        "note": "mandol mandol_basic_unit",
    }


def mandol_agglomerate(*, basic_ids: list[str]) -> dict[str, Any]:
    """Agglomerate basic units into a traceable abstract memory."""
    ids = [i.strip() for i in basic_ids if i.strip()]
    if len(ids) < 2:
        raise SchemaError("at least two basic_ids required")
    aid = hashlib.sha256(
        canonical_dumps({"ids": sorted(ids)}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "abstract_id": aid,
        "parts": len(ids),
        "layer": "abstract",
        "ok": True,
        "note": "mandol mandol_agglomerate",
    }


def mandol_semantic_map_put(*, key: str, vector_ok: bool) -> dict[str, Any]:
    """SemanticMap: key-value + vector fused put."""
    k = key.strip()
    if not k:
        raise SchemaError("key required")
    return {
        "key": k[:64],
        "vector_ok": vector_ok,
        "fused": True,
        "ok": True,
        "note": "mandol mandol_semantic_map_put",
    }


def mandol_hybrid_retrieve(*, vector_hits: int, graph_hops: int) -> dict[str, Any]:
    """Unified hybrid retrieve without cross-DB boundary."""
    if vector_hits < 0 or graph_hops < 0:
        raise SchemaError("counts must be >= 0")
    return {
        "combined": vector_hits + graph_hops,
        "cross_db_io": False,
        "ok": True,
        "note": "mandol mandol_hybrid_retrieve",
    }


def mandol_query_route(*, query_type: str) -> dict[str, Any]:
    """Query-adaptive routing to memory spaces."""
    if query_type not in ("factual", "relational", "temporal"):
        raise SchemaError("query_type must be factual, relational, or temporal")
    space = {
        "factual": "semantic_map",
        "relational": "semantic_graph",
        "temporal": "both",
    }[query_type]
    return {
        "query_type": query_type,
        "space": space,
        "ok": True,
        "note": "mandol mandol_query_route",
    }


def mandol_token_budget(*, selected_tokens: int, max_tokens: int) -> dict[str, Any]:
    """Token-constrained context generation gate."""
    if selected_tokens < 0 or max_tokens < 1:
        raise SchemaError("selected_tokens >= 0 and max_tokens >= 1")
    under = selected_tokens <= max_tokens
    return {
        "under_budget": under,
        "selected_tokens": selected_tokens,
        "max_tokens": max_tokens,
        "ok": True,
        "note": "mandol mandol_token_budget",
    }


def mandol_loop_plan(*, phase: str) -> dict[str, Any]:
    """Basic → agglomerate → retrieve → budget."""
    order = ("basic", "agglomerate", "retrieve", "budget")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "basic"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mandol mandol_loop_plan",
    }
