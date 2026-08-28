"""MixLoRA proxies (stdlib; no LLM).

Shaped by MixLoRA (arXiv:2404.15159): LoRA-based sparse MoE in FFN
plus independent attention LoRAs and a load-balance loss. Proxies only.

Prefix ``mxl_*`` — not MultiLoRA (``mlr_*``) / Mixtral / FlyLoRA (``fly_*``)
/ SuperLoRA (``spr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mxl_experts(*, task: str, n_experts: int) -> dict[str, Any]:
    """Place LoRA experts in FFN (n_experts >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_experts < 2:
        raise SchemaError("n_experts must be >= 2")
    eid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_experts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experts_id": eid,
        "n_experts": n_experts,
        "ok": True,
        "note": "mxl mxl_experts",
    }


def mxl_route(*, experts_id: str, k: int) -> dict[str, Any]:
    """Top-k router over LoRA experts (k >= 1)."""
    eid = experts_id.strip()
    if not eid:
        raise SchemaError("experts_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"e": eid, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "route_id": rid,
        "k": k,
        "ok": True,
        "note": "mxl mxl_route",
    }


def mxl_attn(*, route_id: str) -> dict[str, Any]:
    """Attach independent attention-layer LoRAs."""
    rid = route_id.strip()
    if not rid:
        raise SchemaError("route_id required")
    aid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "attn_id": aid,
        "ok": True,
        "note": "mxl mxl_attn",
    }


def mxl_score(*, attn_id: str, score: int) -> dict[str, Any]:
    """Score MixLoRA run (0–100)."""
    aid = attn_id.strip()
    if not aid:
        raise SchemaError("attn_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mxl mxl_score",
    }


def mxl_balance(*, load_balance: bool) -> dict[str, Any]:
    """Flag auxiliary load-balance loss (report-only)."""
    return {
        "load_balance": load_balance,
        "apply": False,
        "ok": True,
        "note": "mxl mxl_balance",
    }


def mxl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Experts → route → attn → score."""
    order = ("experts", "route", "attn", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "experts"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mxl mxl_loop_plan",
    }
