"""LoRA-FA proxies (stdlib; no LLM).

Shaped by LoRA-FA (arXiv:2308.03303): freeze randomly initialized A;
train only B — lower activation memory, comparable quality. Proxies only.

Prefix ``lfa_*`` — not DyLoRA (``dyl_*``) / LoRA+ (``lrp_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lfa_freeze_a(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate frozen random A for a task (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "a_id": aid,
        "rank": rank,
        "ok": True,
        "note": "lfa lfa_freeze_a",
    }


def lfa_train_b(*, a_id: str) -> dict[str, Any]:
    """Train only the up-projection B; keep A frozen."""
    aid = a_id.strip()
    if not aid:
        raise SchemaError("a_id required")
    bid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": bid,
        "ok": True,
        "note": "lfa lfa_train_b",
    }


def lfa_merge(*, train_id: str) -> dict[str, Any]:
    """Merge BA into W for zero-extra-latency inference."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    mid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "ok": True,
        "note": "lfa lfa_merge",
    }


def lfa_score(*, merge_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-FA adaptation (0–100)."""
    mid = merge_id.strip()
    if not mid:
        raise SchemaError("merge_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lfa lfa_score",
    }


def lfa_memory(*, activation_saved: bool) -> dict[str, Any]:
    """Flag activation-memory savings from freezing A (report-only)."""
    return {
        "activation_saved": activation_saved,
        "apply": False,
        "ok": True,
        "note": "lfa lfa_memory",
    }


def lfa_loop_plan(*, phase: str) -> dict[str, Any]:
    """Freeze_a → train_b → merge → score."""
    order = ("freeze_a", "train_b", "merge", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "freeze_a"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lfa lfa_loop_plan",
    }
