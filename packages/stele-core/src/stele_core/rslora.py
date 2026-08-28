"""rsLoRA proxies (stdlib; no LLM).

Shaped by rsLoRA (arXiv:2312.03732): scale adapters by 1/√r instead of 1/r
so higher ranks stay stable (no gradient collapse). Proxies only.

Prefix ``rsl_*`` — not LoRA-GA (``lga_*``) / LoKr (``lkr_*``) / LoRA+.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rsl_rank(*, task: str, rank: int) -> dict[str, Any]:
    """Declare adapter rank for rank-stabilized scaling (rank >= 1)."""
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
        "note": "rsl rsl_rank",
    }


def rsl_scale(*, rank_id: str) -> dict[str, Any]:
    """Apply 1/√r scaling factor (vs classic 1/r)."""
    rid = rank_id.strip()
    if not rid:
        raise SchemaError("rank_id required")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "rsl rsl_scale",
    }


def rsl_train(*, scale_id: str) -> dict[str, Any]:
    """Train with rank-stabilized adapters."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "rsl rsl_train",
    }


def rsl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score rsLoRA adaptation (0–100)."""
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
        "note": "rsl rsl_score",
    }


def rsl_stable(*, no_collapse: bool) -> dict[str, Any]:
    """Flag no gradient collapse at higher ranks (report-only)."""
    return {
        "no_collapse": no_collapse,
        "apply": False,
        "ok": True,
        "note": "rsl rsl_stable",
    }


def rsl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Rank → scale → train → score."""
    order = ("rank", "scale", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "rank"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rsl rsl_loop_plan",
    }
