"""LoRAFusion proxies (stdlib; no LLM).

Shaped by LoRAFusion (arXiv:2510.00206): fuse memory-bound LoRA
ops and bin-pack multi-job microbatches. Proxies only.

Prefix ``lfu_*`` — not Hybrid PEFT (``hyb_*``) / FlyLoRA (``fly_*``)
/ ConcurrentLoRA (``cnl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lfu_split(*, task: str) -> dict[str, Any]:
    """Split the LoRA graph for kernel fusion."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "split_id": sid,
        "ok": True,
        "note": "lfu lfu_split",
    }


def lfu_fuse(*, split_id: str) -> dict[str, Any]:
    """Fuse memory-bound LoRA ops."""
    sid = split_id.strip()
    if not sid:
        raise SchemaError("split_id required")
    fid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fuse_id": fid,
        "ok": True,
        "note": "lfu lfu_fuse",
    }


def lfu_batch(*, fuse_id: str, jobs: int) -> dict[str, Any]:
    """Bin-pack multi-job microbatches (jobs >= 1)."""
    fid = fuse_id.strip()
    if not fid:
        raise SchemaError("fuse_id required")
    if jobs < 1:
        raise SchemaError("jobs must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"f": fid, "j": jobs}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "batch_id": bid,
        "jobs": jobs,
        "ok": True,
        "note": "lfu lfu_batch",
    }


def lfu_score(*, batch_id: str, score: int) -> dict[str, Any]:
    """Score LoRAFusion run (0–100)."""
    bid = batch_id.strip()
    if not bid:
        raise SchemaError("batch_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"b": bid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "lfu lfu_score",
    }


def lfu_speed(*, faster_than_mlora: bool) -> dict[str, Any]:
    """Flag faster than mLoRA (report-only)."""
    return {
        "faster_than_mlora": faster_than_mlora,
        "apply": False,
        "ok": True,
        "note": "lfu lfu_speed",
    }


def lfu_loop_plan(*, phase: str) -> dict[str, Any]:
    """Split → fuse → batch → score."""
    order = ("split", "fuse", "batch", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "split"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lfu lfu_loop_plan",
    }
