"""Q-GaLore proxies (stdlib; no LLM).

Shaped by Q-GaLore (arXiv:2407.08296): INT8 weights + INT4 gradient
projections with layer-adaptive (lazy) SVD. Proxies only.

Prefix ``qga_*`` — not GaLore (``gal_*``) / QLoRA (``qlo_*``) /
LoRA-Flow (``lfw_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qga_weight(*, task: str) -> dict[str, Any]:
    """Hold weights in INT8 with stochastic rounding."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    wid = hashlib.sha256(
        canonical_dumps({"t": t, "w": "int8"}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "weight_id": wid,
        "ok": True,
        "note": "qga qga_weight",
    }


def qga_proj(*, weight_id: str, rank: int) -> dict[str, Any]:
    """INT4 low-rank gradient projection (rank >= 1)."""
    wid = weight_id.strip()
    if not wid:
        raise SchemaError("weight_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"w": wid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proj_id": pid,
        "rank": rank,
        "ok": True,
        "note": "qga qga_proj",
    }


def qga_lazy(*, proj_id: str) -> dict[str, Any]:
    """Layer-adaptive / lazy SVD subspace refresh."""
    pid = proj_id.strip()
    if not pid:
        raise SchemaError("proj_id required")
    lid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "lazy_id": lid,
        "ok": True,
        "note": "qga qga_lazy",
    }


def qga_score(*, lazy_id: str, score: int) -> dict[str, Any]:
    """Score Q-GaLore run (0–100)."""
    lid = lazy_id.strip()
    if not lid:
        raise SchemaError("lazy_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"l": lid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "qga qga_score",
    }


def qga_mem(*, consumer_gpu: bool) -> dict[str, Any]:
    """Flag 16GB-class GPU pretrain path (report-only)."""
    return {
        "consumer_gpu": consumer_gpu,
        "apply": False,
        "ok": True,
        "note": "qga qga_mem",
    }


def qga_loop_plan(*, phase: str) -> dict[str, Any]:
    """Weight → proj → lazy → score."""
    order = ("weight", "proj", "lazy", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "weight"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qga qga_loop_plan",
    }
