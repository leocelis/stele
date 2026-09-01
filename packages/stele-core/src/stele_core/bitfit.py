"""BitFit proxies (stdlib; no LLM).

Shaped by BitFit (arXiv:2106.10199): freeze all weights; train only bias
terms (+ task head). Proxies only.

Prefix ``bft_*`` — not DoRA (``dora_*``) / LoRA (``lora_*``) / (IA)^3.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def bft_freeze(*, weights_frozen: bool) -> dict[str, Any]:
    """Flag frozen non-bias weights (report-only)."""
    return {
        "weights_frozen": weights_frozen,
        "apply": False,
        "ok": True,
        "note": "bft bft_freeze",
    }


def bft_bias(*, task: str) -> dict[str, Any]:
    """Select bias terms as the only trainable subset for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    bid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "bias_id": bid,
        "ok": True,
        "note": "bft bft_bias",
    }


def bft_train(*, bias_id: str) -> dict[str, Any]:
    """Train bias terms (+ task head) only."""
    bid = bias_id.strip()
    if not bid:
        raise SchemaError("bias_id required")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "bft bft_train",
    }


def bft_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score BitFit adaptation (0–100)."""
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
        "note": "bft bft_score",
    }


def bft_tiny(*, fraction_pct: int) -> dict[str, Any]:
    """Flag tiny trainable fraction (e.g. ~0.08% → 8 basis points)."""
    if fraction_pct < 0 or fraction_pct > 10000:
        raise SchemaError("fraction_pct must be 0..10000 (basis points)")
    return {
        "fraction_pct": fraction_pct,
        "apply": False,
        "ok": True,
        "note": "bft bft_tiny",
    }


def bft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Freeze → bias → train → score."""
    order = ("freeze", "bias", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "freeze"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "bft bft_loop_plan",
    }
