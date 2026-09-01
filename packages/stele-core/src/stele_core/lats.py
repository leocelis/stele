"""LATS-shaped language agent tree search (stdlib; no LLM).

Shaped by Language Agent Tree Search (arXiv:2310.04406): expand,
value, reflect, select with environment feedback. Proxies only —
≠ RAP (Reasoning via Planning) MCTS.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lats_expand(*, state: str, actions: int) -> dict[str, Any]:
    """Expand tree node with candidate actions."""
    s = state.strip()
    if not s:
        raise SchemaError("state required")
    if actions < 1:
        raise SchemaError("actions must be >= 1")
    nid = hashlib.sha256(
        canonical_dumps({"s": s, "a": actions}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "actions": actions,
        "ok": True,
        "note": "lats lats_expand",
    }


def lats_value(*, node_id: str, score: float) -> dict[str, Any]:
    """LM-shaped value estimate for a node."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    if score < 0.0 or score > 1.0:
        raise SchemaError("score must be in [0, 1]")
    vid = hashlib.sha256(
        canonical_dumps({"n": nid, "v": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "value_id": vid,
        "score": score,
        "ok": True,
        "note": "lats lats_value",
    }


def lats_reflect(*, node_id: str, feedback: str) -> dict[str, Any]:
    """Self-reflection from environment / trajectory feedback."""
    nid = node_id.strip()
    f = feedback.strip()
    if not nid or not f:
        raise SchemaError("node_id and feedback required")
    rid = hashlib.sha256(
        canonical_dumps({"n": nid, "f": f}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflect_id": rid,
        "ok": True,
        "note": "lats lats_reflect",
    }


def lats_select(*, node_id: str) -> dict[str, Any]:
    """Select next action / node in the search tree."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    return {
        "node_id": nid[:64],
        "selected": True,
        "ok": True,
        "note": "lats lats_select",
    }


def lats_env_feedback(*, useful: bool) -> dict[str, Any]:
    """Flag external environment feedback (report-only)."""
    return {
        "useful": useful,
        "apply": False,
        "ok": True,
        "note": "lats lats_env_feedback",
    }


def lats_loop_plan(*, phase: str) -> dict[str, Any]:
    """Expand → value → reflect → select."""
    order = ("expand", "value", "reflect", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "expand"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lats lats_loop_plan",
    }
