"""LoRA-Pro proxies (stdlib; no LLM).

Shaped by LoRA-Pro (arXiv:2407.18242): adjust adapter gradients so the
equivalent gradient of BA matches full fine-tuning — closes the LoRA↔FFT
optimization gap. Proxies only.

Prefix ``lpr_*`` — not LoRA+ (``lrp_*``) / LoRA-GA (``lga_*``) / Kron-LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lpr_equiv(*, task: str) -> dict[str, Any]:
    """Declare equivalent-gradient target for LoRA vs full FT."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    eid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "equiv_id": eid,
        "ok": True,
        "note": "lpr lpr_equiv",
    }


def lpr_adjust(*, equiv_id: str) -> dict[str, Any]:
    """Closed-form gradient adjustment for A and B."""
    eid = equiv_id.strip()
    if not eid:
        raise SchemaError("equiv_id required")
    aid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adjust_id": aid,
        "ok": True,
        "note": "lpr lpr_adjust",
    }


def lpr_train(*, adjust_id: str) -> dict[str, Any]:
    """Train with LoRA-Pro adjusted gradients."""
    aid = adjust_id.strip()
    if not aid:
        raise SchemaError("adjust_id required")
    tid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lpr lpr_train",
    }


def lpr_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Pro adaptation (0–100)."""
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
        "note": "lpr lpr_score",
    }


def lpr_bridge(*, closer_to_fft: bool) -> dict[str, Any]:
    """Flag closer optimization to full fine-tuning (report-only)."""
    return {
        "closer_to_fft": closer_to_fft,
        "apply": False,
        "ok": True,
        "note": "lpr lpr_bridge",
    }


def lpr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Equiv → adjust → train → score."""
    order = ("equiv", "adjust", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "equiv"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lpr lpr_loop_plan",
    }
