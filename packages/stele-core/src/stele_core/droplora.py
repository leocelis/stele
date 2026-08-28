"""DropLoRA proxies (stdlib; no LLM).

Shaped by DropLoRA (arXiv:2508.17337): stochastic Bernoulli prune on the
rank dimension between A and B — dynamic subspace learning without extra
inference cost. Proxies only.

Prefix ``drl_*`` — not DoRA (``dora-*``) / DyLoRA (``dyl_*``) / dormant-scan.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def drl_rank(*, task: str, rank: int) -> dict[str, Any]:
    """Declare LoRA rank for DropLoRA (rank >= 1)."""
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
        "note": "drl drl_rank",
    }


def drl_mask(*, rank_id: str, keep_prob: int) -> dict[str, Any]:
    """Sample Bernoulli prune mask on rank dim (keep_prob 1–100)."""
    rid = rank_id.strip()
    if not rid:
        raise SchemaError("rank_id required")
    if keep_prob < 1 or keep_prob > 100:
        raise SchemaError("keep_prob must be 1..100")
    mid = hashlib.sha256(
        canonical_dumps({"r": rid, "p": keep_prob}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mask_id": mid,
        "keep_prob": keep_prob,
        "ok": True,
        "note": "drl drl_mask",
    }


def drl_train(*, mask_id: str) -> dict[str, Any]:
    """Train with dynamic subspace (B⊙M)(M⊙A)."""
    mid = mask_id.strip()
    if not mid:
        raise SchemaError("mask_id required")
    tid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "drl drl_train",
    }


def drl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score DropLoRA adaptation (0–100)."""
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
        "note": "drl drl_score",
    }


def drl_infer(*, no_extra_cost: bool) -> dict[str, Any]:
    """Flag no added inference cost vs LoRA (report-only)."""
    return {
        "no_extra_cost": no_extra_cost,
        "apply": False,
        "ok": True,
        "note": "drl drl_infer",
    }


def drl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Rank → mask → train → score."""
    order = ("rank", "mask", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "rank"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "drl drl_loop_plan",
    }
