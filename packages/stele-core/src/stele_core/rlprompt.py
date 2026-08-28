"""RLPrompt proxies (stdlib; no LLM).

Shaped by RLPrompt (arXiv:2205.12548): RL over discrete soft-prompt
tokens / black-box reward from task feedback. Proxies only.

Prefix ``rlp_*`` — not TEMPERA (``tmpa_*``) / Self-Consistency (``sc_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rlp_init(*, task: str) -> dict[str, Any]:
    """Initialize an RL policy over discrete prompt tokens."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    iid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "policy_id": iid,
        "ok": True,
        "note": "rlp rlp_init",
    }


def rlp_sample(*, policy_id: str) -> dict[str, Any]:
    """Sample a discrete prompt token sequence from the policy."""
    pid = policy_id.strip()
    if not pid:
        raise SchemaError("policy_id required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sample_id": sid,
        "ok": True,
        "note": "rlp rlp_sample",
    }


def rlp_reward(*, sample_id: str, score: int) -> dict[str, Any]:
    """Black-box task reward for the sampled prompt (0–100)."""
    sid = sample_id.strip()
    if not sid:
        raise SchemaError("sample_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    rid = hashlib.sha256(
        canonical_dumps({"s": sid, "r": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reward_id": rid,
        "score": score,
        "ok": True,
        "note": "rlp rlp_reward",
    }


def rlp_update(*, reward_id: str) -> dict[str, Any]:
    """Update the policy from the observed reward."""
    rid = reward_id.strip()
    if not rid:
        raise SchemaError("reward_id required")
    uid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "update_id": uid,
        "ok": True,
        "note": "rlp rlp_update",
    }


def rlp_discrete(*, discrete: bool) -> dict[str, Any]:
    """Flag discrete (API-friendly) soft-prompt search (report-only)."""
    return {
        "discrete": discrete,
        "apply": False,
        "ok": True,
        "note": "rlp rlp_discrete",
    }


def rlp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → sample → reward → update."""
    order = ("init", "sample", "reward", "update")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rlp rlp_loop_plan",
    }
