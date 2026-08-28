"""LoRA proxies (stdlib; no LLM).

Shaped by LoRA (arXiv:2106.09685): freeze W0; train low-rank ΔW=BA;
merge at inference with no added latency. Proxies only.

Prefix ``lora_*`` — not AdapterFusion (``adf_*``) / Multitask Prompt Tuning.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lora_freeze(*, base_frozen: bool) -> dict[str, Any]:
    """Flag frozen pretrained weights W0 (report-only)."""
    return {
        "base_frozen": base_frozen,
        "apply": False,
        "ok": True,
        "note": "lora lora_freeze",
    }


def lora_rank(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate low-rank factors B,A with given rank r (>=1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rank_id": rid,
        "rank": rank,
        "ok": True,
        "note": "lora lora_rank",
    }


def lora_train(*, rank_id: str) -> dict[str, Any]:
    """Train only the low-rank adapters for the task."""
    rid = rank_id.strip()
    if not rid:
        raise SchemaError("rank_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lora lora_train",
    }


def lora_merge(*, train_id: str, score: int) -> dict[str, Any]:
    """Merge BA into W0 for zero-extra-latency inference (score 0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    mid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "score": score,
        "ok": True,
        "note": "lora lora_merge",
    }


def lora_latency(*, zero_extra: bool) -> dict[str, Any]:
    """Flag no added inference latency after merge (report-only)."""
    return {
        "zero_extra": zero_extra,
        "apply": False,
        "ok": True,
        "note": "lora lora_latency",
    }


def lora_loop_plan(*, phase: str) -> dict[str, Any]:
    """Freeze → rank → train → merge."""
    order = ("freeze", "rank", "train", "merge")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "freeze"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lora lora_loop_plan",
    }
