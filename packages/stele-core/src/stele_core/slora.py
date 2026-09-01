"""S-LoRA proxies (stdlib; no LLM).

Shaped by S-LoRA (arXiv:2311.03285): scalable serving of thousands of
concurrent LoRA adapters via host-memory store, Unified Paging for
adapters+KV, and heterogeneous batched compute. Proxies only.

Prefix ``slr_*`` — not rsLoRA (``rsl_*``) / LoRA-TSD (``lts_*``) /
MoSLoRA (``mos_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def slr_pool(*, adapters: int) -> dict[str, Any]:
    """Declare host-memory adapter pool (adapters >= 1)."""
    if adapters < 1:
        raise SchemaError("adapters must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"a": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pool_id": pid,
        "adapters": adapters,
        "ok": True,
        "note": "slr slr_pool",
    }


def slr_page(*, pool_id: str, unified: bool) -> dict[str, Any]:
    """Enable Unified Paging over adapters + KV cache."""
    pid = pool_id.strip()
    if not pid:
        raise SchemaError("pool_id required")
    xid = hashlib.sha256(
        canonical_dumps({"p": pid, "u": unified}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "page_id": xid,
        "unified": unified,
        "ok": True,
        "note": "slr slr_page",
    }


def slr_batch(*, page_id: str, concurrent: int) -> dict[str, Any]:
    """Heterogeneous batch of concurrent adapters (concurrent >= 1)."""
    xid = page_id.strip()
    if not xid:
        raise SchemaError("page_id required")
    if concurrent < 1:
        raise SchemaError("concurrent must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"p": xid, "c": concurrent}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "batch_id": bid,
        "concurrent": concurrent,
        "ok": True,
        "note": "slr slr_batch",
    }


def slr_score(*, batch_id: str, score: int) -> dict[str, Any]:
    """Score S-LoRA serving throughput proxy (0–100)."""
    bid = batch_id.strip()
    if not bid:
        raise SchemaError("batch_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"b": bid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "slr slr_score",
    }


def slr_scale(*, thousands: bool) -> dict[str, Any]:
    """Flag thousands-of-adapters serving scale (report-only)."""
    return {
        "thousands": thousands,
        "apply": False,
        "ok": True,
        "note": "slr slr_scale",
    }


def slr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pool → page → batch → score."""
    order = ("pool", "page", "batch", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pool"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "slr slr_loop_plan",
    }
