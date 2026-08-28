"""Skeleton-of-Thought-shaped parallel expand (stdlib; no LLM).

Shaped by Skeleton-of-Thought (arXiv:2307.15337): emit skeleton, extract
points, parallel expand, optional router. Proxies only — no live decode.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sot_emit_skeleton(*, question: str) -> dict[str, Any]:
    """Emit an answer skeleton for a question."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    sid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "skeleton_id": sid,
        "ok": True,
        "note": "sot sot_emit_skeleton",
    }


def sot_extract_points(*, skeleton_id: str, points: int) -> dict[str, Any]:
    """Extract B skeleton points."""
    sid = skeleton_id.strip()
    if not sid:
        raise SchemaError("skeleton_id required")
    if points < 1:
        raise SchemaError("points must be >= 1")
    return {
        "skeleton_id": sid[:64],
        "points": points,
        "ok": True,
        "note": "sot sot_extract_points",
    }


def sot_parallel_expand(*, points: int) -> dict[str, Any]:
    """Expand points in parallel (report-only apply)."""
    if points < 1:
        raise SchemaError("points must be >= 1")
    return {
        "points": points,
        "apply": False,
        "ok": True,
        "note": "sot sot_parallel_expand",
    }


def sot_router(*, suitable: bool) -> dict[str, Any]:
    """SoT-R router gate — only trigger SoT when suitable."""
    return {
        "suitable": suitable,
        "apply": False,
        "ok": True,
        "note": "sot sot_router",
    }


def sot_latency_gain(*, sequential: int, parallel: int) -> dict[str, Any]:
    """Proxy latency comparison (units arbitrary)."""
    if sequential < 0 or parallel < 0:
        raise SchemaError("sequential and parallel must be >= 0")
    return {
        "sequential": sequential,
        "parallel": parallel,
        "faster": parallel < sequential,
        "ok": True,
        "note": "sot sot_latency_gain",
    }


def sot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Skeleton → extract → expand → route."""
    order = ("skeleton", "extract", "expand", "route")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "skeleton"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "sot sot_loop_plan",
    }
