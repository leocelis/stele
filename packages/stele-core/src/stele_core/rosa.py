"""RoSA proxies (stdlib; no LLM).

Shaped by RoSA (arXiv:2401.04679): joint low-rank + highly sparse
residual, RPCA-style, to close the FFT gap. Proxies only.

Prefix ``ros_*`` — not LoRA (``lora``) / ABBA (``abb_*``) / DoRA
(``dora_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ros_rank(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate the low-rank branch (rank >= 1)."""
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
        "note": "ros ros_rank",
    }


def ros_sparse(*, rank_id: str) -> dict[str, Any]:
    """Allocate the sparse residual branch."""
    rid = rank_id.strip()
    if not rid:
        raise SchemaError("rank_id required")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sparse_id": sid,
        "ok": True,
        "note": "ros ros_sparse",
    }


def ros_train(*, sparse_id: str) -> dict[str, Any]:
    """Train rank + sparse jointly."""
    sid = sparse_id.strip()
    if not sid:
        raise SchemaError("sparse_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "ros ros_train",
    }


def ros_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score RoSA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "ros ros_score",
    }


def ros_fft(*, matches_fft: bool) -> dict[str, Any]:
    """Flag FFT-level recovery on some tasks (report-only)."""
    return {
        "matches_fft": matches_fft,
        "apply": False,
        "ok": True,
        "note": "ros ros_fft",
    }


def ros_loop_plan(*, phase: str) -> dict[str, Any]:
    """Rank → sparse → train → score."""
    order = ("rank", "sparse", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "rank"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ros ros_loop_plan",
    }
