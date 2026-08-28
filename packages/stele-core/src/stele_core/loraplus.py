"""LoRA+ proxies (stdlib; no LLM).

Shaped by LoRA+ (arXiv:2402.12354): set learning rate of B to λ× that
of A (λ ≫ 1) so large-width models learn features efficiently. Proxies only.

Prefix ``lrp_*`` — not LoRA-Pro (``lpr_*``) / LoRA-FA (``lfa_*``) / FLoRA
(``flo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lrp_split(*, task: str) -> dict[str, Any]:
    """Split A/B learning-rate schedule for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "split_id": sid,
        "ok": True,
        "note": "lrp lrp_split",
    }


def lrp_ratio(*, split_id: str, lambda_ratio: int) -> dict[str, Any]:
    """Declare η_B / η_A ratio (lambda_ratio >= 2)."""
    sid = split_id.strip()
    if not sid:
        raise SchemaError("split_id required")
    if lambda_ratio < 2:
        raise SchemaError("lambda_ratio must be >= 2")
    rid = hashlib.sha256(
        canonical_dumps({"s": sid, "l": lambda_ratio}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ratio_id": rid,
        "lambda_ratio": lambda_ratio,
        "ok": True,
        "note": "lrp lrp_ratio",
    }


def lrp_train(*, ratio_id: str) -> dict[str, Any]:
    """Train with asymmetric learning rates."""
    rid = ratio_id.strip()
    if not rid:
        raise SchemaError("ratio_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lrp lrp_train",
    }


def lrp_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA+ adaptation (0–100)."""
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
        "note": "lrp lrp_score",
    }


def lrp_speed(*, faster_than_lora: bool) -> dict[str, Any]:
    """Flag finetuning speedup vs LoRA (report-only)."""
    return {
        "faster_than_lora": faster_than_lora,
        "apply": False,
        "ok": True,
        "note": "lrp lrp_speed",
    }


def lrp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Split → ratio → train → score."""
    order = ("split", "ratio", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "split"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lrp lrp_loop_plan",
    }
