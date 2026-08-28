"""RAPTOR-shaped recursive tree retrieval (stdlib; no LLM).

Shaped by RAPTOR (arXiv:2401.18059): recursive embed/cluster/summarize
tree, tree-traversal vs collapsed-tree retrieve. Proxies only — not
RAPTOR paper scores. No embeddings/LLM on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def raptor_embed_chunk(*, content: str) -> dict[str, Any]:
    """Leaf chunk identity (embedding proxy via content hash)."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    cid = hashlib.sha256(
        canonical_dumps({"c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "chunk_id": cid,
        "ok": True,
        "note": "raptor raptor_embed_chunk",
    }


def raptor_cluster(*, chunks: int, clusters: int) -> dict[str, Any]:
    """Cluster leaf chunks before recursive summarization."""
    if chunks < 0 or clusters < 0:
        raise SchemaError("chunks and clusters must be >= 0")
    if clusters > chunks and chunks > 0:
        raise SchemaError("clusters cannot exceed chunks")
    return {
        "chunks": chunks,
        "clusters": clusters,
        "ok": True,
        "note": "raptor raptor_cluster",
    }


def raptor_summarize_node(*, level: int, children: int) -> dict[str, Any]:
    """Build a summary node from clustered children (report-only)."""
    if level < 0 or children < 0:
        raise SchemaError("level and children must be >= 0")
    nid = hashlib.sha256(
        canonical_dumps({"l": level, "n": children}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "level": level,
        "apply": False,
        "ok": True,
        "note": "raptor raptor_summarize_node",
    }


def raptor_tree_traverse(*, depth: int, keep_per_level: int) -> dict[str, Any]:
    """Layer-by-layer tree traversal with pruning."""
    if depth < 0 or keep_per_level < 1:
        raise SchemaError("depth >= 0 and keep_per_level >= 1")
    return {
        "depth": depth,
        "keep_per_level": keep_per_level,
        "ok": True,
        "note": "raptor raptor_tree_traverse",
    }


def raptor_collapsed_retrieve(*, candidates: int, top_k: int) -> dict[str, Any]:
    """Collapsed tree: score nodes across all layers together."""
    if candidates < 0 or top_k < 1:
        raise SchemaError("candidates >= 0 and top_k >= 1")
    return {
        "selected": min(candidates, top_k),
        "top_k": top_k,
        "ok": True,
        "note": "raptor raptor_collapsed_retrieve",
    }


def raptor_loop_plan(*, phase: str) -> dict[str, Any]:
    """Embed → cluster → summarize → retrieve."""
    order = ("embed", "cluster", "summarize", "retrieve")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "embed"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "raptor raptor_loop_plan",
    }
