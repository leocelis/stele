"""MemWalker-shaped interactive summary-tree reading (stdlib; no LLM).

Shaped by MemWalker (arXiv:2310.05029): segment → summary tree, navigate
from root, choose child / revert, gather leaf evidence. Proxies only —
not MemWalker paper scores. No LLM prompting on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def memwalker_segment(*, content: str, chunk_size: int) -> dict[str, Any]:
    """Split long text into segments that fit a context budget."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    if chunk_size < 1:
        raise SchemaError("chunk_size must be >= 1")
    n = max(1, (len(body) + chunk_size - 1) // chunk_size)
    return {
        "segments": n,
        "chunk_size": chunk_size,
        "ok": True,
        "note": "memwalker memwalker_segment",
    }


def memwalker_build_node(*, summary: str, level: int) -> dict[str, Any]:
    """Build a summary node at a tree level (0=leaf)."""
    s = summary.strip()
    if not s:
        raise SchemaError("summary required")
    if level < 0:
        raise SchemaError("level must be >= 0")
    nid = hashlib.sha256(
        canonical_dumps({"s": s, "l": level}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "level": level,
        "ok": True,
        "note": "memwalker memwalker_build_node",
    }


def memwalker_navigate(
    *,
    node_id: str,
    action: str,
) -> dict[str, Any]:
    """Navigate: choose child path, stay, or revert to parent."""
    nid = node_id.strip()
    act = action.strip().lower()
    if not nid:
        raise SchemaError("node_id required")
    if act not in ("child", "revert", "stay", "answer"):
        raise SchemaError("action must be child|revert|stay|answer")
    return {
        "node_id": nid[:64],
        "action": act,
        "ok": True,
        "note": "memwalker memwalker_navigate",
    }


def memwalker_gather(*, leaves: int, budget: int) -> dict[str, Any]:
    """Gather leaf evidence under a token budget."""
    if leaves < 0 or budget < 1:
        raise SchemaError("leaves >= 0 and budget >= 1")
    return {
        "selected": min(leaves, budget),
        "budget": budget,
        "ok": True,
        "note": "memwalker memwalker_gather",
    }


def memwalker_path_gate(*, depth: int, max_depth: int) -> dict[str, Any]:
    """Path depth gate during navigation."""
    if depth < 0 or max_depth < 1:
        raise SchemaError("depth >= 0 and max_depth >= 1")
    return {
        "within": depth <= max_depth,
        "depth": depth,
        "ok": True,
        "note": "memwalker memwalker_path_gate",
    }


def memwalker_loop_plan(*, phase: str) -> dict[str, Any]:
    """Segment → build → navigate → gather."""
    order = ("segment", "build", "navigate", "gather")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "segment"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memwalker memwalker_loop_plan",
    }
