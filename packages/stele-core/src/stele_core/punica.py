"""Punica proxies (stdlib; no LLM).

Shaped by Punica (arXiv:2310.18547): multi-tenant LoRA serving on a
shared backbone via SGMV batching — one pretrained copy, many adapters.
Proxies only.

Prefix ``pun_*`` — not S-LoRA (``slr_*``) / Compress-then-Serve (``cts_*``)
/ mLoRA (``mla_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pun_backbone(*, model: str) -> dict[str, Any]:
    """Declare shared pretrained backbone for multi-tenant serving."""
    m = model.strip()
    if not m:
        raise SchemaError("model required")
    bid = hashlib.sha256(
        canonical_dumps({"m": m}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "backbone_id": bid,
        "ok": True,
        "note": "pun pun_backbone",
    }


def pun_sgmv(*, backbone_id: str, adapters: int) -> dict[str, Any]:
    """SGMV-batched LoRA compute (adapters >= 1)."""
    bid = backbone_id.strip()
    if not bid:
        raise SchemaError("backbone_id required")
    if adapters < 1:
        raise SchemaError("adapters must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"b": bid, "a": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sgmv_id": sid,
        "adapters": adapters,
        "ok": True,
        "note": "pun pun_sgmv",
    }


def pun_sched(*, sgmv_id: str) -> dict[str, Any]:
    """Consolidate multi-tenant LoRA workloads on the cluster."""
    sid = sgmv_id.strip()
    if not sid:
        raise SchemaError("sgmv_id required")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sched_id": xid,
        "ok": True,
        "note": "pun pun_sched",
    }


def pun_score(*, sched_id: str, score: int) -> dict[str, Any]:
    """Score Punica serving throughput proxy (0–100)."""
    sid = sched_id.strip()
    if not sid:
        raise SchemaError("sched_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid, "x": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "pun pun_score",
    }


def pun_multi(*, multi_tenant: bool) -> dict[str, Any]:
    """Flag multi-tenant shared-backbone mode (report-only)."""
    return {
        "multi_tenant": multi_tenant,
        "apply": False,
        "ok": True,
        "note": "pun pun_multi",
    }


def pun_loop_plan(*, phase: str) -> dict[str, Any]:
    """Backbone → sgmv → sched → score."""
    order = ("backbone", "sgmv", "sched", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "backbone"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pun pun_loop_plan",
    }
