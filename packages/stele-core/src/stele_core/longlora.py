"""LongLoRA proxies (stdlib; no LLM).

Shaped by LongLoRA (arXiv:2309.12307): extend context with shifted
sparse attention (S2-Attn) during train, then LoRA on the long
window. Sparse train attention is optional at infer. Proxies only.

Prefix ``llr_*`` — not LoRA (``lra_*``) / LoRA-FA (``lfa_*``) /
HiRA (``hir_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def llr_window(*, task: str, ctx_len: int) -> dict[str, Any]:
    """Open a long-context window (ctx_len >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if ctx_len < 1:
        raise SchemaError("ctx_len must be >= 1")
    wid = hashlib.sha256(
        canonical_dumps({"t": t, "c": ctx_len}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "window_id": wid,
        "ctx_len": ctx_len,
        "ok": True,
        "note": "llr llr_window",
    }


def llr_shift(*, window_id: str) -> dict[str, Any]:
    """Apply shifted sparse attention (S2-Attn) for train."""
    wid = window_id.strip()
    if not wid:
        raise SchemaError("window_id required")
    sid = hashlib.sha256(
        canonical_dumps({"w": wid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "shift_id": sid,
        "ok": True,
        "note": "llr llr_shift",
    }


def llr_lora(*, shift_id: str, rank: int) -> dict[str, Any]:
    """LoRA-adapt the long-context window (rank >= 1)."""
    sid = shift_id.strip()
    if not sid:
        raise SchemaError("shift_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    lid = hashlib.sha256(
        canonical_dumps({"s": sid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "lora_id": lid,
        "rank": rank,
        "ok": True,
        "note": "llr llr_lora",
    }


def llr_score(*, lora_id: str, score: int) -> dict[str, Any]:
    """Score LongLoRA run (0–100)."""
    lid = lora_id.strip()
    if not lid:
        raise SchemaError("lora_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"l": lid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "llr llr_score",
    }


def llr_sparse(*, sparse_train: bool) -> dict[str, Any]:
    """Flag sparse train attention (report-only)."""
    return {
        "sparse_train": sparse_train,
        "apply": False,
        "ok": True,
        "note": "llr llr_sparse",
    }


def llr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Window → shift → lora → score."""
    order = ("window", "shift", "lora", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "window"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "llr llr_loop_plan",
    }
