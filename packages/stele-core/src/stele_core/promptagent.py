"""PromptAgent proxies (stdlib; no LLM).

Shaped by PromptAgent (arXiv:2310.16427): MCTS over prompt states with
self-reflection error feedback as actions. Proxies only.

Prefix ``pag_*`` — not ProTeGi (``ptg_*``) / Active-Prompt (``ap_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pag_state(*, prompt: str) -> dict[str, Any]:
    """Register a prompt as an MCTS state node."""
    p = prompt.strip()
    if not p:
        raise SchemaError("prompt required")
    sid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "state_id": sid,
        "ok": True,
        "note": "pag pag_state",
    }


def pag_reflect(*, state_id: str) -> dict[str, Any]:
    """Self-reflect on model errors to form an insightful action."""
    sid = state_id.strip()
    if not sid:
        raise SchemaError("state_id required")
    rid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflect_id": rid,
        "ok": True,
        "note": "pag pag_reflect",
    }


def pag_expand(*, reflect_id: str) -> dict[str, Any]:
    """Expand the MCTS tree with a refined child prompt."""
    rid = reflect_id.strip()
    if not rid:
        raise SchemaError("reflect_id required")
    eid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "expand_id": eid,
        "ok": True,
        "note": "pag pag_expand",
    }


def pag_backprop(*, expand_id: str, reward: int) -> dict[str, Any]:
    """Backpropagate reward into Q(s,a) beliefs (reward 0–100)."""
    eid = expand_id.strip()
    if not eid:
        raise SchemaError("expand_id required")
    if reward < 0 or reward > 100:
        raise SchemaError("reward must be 0..100")
    bid = hashlib.sha256(
        canonical_dumps({"e": eid, "r": reward}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "back_id": bid,
        "reward": reward,
        "ok": True,
        "note": "pag pag_backprop",
    }


def pag_expert(*, expert_level: bool) -> dict[str, Any]:
    """Flag expert-level prompt target (report-only)."""
    return {
        "expert_level": expert_level,
        "apply": False,
        "ok": True,
        "note": "pag pag_expert",
    }


def pag_loop_plan(*, phase: str) -> dict[str, Any]:
    """State → reflect → expand → backprop."""
    order = ("state", "reflect", "expand", "backprop")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "state"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pag pag_loop_plan",
    }
