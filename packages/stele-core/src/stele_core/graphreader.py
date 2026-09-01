"""GraphReader-shaped graph exploration agent (stdlib; no LLM).

Shaped by GraphReader (arXiv:2406.14550): structure long text as a graph,
coarse-to-fine explore via read node/neighbors, note insights, reflect.
Proxies only — not the paper's LLM agent loop.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def graphreader_build_node(*, chunk: str) -> dict[str, Any]:
    """Register a graph node from a text chunk."""
    c = chunk.strip()
    if not c:
        raise SchemaError("chunk required")
    node_id = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": node_id,
        "ok": True,
        "note": "graphreader graphreader_build_node",
    }


def graphreader_read_node(*, node_id: str) -> dict[str, Any]:
    """Read node content (coarse exploration step)."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    return {
        "node_id": nid[:64],
        "read": True,
        "ok": True,
        "note": "graphreader graphreader_read_node",
    }


def graphreader_read_neighbors(*, node_id: str, hops: int = 1) -> dict[str, Any]:
    """Read neighbor nodes (fine exploration)."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    if hops < 1:
        raise SchemaError("hops must be >= 1")
    return {
        "node_id": nid[:64],
        "neighbors": hops,
        "ok": True,
        "note": "graphreader graphreader_read_neighbors",
    }


def graphreader_note_insight(*, text: str) -> dict[str, Any]:
    """Record an insight note during exploration."""
    t = text.strip()
    if not t:
        raise SchemaError("text required")
    note_id = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "note_id": note_id,
        "ok": True,
        "note": "graphreader graphreader_note_insight",
    }


def graphreader_reflect_plan(*, enough: bool) -> dict[str, Any]:
    """Reflect whether enough info gathered (report-only)."""
    return {
        "enough": enough,
        "apply": False,
        "ok": True,
        "note": "graphreader graphreader_reflect_plan",
    }


def graphreader_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plan → read → note → reflect."""
    order = ("plan", "read", "note", "reflect")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plan"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "graphreader graphreader_loop_plan",
    }
