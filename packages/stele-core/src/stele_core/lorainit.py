"""LoRA-Init proxies (stdlib; no LLM).

Shaped by LoRA-Init in *Task-Specific Directions…* (arXiv:2409.01035):
initialize adapters from TSDs that need the most adjustment for the
downstream task (complements LoRA-Dash). Proxies only.

Prefix ``lin_*`` — not LoRA-Dash (``lds_*``) / LoRA-Null (``lnu_*``) /
LoRA-One (``lon_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lin_tsd(*, task: str, count: int) -> dict[str, Any]:
    """Identify task-specific directions for init (count >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if count < 1:
        raise SchemaError("count must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tsd_id": tid,
        "count": count,
        "ok": True,
        "note": "lin lin_tsd",
    }


def lin_init(*, tsd_id: str) -> dict[str, Any]:
    """Initialize LoRA matrices from selected TSDs."""
    tid = tsd_id.strip()
    if not tid:
        raise SchemaError("tsd_id required")
    iid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "ok": True,
        "note": "lin lin_init",
    }


def lin_train(*, init_id: str) -> dict[str, Any]:
    """Train after TSD-based initialization."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lin lin_train",
    }


def lin_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Init adaptation (0–100)."""
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
        "note": "lin lin_score",
    }


def lin_fast(*, faster_convergence: bool) -> dict[str, Any]:
    """Flag faster convergence vs random init (report-only)."""
    return {
        "faster_convergence": faster_convergence,
        "apply": False,
        "ok": True,
        "note": "lin lin_fast",
    }


def lin_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tsd → init → train → score."""
    order = ("tsd", "init", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tsd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lin lin_loop_plan",
    }
