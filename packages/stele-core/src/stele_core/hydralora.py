"""HydraLoRA proxies (stdlib; no LLM).

Shaped by HydraLoRA (arXiv:2404.19245 · NeurIPS 2024): asymmetric
shared-A + multi-B LoRA with MoE routing — no domain expertise needed
at train/inference. Proxies only.

Prefix ``hyd_*`` — not AsymmetryLoRA (``asy_*``) / LoRA-LEGO (``llg_*``) /
LoRAMoE.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hyd_share(*, task: str) -> dict[str, Any]:
    """Declare shared A matrix for Hydra asymmetric LoRA."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": sid,
        "ok": True,
        "note": "hyd hyd_share",
    }


def hyd_heads(*, share_id: str, heads: int) -> dict[str, Any]:
    """Allocate multiple B heads (heads >= 2)."""
    sid = share_id.strip()
    if not sid:
        raise SchemaError("share_id required")
    if heads < 2:
        raise SchemaError("heads must be >= 2")
    hid = hashlib.sha256(
        canonical_dumps({"s": sid, "h": heads}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "heads_id": hid,
        "heads": heads,
        "ok": True,
        "note": "hyd hyd_heads",
    }


def hyd_route(*, heads_id: str) -> dict[str, Any]:
    """MoE-style route across B heads at train/infer."""
    hid = heads_id.strip()
    if not hid:
        raise SchemaError("heads_id required")
    rid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "route_id": rid,
        "ok": True,
        "note": "hyd hyd_route",
    }


def hyd_score(*, route_id: str, score: int) -> dict[str, Any]:
    """Score HydraLoRA adaptation (0–100)."""
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
        "note": "hyd hyd_score",
    }


def hyd_nodomain(*, no_domain_labels: bool) -> dict[str, Any]:
    """Flag no domain expertise required (report-only)."""
    return {
        "no_domain_labels": no_domain_labels,
        "apply": False,
        "ok": True,
        "note": "hyd hyd_nodomain",
    }


def hyd_loop_plan(*, phase: str) -> dict[str, Any]:
    """Share → heads → route → score."""
    order = ("share", "heads", "route", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "share"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hyd hyd_loop_plan",
    }
