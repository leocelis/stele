"""OLoRA proxies (stdlib; no LLM).

Shaped by OLoRA (arXiv:2406.01775): QR orthonormal init so adapters
approximate final W with a more stable optimization landscape. Proxies only.

Prefix ``olr_*`` — not LoRA (``lora_*``) / LoRA-One (``lon_*``) / LoRA-SP.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def olr_qr(*, task: str, rank: int) -> dict[str, Any]:
    """Declare QR orthonormal init for adapters (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    qid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "qr_id": qid,
        "rank": rank,
        "ok": True,
        "note": "olr olr_qr",
    }


def olr_ortho(*, qr_id: str) -> dict[str, Any]:
    """Lock orthonormal columns for adaptation matrices."""
    qid = qr_id.strip()
    if not qid:
        raise SchemaError("qr_id required")
    oid = hashlib.sha256(
        canonical_dumps({"q": qid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ortho_id": oid,
        "ok": True,
        "note": "olr olr_ortho",
    }


def olr_train(*, ortho_id: str) -> dict[str, Any]:
    """Train from OLoRA orthonormal initialization."""
    oid = ortho_id.strip()
    if not oid:
        raise SchemaError("ortho_id required")
    tid = hashlib.sha256(
        canonical_dumps({"o": oid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "olr olr_train",
    }


def olr_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score OLoRA adaptation (0–100)."""
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
        "note": "olr olr_score",
    }


def olr_stable(*, stable_landscape: bool) -> dict[str, Any]:
    """Flag more stable optimization landscape (report-only)."""
    return {
        "stable_landscape": stable_landscape,
        "apply": False,
        "ok": True,
        "note": "olr olr_stable",
    }


def olr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Qr → ortho → train → score."""
    order = ("qr", "ortho", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "qr"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "olr olr_loop_plan",
    }
