"""MemGraphRAG-shaped three-layer global memory (stdlib; no LLM).

Shaped by MemGraphRAG (arXiv:2606.00610): ontology/fact/passage layers,
extract/detect/resolve agents as plans, multi-layer retrieve, PPR-style
propagation proxy. Proxies only — not MemGraphRAG paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

LAYERS = frozenset({"ontology", "fact", "passage"})


def mgr_store_layer(*, content: str, layer: str) -> dict[str, Any]:
    """Store into ontology / fact / passage global memory layer."""
    body = content.strip()
    ly = layer.strip().lower()
    if not body:
        raise SchemaError("content required")
    if ly not in LAYERS:
        raise SchemaError(f"layer must be one of {sorted(LAYERS)}")
    mid = hashlib.sha256(
        canonical_dumps({"c": body, "l": ly}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "layer": ly,
        "ok": True,
        "note": "memgraphrag mgr_store_layer",
    }


def mgr_detect_conflict(*, facts: int, anomalies: int) -> dict[str, Any]:
    """Conflict detection agent proxy over fact layer."""
    if facts < 0 or anomalies < 0:
        raise SchemaError("counts must be >= 0")
    return {
        "conflict": anomalies > 0,
        "anomalies": anomalies,
        "ok": True,
        "note": "memgraphrag mgr_detect_conflict",
    }


def mgr_resolve_plan(*, conflict_id: str) -> dict[str, Any]:
    """Conflict resolution plan — report-only (no auto-write)."""
    cid = conflict_id.strip()
    if not cid:
        raise SchemaError("conflict_id required")
    return {
        "conflict_id": cid[:64],
        "apply": False,
        "ok": True,
        "note": "memgraphrag mgr_resolve_plan",
    }


def mgr_multilayer_retrieve(*, query: str, layers_hit: int) -> dict[str, Any]:
    """Retrieve across ontology/fact/passage layers."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if layers_hit < 0:
        raise SchemaError("layers_hit must be >= 0")
    return {
        "query": q[:120],
        "layers_hit": min(layers_hit, 3),
        "ok": True,
        "note": "memgraphrag mgr_multilayer_retrieve",
    }


def mgr_propagate(*, seeds: int, damping: float = 0.85) -> dict[str, Any]:
    """Personalized PageRank-style graph propagation proxy."""
    if seeds < 0:
        raise SchemaError("seeds must be >= 0")
    if not (0.0 < damping < 1.0):
        raise SchemaError("damping must be in (0, 1)")
    return {
        "seeds": seeds,
        "damping": round(damping, 4),
        "ranked": seeds > 0,
        "ok": True,
        "note": "memgraphrag mgr_propagate",
    }


def mgr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → detect → retrieve → propagate."""
    order = ("store", "detect", "retrieve", "propagate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memgraphrag mgr_loop_plan",
    }
