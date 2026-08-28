"""LoRA-One proxies (stdlib; no LLM).

Shaped by LoRA-One (arXiv:2502.01235): initialize adapters from the
one-step full fine-tuning gradient so they align with optimal singular
subspaces immediately. Proxies only.

Prefix ``lon_*`` — not LoRA-GA (``lga_*``) / LoRA-Pro (``lpr_*``) / Delta-LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lon_grad(*, task: str) -> dict[str, Any]:
    """Declare one-step full fine-tuning gradient."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    gid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "grad_id": gid,
        "ok": True,
        "note": "lon lon_grad",
    }


def lon_align(*, grad_id: str, rank: int) -> dict[str, Any]:
    """Init A/B aligned to singular subspaces of one-step gradient."""
    gid = grad_id.strip()
    if not gid:
        raise SchemaError("grad_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"g": gid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "align_id": aid,
        "rank": rank,
        "ok": True,
        "note": "lon lon_align",
    }


def lon_train(*, align_id: str) -> dict[str, Any]:
    """Train from LoRA-One initialization."""
    aid = align_id.strip()
    if not aid:
        raise SchemaError("align_id required")
    tid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lon lon_train",
    }


def lon_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-One adaptation (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lon lon_score",
    }


def lon_immediate(*, immediate_align: bool) -> dict[str, Any]:
    """Flag immediate subspace alignment (report-only)."""
    return {
        "immediate_align": immediate_align,
        "apply": False,
        "ok": True,
        "note": "lon lon_immediate",
    }


def lon_loop_plan(*, phase: str) -> dict[str, Any]:
    """Grad → align → train → score."""
    order = ("grad", "align", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "grad"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lon lon_loop_plan",
    }
