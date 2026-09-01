"""FlyLoRA proxies (stdlib; no LLM).

Shaped by FlyLoRA (arXiv:2510.08396): implicit rank-wise MoE — frozen
sparse random A as router, top-k rank-1 experts on B. Proxies only.

Prefix ``fly_*`` — not FLoRA (``flo_*``) / NOLA (``nla_*``) / MixLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def fly_proj(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate frozen sparse random projection (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proj_id": pid,
        "rank": rank,
        "ok": True,
        "note": "fly fly_proj",
    }


def fly_topk(*, proj_id: str, k: int) -> dict[str, Any]:
    """Activate top-k rank-1 experts (k >= 1)."""
    pid = proj_id.strip()
    if not pid:
        raise SchemaError("proj_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"p": pid, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "topk_id": tid,
        "k": k,
        "ok": True,
        "note": "fly fly_topk",
    }


def fly_train(*, topk_id: str) -> dict[str, Any]:
    """Train FlyLoRA B experts."""
    tid = topk_id.strip()
    if not tid:
        raise SchemaError("topk_id required")
    rid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": rid,
        "ok": True,
        "note": "fly fly_train",
    }


def fly_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score FlyLoRA run (0–100)."""
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
        "note": "fly fly_score",
    }


def fly_implicit(*, implicit_router: bool) -> dict[str, Any]:
    """Flag implicit frozen router (report-only)."""
    return {
        "implicit_router": implicit_router,
        "apply": False,
        "ok": True,
        "note": "fly fly_implicit",
    }


def fly_loop_plan(*, phase: str) -> dict[str, Any]:
    """Proj → topk → train → score."""
    order = ("proj", "topk", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "proj"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "fly fly_loop_plan",
    }
