"""CARE-LoRA proxies (stdlib; no LLM).

Shaped by CARE-LoRA (arXiv:2607.11940): Compressed Activation
REconstruction for memory-efficient LoRA — keep low-rank compressed
activations and reconstruct gradients for backprop, cutting activation
memory without full recomputation. Proxies only.

Prefix ``car_*`` — not LoRA-Composer (``lco_*``) / Compress-then-Serve
(``cts_*``) / LoRA-FA (``lfa_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def car_compress(*, task: str, keep_rank: int) -> dict[str, Any]:
    """Compress activations to keep_rank (>= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if keep_rank < 1:
        raise SchemaError("keep_rank must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"t": t, "k": keep_rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compress_id": cid,
        "keep_rank": keep_rank,
        "ok": True,
        "note": "car car_compress",
    }


def car_recon(*, compress_id: str) -> dict[str, Any]:
    """Reconstruct activation gradients from compressed state."""
    cid = compress_id.strip()
    if not cid:
        raise SchemaError("compress_id required")
    rid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "recon_id": rid,
        "ok": True,
        "note": "car car_recon",
    }


def car_train(*, recon_id: str) -> dict[str, Any]:
    """Train LoRA with CARE backprop path."""
    rid = recon_id.strip()
    if not rid:
        raise SchemaError("recon_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "car car_train",
    }


def car_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score CARE-LoRA run (0–100)."""
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
        "note": "car car_score",
    }


def car_mem(*, activation_saved: bool) -> dict[str, Any]:
    """Flag activation-memory savings (report-only)."""
    return {
        "activation_saved": activation_saved,
        "apply": False,
        "ok": True,
        "note": "car car_mem",
    }


def car_loop_plan(*, phase: str) -> dict[str, Any]:
    """Compress → recon → train → score."""
    order = ("compress", "recon", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "compress"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "car car_loop_plan",
    }
