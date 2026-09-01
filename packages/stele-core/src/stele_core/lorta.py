"""LoRTA proxies (stdlib; no LLM).

Shaped by LoRTA (arXiv:2410.04060): 5th-order CP tensor shares
updates across layers, heads, and matrices. Proxies only.

Prefix ``lrt_*`` — not LoRA (``lra_*``) / LoRA-TSD (``tsd_*``) /
C-LoRA (``clo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lrt_tensor(*, task: str, order: int) -> dict[str, Any]:
    """Open a unified update tensor (order >= 3)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if order < 3:
        raise SchemaError("order must be >= 3")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "o": order}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tensor_id": tid,
        "order": order,
        "ok": True,
        "note": "lrt lrt_tensor",
    }


def lrt_cp(*, tensor_id: str, rank: int) -> dict[str, Any]:
    """CP-decompose the tensor (rank >= 1)."""
    tid = tensor_id.strip()
    if not tid:
        raise SchemaError("tensor_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"t": tid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cp_id": cid,
        "rank": rank,
        "ok": True,
        "note": "lrt lrt_cp",
    }


def lrt_share(*, cp_id: str) -> dict[str, Any]:
    """Share factors across layers/heads/matrices."""
    cid = cp_id.strip()
    if not cid:
        raise SchemaError("cp_id required")
    sid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": sid,
        "ok": True,
        "note": "lrt lrt_share",
    }


def lrt_score(*, share_id: str, score: int) -> dict[str, Any]:
    """Score LoRTA run (0–100)."""
    sid = share_id.strip()
    if not sid:
        raise SchemaError("share_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"h": sid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "lrt lrt_score",
    }


def lrt_compact(*, fewer_params: bool) -> dict[str, Any]:
    """Flag 10–100× fewer params vs LoRA (report-only)."""
    return {
        "fewer_params": fewer_params,
        "apply": False,
        "ok": True,
        "note": "lrt lrt_compact",
    }


def lrt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tensor → cp → share → score."""
    order = ("tensor", "cp", "share", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tensor"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lrt lrt_loop_plan",
    }
