"""VeRA proxies (stdlib; no LLM).

Shaped by VeRA (arXiv:2310.11454): share frozen random low-rank matrices
across layers; train only tiny per-layer scaling vectors. Proxies only.

Prefix ``vra_*`` — not AdapterDrop (``adp_*``) / LoRA (``lora_*``) / versioning.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def vra_share(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate shared frozen random A,B matrices (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": sid,
        "rank": rank,
        "ok": True,
        "note": "vra vra_share",
    }


def vra_scale(*, share_id: str) -> dict[str, Any]:
    """Train per-layer scaling vectors on frozen shared matrices."""
    sid = share_id.strip()
    if not sid:
        raise SchemaError("share_id required")
    vid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": vid,
        "ok": True,
        "note": "vra vra_scale",
    }


def vra_train(*, scale_id: str) -> dict[str, Any]:
    """Train only the scaling vectors; freeze shared random matrices."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "vra vra_train",
    }


def vra_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score VeRA adaptation (0–100)."""
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
        "note": "vra vra_score",
    }


def vra_tiny(*, vector_only: bool) -> dict[str, Any]:
    """Flag vector-only trainable footprint (report-only)."""
    return {
        "vector_only": vector_only,
        "apply": False,
        "ok": True,
        "note": "vra vra_tiny",
    }


def vra_loop_plan(*, phase: str) -> dict[str, Any]:
    """Share → scale → train → score."""
    order = ("share", "scale", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "share"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "vra vra_loop_plan",
    }
