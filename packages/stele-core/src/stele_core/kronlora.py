"""Kron-LoRA proxies (stdlib; no LLM).

Shaped by Kron-LoRA (arXiv:2508.01961): hybrid two-stage adapter —
Kronecker factors plus LoRA low-rank update for multiplicative
compression vs plain LoRA. Proxies only.

Prefix ``krl_*`` — not LoKr (``lkr_*``) / LoRA-Pro (``lpr_*``) / MoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def krl_kron(*, task: str, factor: int) -> dict[str, Any]:
    """Declare Kronecker stage factors (factor >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if factor < 1:
        raise SchemaError("factor must be >= 1")
    kid = hashlib.sha256(
        canonical_dumps({"t": t, "f": factor}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "kron_id": kid,
        "factor": factor,
        "ok": True,
        "note": "krl krl_kron",
    }


def krl_lora(*, kron_id: str, rank: int) -> dict[str, Any]:
    """Attach LoRA stage on top of Kronecker (rank >= 1)."""
    kid = kron_id.strip()
    if not kid:
        raise SchemaError("kron_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    lid = hashlib.sha256(
        canonical_dumps({"k": kid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "lora_id": lid,
        "rank": rank,
        "ok": True,
        "note": "krl krl_lora",
    }


def krl_train(*, lora_id: str) -> dict[str, Any]:
    """Train hybrid Kronecker–LoRA adapter."""
    lid = lora_id.strip()
    if not lid:
        raise SchemaError("lora_id required")
    tid = hashlib.sha256(
        canonical_dumps({"l": lid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "krl krl_train",
    }


def krl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score Kron-LoRA adaptation (0–100)."""
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
        "note": "krl krl_score",
    }


def krl_compress(*, more_compression: bool) -> dict[str, Any]:
    """Flag multiplicative param compression vs LoRA (report-only)."""
    return {
        "more_compression": more_compression,
        "apply": False,
        "ok": True,
        "note": "krl krl_compress",
    }


def krl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Kron → lora → train → score."""
    order = ("kron", "lora", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "kron"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "krl krl_loop_plan",
    }
