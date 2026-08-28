"""TensLoRA proxies (stdlib; no LLM).

Shaped by TensLoRA (arXiv:2509.19391): stack LoRA updates into
a higher-order tensor, Tucker-factor it, and set per-mode ranks.
Proxies only.

Prefix ``tnl_*`` — not LoRTA (``lrt_*``) / TeRA (``ter_*``) /
AdaZeta (``azt_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tnl_stack(*, task: str) -> dict[str, Any]:
    """Stack Q/K/V × layer LoRA updates into one tensor."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "stack_id": sid,
        "ok": True,
        "note": "tnl tnl_stack",
    }


def tnl_tucker(*, stack_id: str, ranks: int) -> dict[str, Any]:
    """Tucker-factor the stacked tensor (ranks >= 1)."""
    sid = stack_id.strip()
    if not sid:
        raise SchemaError("stack_id required")
    if ranks < 1:
        raise SchemaError("ranks must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid, "r": ranks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tucker_id": tid,
        "ranks": ranks,
        "ok": True,
        "note": "tnl tnl_tucker",
    }


def tnl_mode(*, tucker_id: str) -> dict[str, Any]:
    """Set per-mode compression (heads vs QKV vs depth)."""
    tid = tucker_id.strip()
    if not tid:
        raise SchemaError("tucker_id required")
    mid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mode_id": mid,
        "ok": True,
        "note": "tnl tnl_mode",
    }


def tnl_score(*, mode_id: str, score: int) -> dict[str, Any]:
    """Score TensLoRA run (0–100)."""
    mid = mode_id.strip()
    if not mid:
        raise SchemaError("mode_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "tnl tnl_score",
    }


def tnl_budget(*, mode_specific: bool) -> dict[str, Any]:
    """Flag mode-specific rank budget (report-only)."""
    return {
        "mode_specific": mode_specific,
        "apply": False,
        "ok": True,
        "note": "tnl tnl_budget",
    }


def tnl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Stack → tucker → mode → score."""
    order = ("stack", "tucker", "mode", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "stack"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tnl tnl_loop_plan",
    }
