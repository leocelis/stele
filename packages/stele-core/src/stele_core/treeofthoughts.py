"""Tree-of-Thoughts-shaped deliberate search (stdlib; no LLM).

Shaped by Tree of Thoughts (arXiv:2305.10601): propose thoughts, evaluate,
expand BFS/DFS, backtrack. Proxies only — not Princeton ToT runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tot_propose(*, parent_id: str, text: str) -> dict[str, Any]:
    """Propose a thought node under a parent."""
    p = parent_id.strip()
    t = text.strip()
    if not p:
        raise SchemaError("parent_id required")
    if not t:
        raise SchemaError("text required")
    nid = hashlib.sha256(
        canonical_dumps({"p": p, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "parent_id": p[:64],
        "ok": True,
        "note": "tot tot_propose",
    }


def tot_evaluate(*, node_id: str, score: float) -> dict[str, Any]:
    """Self-evaluate a thought (0..1)."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    if score < 0.0 or score > 1.0:
        raise SchemaError("score must be in [0, 1]")
    return {
        "node_id": nid[:64],
        "score": score,
        "ok": True,
        "note": "tot tot_evaluate",
    }


def tot_expand(*, breadth: int, depth: int) -> dict[str, Any]:
    """Record BFS/DFS expansion budget."""
    if breadth < 1 or depth < 1:
        raise SchemaError("breadth and depth must be >= 1")
    return {
        "breadth": breadth,
        "depth": depth,
        "ok": True,
        "note": "tot tot_expand",
    }


def tot_backtrack(*, from_node: str) -> dict[str, Any]:
    """Backtrack from a failed leaf (report-only)."""
    n = from_node.strip()
    if not n:
        raise SchemaError("from_node required")
    return {
        "from_node": n[:64],
        "apply": False,
        "ok": True,
        "note": "tot tot_backtrack",
    }


def tot_select_best(*, candidates: int) -> dict[str, Any]:
    """Select best thought among candidates."""
    if candidates < 0:
        raise SchemaError("candidates must be >= 0")
    return {
        "candidates": candidates,
        "selected": candidates > 0,
        "ok": True,
        "note": "tot tot_select_best",
    }


def tot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Propose → evaluate → expand → select."""
    order = ("propose", "evaluate", "expand", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tot tot_loop_plan",
    }
