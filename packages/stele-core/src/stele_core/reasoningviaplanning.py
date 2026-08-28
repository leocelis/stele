"""Reasoning-via-Planning (RAP) shaped MCTS proxies (stdlib; no LLM).

Shaped by RAP (arXiv:2305.14992): world-model state, expand, reward,
select path. Proxies only — not Hao et al. MCTS / llm-reasoners.
Distinct from RAPTOR (`raptor.py`).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rap_world_state(*, state: str) -> dict[str, Any]:
    """Record world-model predicted state."""
    s = state.strip()
    if not s:
        raise SchemaError("state required")
    sid = hashlib.sha256(
        canonical_dumps({"s": s}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "state_id": sid,
        "ok": True,
        "note": "rap rap_world_state",
    }


def rap_expand(*, state_id: str, actions: int) -> dict[str, Any]:
    """Expand MCTS children from a state."""
    sid = state_id.strip()
    if not sid:
        raise SchemaError("state_id required")
    if actions < 1:
        raise SchemaError("actions must be >= 1")
    return {
        "state_id": sid[:64],
        "actions": actions,
        "ok": True,
        "note": "rap rap_expand",
    }


def rap_reward(*, state_id: str, reward: float) -> dict[str, Any]:
    """Assign reward to a state (0..1)."""
    sid = state_id.strip()
    if not sid:
        raise SchemaError("state_id required")
    if reward < 0.0 or reward > 1.0:
        raise SchemaError("reward must be in [0, 1]")
    return {
        "state_id": sid[:64],
        "reward": reward,
        "ok": True,
        "note": "rap rap_reward",
    }


def rap_select_path(*, visits: int) -> dict[str, Any]:
    """Select high-reward path after MCTS visits (report-only)."""
    if visits < 0:
        raise SchemaError("visits must be >= 0")
    return {
        "visits": visits,
        "apply": False,
        "ok": True,
        "note": "rap rap_select_path",
    }


def rap_balance(*, explore: float) -> dict[str, Any]:
    """Exploration vs exploitation balance (0..1)."""
    if explore < 0.0 or explore > 1.0:
        raise SchemaError("explore must be in [0, 1]")
    return {
        "explore": explore,
        "ok": True,
        "note": "rap rap_balance",
    }


def rap_loop_plan(*, phase: str) -> dict[str, Any]:
    """State → expand → reward → select."""
    order = ("state", "expand", "reward", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "state"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rap rap_loop_plan",
    }
