"""LoRAMoE proxies (stdlib; no LLM).

Shaped by LoRAMoE (arXiv:2312.09979 · ACL 2024): MoE-style LoRA
plugin with localized balancing — freeze backbone, route experts so
some preserve world knowledge while others serve tasks. Proxies only.

Prefix ``lme_*`` — not MoELoRA (``mel_*``) / HydraLoRA (``hyd_*``) /
MiLoRA (``mil_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lme_plugin(*, task: str, experts: int) -> dict[str, Any]:
    """Declare MoE-style LoRA plugin (experts >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if experts < 2:
        raise SchemaError("experts must be >= 2")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "e": experts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plugin_id": pid,
        "experts": experts,
        "ok": True,
        "note": "lme lme_plugin",
    }


def lme_balance(*, plugin_id: str) -> dict[str, Any]:
    """Apply localized balancing across expert groups."""
    pid = plugin_id.strip()
    if not pid:
        raise SchemaError("plugin_id required")
    bid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "balance_id": bid,
        "ok": True,
        "note": "lme lme_balance",
    }


def lme_route(*, balance_id: str) -> dict[str, Any]:
    """Route tokens across knowledge vs task experts."""
    bid = balance_id.strip()
    if not bid:
        raise SchemaError("balance_id required")
    rid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "route_id": rid,
        "ok": True,
        "note": "lme lme_route",
    }


def lme_score(*, route_id: str, score: int) -> dict[str, Any]:
    """Score LoRAMoE adaptation (0–100)."""
    rid = route_id.strip()
    if not rid:
        raise SchemaError("route_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lme lme_score",
    }


def lme_forget(*, preserves_world: bool) -> dict[str, Any]:
    """Flag world-knowledge preservation under SFT scale-up (report-only)."""
    return {
        "preserves_world": preserves_world,
        "apply": False,
        "ok": True,
        "note": "lme lme_forget",
    }


def lme_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plugin → balance → route → score."""
    order = ("plugin", "balance", "route", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plugin"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lme lme_loop_plan",
    }
