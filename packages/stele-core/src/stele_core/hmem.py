"""H-Mem-shaped hybrid tree–graph memory (stdlib; no LLM / no graph DB).

Shaped by H-Mem (arXiv:2605.15701): temporal-semantic tree (STM→LTM),
entity knowledge graph, hybrid retrieval (bottom-up tree + multi-hop).
Proxies only — not H-Mem paper scores. Distinct from H-MEM §levels (2507.22925).
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hmem_leaf_event(
    *,
    topic: str,
    timestamp: str,
) -> dict[str, Any]:
    """Leaf node: short-term event with topic + timestamp."""
    top = topic.strip()
    ts = timestamp.strip()
    if not top or not ts:
        raise SchemaError("topic and timestamp required")
    nid = hashlib.sha256(
        canonical_dumps({"t": top, "ts": ts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "topic": top[:80],
        "timestamp": ts[:40],
        "level": "leaf",
        "ok": True,
        "note": "hmem hmem_leaf_event",
    }


def hmem_consolidate_nodes(
    *,
    time_gap: float,
    max_gap: float = 1.0,
    same_topic: bool,
) -> dict[str, Any]:
    """Consolidate nearby same-topic nodes into long-term summary."""
    if time_gap < 0 or max_gap < 0:
        raise SchemaError("time_gap and max_gap must be >= 0")
    consolidate = same_topic and time_gap <= max_gap
    return {
        "consolidate": consolidate,
        "to_long_term": consolidate,
        "ok": True,
        "note": "hmem hmem_consolidate_nodes",
    }


def hmem_link_entities(
    *,
    entity_a: str,
    entity_b: str,
    relation: str,
) -> dict[str, Any]:
    """Add a knowledge-graph edge between entities."""
    a = entity_a.strip()
    b = entity_b.strip()
    rel = relation.strip()
    if not a or not b or not rel:
        raise SchemaError("entity_a, entity_b, and relation required")
    eid = hashlib.sha256(
        canonical_dumps({"a": a, "b": b, "r": rel}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edge_id": eid,
        "entity_a": a[:60],
        "entity_b": b[:60],
        "relation": rel[:60],
        "ok": True,
        "note": "hmem hmem_link_entities",
    }


def hmem_decompose_query(
    *,
    sub_queries: Sequence[str],
) -> dict[str, Any]:
    """Decompose a query into sub-queries for hybrid retrieval workflows."""
    if not isinstance(sub_queries, Sequence) or isinstance(
        sub_queries, (str, bytes)
    ):
        raise SchemaError("sub_queries sequence required")
    cleaned = [str(s).strip() for s in sub_queries if str(s).strip()]
    if not cleaned:
        raise SchemaError("sub_queries required")
    return {
        "sub_queries": cleaned[:10],
        "count": len(cleaned),
        "ok": True,
        "note": "hmem hmem_decompose_query",
    }


def hmem_hybrid_retrieve(
    *,
    tree_hits: int,
    graph_hops: int,
) -> dict[str, Any]:
    """Combine bottom-up tree hits with multi-hop graph evidence."""
    if tree_hits < 0 or graph_hops < 0:
        raise SchemaError("tree_hits and graph_hops must be >= 0")
    return {
        "evidence_score": tree_hits + graph_hops,
        "hybrid": tree_hits > 0 and graph_hops > 0,
        "ok": True,
        "note": "hmem hmem_hybrid_retrieve",
    }


def hmem_evolution_gate(
    *,
    short_term_count: int,
    consolidated_count: int,
) -> dict[str, Any]:
    """Evolution progress: fraction of STM promoted to LTM summaries."""
    if short_term_count < 0 or consolidated_count < 0:
        raise SchemaError("counts must be >= 0")
    if short_term_count == 0:
        ratio = 0.0
    else:
        ratio = min(1.0, consolidated_count / short_term_count)
    return {
        "evolution_ratio": round(ratio, 4),
        "apply": False,
        "ok": True,
        "note": "hmem hmem_evolution_gate",
    }
