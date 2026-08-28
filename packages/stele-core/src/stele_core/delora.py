"""DeLoRA proxies (stdlib; no LLM).

Shaped by DeLoRA (arXiv:2503.18225 · ICLR 2025): normalize and scale
low-rank updates to bound Frobenius distance — decouple angular learning
from adaptation strength for hyperparameter robustness. Proxies only.

Prefix ``dlr_*`` — not Delta-LoRA (``dlo_*``) / MELoRA (``meo_*``) /
DoRA (``dora_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dlr_norm(*, task: str, rank: int) -> dict[str, Any]:
    """Normalize BA low-rank factors (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    nid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "norm_id": nid,
        "rank": rank,
        "ok": True,
        "note": "dlr dlr_norm",
    }


def dlr_bound(*, norm_id: str, lambda_bound: int) -> dict[str, Any]:
    """Set Frobenius boundary λ (lambda_bound >= 1)."""
    nid = norm_id.strip()
    if not nid:
        raise SchemaError("norm_id required")
    if lambda_bound < 1:
        raise SchemaError("lambda_bound must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"n": nid, "l": lambda_bound}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "bound_id": bid,
        "lambda_bound": lambda_bound,
        "ok": True,
        "note": "dlr dlr_bound",
    }


def dlr_train(*, bound_id: str) -> dict[str, Any]:
    """Train with decoupled angle vs strength."""
    bid = bound_id.strip()
    if not bid:
        raise SchemaError("bound_id required")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "dlr dlr_train",
    }


def dlr_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score DeLoRA adaptation (0–100)."""
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
        "note": "dlr dlr_score",
    }


def dlr_robust(*, hyperparam_robust: bool) -> dict[str, Any]:
    """Flag hyperparameter / long-train robustness (report-only)."""
    return {
        "hyperparam_robust": hyperparam_robust,
        "apply": False,
        "ok": True,
        "note": "dlr dlr_robust",
    }


def dlr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Norm → bound → train → score."""
    order = ("norm", "bound", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "norm"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dlr dlr_loop_plan",
    }
