"""MiSS proxies (stdlib; no LLM).

Shaped by MiSS (arXiv:2409.15371): update weight shards via a single shared
trainable matrix D (zero-init) instead of dual BA — lower optimization
complexity / better perf–memory–efficiency trade-off. Proxies only.

Prefix ``mss_*`` — not Soft Prompt Mixtures (``msp_*``) / OFT (``oft_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mss_shard(*, task: str, shards: int) -> dict[str, Any]:
    """Declare weight shards to update (shards >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if shards < 1:
        raise SchemaError("shards must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "n": shards}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "shard_id": sid,
        "shards": shards,
        "ok": True,
        "note": "mss mss_shard",
    }


def mss_share(*, shard_id: str) -> dict[str, Any]:
    """Allocate shared trainable matrix D across shards."""
    sid = shard_id.strip()
    if not sid:
        raise SchemaError("shard_id required")
    did = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": did,
        "ok": True,
        "note": "mss mss_share",
    }


def mss_train(*, share_id: str) -> dict[str, Any]:
    """Train shared D only (zero-init)."""
    did = share_id.strip()
    if not did:
        raise SchemaError("share_id required")
    tid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "mss mss_train",
    }


def mss_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score MiSS adaptation (0–100)."""
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
        "note": "mss mss_score",
    }


def mss_pareto(*, better_tradeoff: bool) -> dict[str, Any]:
    """Flag favorable Pareto trade-off vs LoRA variants (report-only)."""
    return {
        "better_tradeoff": better_tradeoff,
        "apply": False,
        "ok": True,
        "note": "mss mss_pareto",
    }


def mss_loop_plan(*, phase: str) -> dict[str, Any]:
    """Shard → share → train → score."""
    order = ("shard", "share", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "shard"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mss mss_loop_plan",
    }
