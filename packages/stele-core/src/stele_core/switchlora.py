"""SwitchLoRA proxies (stdlib; no LLM).

Shaped by SwitchLoRA (arXiv:2406.06564): frequently replace LoRA
trainable dimensions to approximate full-rank pre-training with
low optimizer-state disruption. Proxies only.

Prefix ``swl_*`` — not Chain of LoRA (``col_*``) / ReLoRA / Delta-LoRA
(``dlo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def swl_alloc(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate switched LoRA adapters (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "alloc_id": aid,
        "rank": rank,
        "ok": True,
        "note": "swl swl_alloc",
    }


def swl_switch(*, alloc_id: str, dims: int) -> dict[str, Any]:
    """Switch a few trainable dimensions (dims >= 1)."""
    aid = alloc_id.strip()
    if not aid:
        raise SchemaError("alloc_id required")
    if dims < 1:
        raise SchemaError("dims must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "d": dims}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "switch_id": sid,
        "dims": dims,
        "ok": True,
        "note": "swl swl_switch",
    }


def swl_train(*, switch_id: str) -> dict[str, Any]:
    """Continue training after subspace switch."""
    sid = switch_id.strip()
    if not sid:
        raise SchemaError("switch_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "swl swl_train",
    }


def swl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score SwitchLoRA adaptation (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "swl swl_score",
    }


def swl_full(*, mimics_fullrank: bool) -> dict[str, Any]:
    """Flag full-rank mimicry via frequent switches (report-only)."""
    return {
        "mimics_fullrank": mimics_fullrank,
        "apply": False,
        "ok": True,
        "note": "swl swl_full",
    }


def swl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Alloc → switch → train → score."""
    order = ("alloc", "switch", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "alloc"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "swl swl_loop_plan",
    }
