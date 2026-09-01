"""FLoRA proxies (stdlib; no LLM).

Shaped by FLoRA (arXiv:2409.05976): federated fine-tuning with
heterogeneous LoRA adapters via stacking-based aggregation (noise-free,
rank-heterogeneous clients). Proxies only.

Prefix ``flo_*`` — not FLoRA-as-LoRA+ / Compress-then-Serve (``cts_*``) /
LoRA+ (``lrp_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def flo_clients(*, clients: int) -> dict[str, Any]:
    """Declare federated client set (clients >= 1)."""
    if clients < 1:
        raise SchemaError("clients must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"c": clients}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "clients_id": cid,
        "clients": clients,
        "ok": True,
        "note": "flo flo_clients",
    }


def flo_stack(*, clients_id: str, hetero_ranks: bool) -> dict[str, Any]:
    """Stack local A/B adapters (supports heterogeneous ranks)."""
    cid = clients_id.strip()
    if not cid:
        raise SchemaError("clients_id required")
    sid = hashlib.sha256(
        canonical_dumps({"c": cid, "h": hetero_ranks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "stack_id": sid,
        "hetero_ranks": hetero_ranks,
        "ok": True,
        "note": "flo flo_stack",
    }


def flo_agg(*, stack_id: str) -> dict[str, Any]:
    """Noise-free stacking aggregation to global A/B."""
    sid = stack_id.strip()
    if not sid:
        raise SchemaError("stack_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "agg_id": aid,
        "ok": True,
        "note": "flo flo_agg",
    }


def flo_score(*, agg_id: str, score: int) -> dict[str, Any]:
    """Score FLoRA federated adaptation (0–100)."""
    aid = agg_id.strip()
    if not aid:
        raise SchemaError("agg_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "flo flo_score",
    }


def flo_hetero(*, supports_hetero: bool) -> dict[str, Any]:
    """Flag heterogeneous-rank client support (report-only)."""
    return {
        "supports_hetero": supports_hetero,
        "apply": False,
        "ok": True,
        "note": "flo flo_hetero",
    }


def flo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Clients → stack → agg → score."""
    order = ("clients", "stack", "agg", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "clients"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "flo flo_loop_plan",
    }
