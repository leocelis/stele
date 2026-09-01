"""Graph-of-Thoughts-shaped arbitrary DAG reasoning (stdlib; no LLM).

Shaped by Graph of Thoughts (arXiv:2308.09687): add vertices/edges,
aggregate, feedback, score. Proxies only — not SPCL GoT runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def got_add_thought(*, text: str) -> dict[str, Any]:
    """Add a thought vertex."""
    t = text.strip()
    if not t:
        raise SchemaError("text required")
    vid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "vertex_id": vid,
        "ok": True,
        "note": "got got_add_thought",
    }


def got_link(*, src: str, dst: str) -> dict[str, Any]:
    """Add a dependency edge between thoughts."""
    s = src.strip()
    d = dst.strip()
    if not s or not d:
        raise SchemaError("src and dst required")
    eid = hashlib.sha256(
        canonical_dumps({"s": s, "d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edge_id": eid,
        "src": s[:64],
        "dst": d[:64],
        "ok": True,
        "note": "got got_link",
    }


def got_aggregate(*, inputs: int) -> dict[str, Any]:
    """Aggregate multiple thoughts into one (report-only apply)."""
    if inputs < 1:
        raise SchemaError("inputs must be >= 1")
    return {
        "inputs": inputs,
        "apply": False,
        "ok": True,
        "note": "got got_aggregate",
    }


def got_feedback(*, vertex_id: str) -> dict[str, Any]:
    """Feedback loop onto a thought (report-only)."""
    v = vertex_id.strip()
    if not v:
        raise SchemaError("vertex_id required")
    return {
        "vertex_id": v[:64],
        "apply": False,
        "ok": True,
        "note": "got got_feedback",
    }


def got_score_graph(*, vertices: int, edges: int) -> dict[str, Any]:
    """Score graph size as a proxy quality signal."""
    if vertices < 0 or edges < 0:
        raise SchemaError("vertices and edges must be >= 0")
    return {
        "vertices": vertices,
        "edges": edges,
        "ok": True,
        "note": "got got_score_graph",
    }


def got_loop_plan(*, phase: str) -> dict[str, Any]:
    """Add → link → aggregate → score."""
    order = ("add", "link", "aggregate", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "add"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "got got_loop_plan",
    }
