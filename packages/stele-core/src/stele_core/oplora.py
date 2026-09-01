"""OPLoRA proxies — Orthogonal Projection LoRA (stdlib; no LLM).

Shaped by OPLoRA (arXiv:2510.13003): double-sided orthogonal projections
so LoRA updates stay orthogonal to pretrained subspaces and reduce
catastrophic forgetting. Proxies only.

Prefix ``opl_*`` — not OLoRA (``olr_*``) / GeLoRA (``gel_*``) / alternating-update OPLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def opl_proj(*, task: str) -> dict[str, Any]:
    """Declare orthogonal projection bases for pretrained subspaces."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    pid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proj_id": pid,
        "ok": True,
        "note": "opl opl_proj",
    }


def opl_constrain(*, proj_id: str, rank: int) -> dict[str, Any]:
    """Constrain LoRA updates to the orthogonal complement (rank >= 1)."""
    pid = proj_id.strip()
    if not pid:
        raise SchemaError("proj_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"p": pid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "constrain_id": cid,
        "rank": rank,
        "ok": True,
        "note": "opl opl_constrain",
    }


def opl_train(*, constrain_id: str) -> dict[str, Any]:
    """Train under orthogonal-projection constraint."""
    cid = constrain_id.strip()
    if not cid:
        raise SchemaError("constrain_id required")
    tid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "opl opl_train",
    }


def opl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score OPLoRA adaptation (0–100)."""
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
        "note": "opl opl_score",
    }


def opl_forget(*, less_forgetting: bool) -> dict[str, Any]:
    """Flag less catastrophic forgetting (report-only)."""
    return {
        "less_forgetting": less_forgetting,
        "apply": False,
        "ok": True,
        "note": "opl opl_forget",
    }


def opl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Proj → constrain → train → score."""
    order = ("proj", "constrain", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "proj"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "opl opl_loop_plan",
    }
