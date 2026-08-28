"""TEMPERA proxies (stdlib; no LLM).

Shaped by TEMPERA (arXiv:2211.11890): test-time RL editing of
instructions, exemplars, and verbalizers per query. Proxies only.

Prefix ``tmpa_*`` — not Self-Consistency temperature (``sc_temperature``)
or RLPrompt (``rlp_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tmpa_state(*, prompt: str, query: str) -> dict[str, Any]:
    """Register MDP state s=(p0, x) for a query-adaptive edit."""
    p = prompt.strip()
    q = query.strip()
    if not p or not q:
        raise SchemaError("prompt and query required")
    sid = hashlib.sha256(
        canonical_dumps({"p": p, "q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "state_id": sid,
        "ok": True,
        "note": "tmpa tmpa_state",
    }


def tmpa_act(*, state_id: str, component: str) -> dict[str, Any]:
    """Select an edit action over instruction|exemplar|verbalizer."""
    sid = state_id.strip()
    if not sid:
        raise SchemaError("state_id required")
    allowed = ("instruction", "exemplar", "verbalizer")
    if component not in allowed:
        raise SchemaError(f"component must be one of {list(allowed)}")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": component}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "act_id": aid,
        "component": component,
        "ok": True,
        "note": "tmpa tmpa_act",
    }


def tmpa_reward(*, act_id: str, score: int) -> dict[str, Any]:
    """Step reward from label log-prob difference (score 0–100)."""
    aid = act_id.strip()
    if not aid:
        raise SchemaError("act_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    rid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reward_id": rid,
        "score": score,
        "ok": True,
        "note": "tmpa tmpa_reward",
    }


def tmpa_adapt(*, reward_id: str) -> dict[str, Any]:
    """Commit the query-adaptive edited prompt."""
    rid = reward_id.strip()
    if not rid:
        raise SchemaError("reward_id required")
    pid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": pid,
        "ok": True,
        "note": "tmpa tmpa_adapt",
    }


def tmpa_efficiency(*, sample_efficient: bool) -> dict[str, Any]:
    """Flag sample-efficiency claim vs fine-tuning (report-only)."""
    return {
        "sample_efficient": sample_efficient,
        "apply": False,
        "ok": True,
        "note": "tmpa tmpa_efficiency",
    }


def tmpa_loop_plan(*, phase: str) -> dict[str, Any]:
    """State → act → reward → adapt."""
    order = ("state", "act", "reward", "adapt")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "state"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tmpa tmpa_loop_plan",
    }
