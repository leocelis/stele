"""Alternating OPLoRA proxies (stdlib; no LLM).

Shaped by *Faster Than SVD, Smarter Than SGD: The OPLoRA Alternating
Update* (arXiv:2509.19977): cast LoRA steps as ALS / LoRSum
subproblems so 1–2 alternating updates approach truncated-SVD LoRA
without forming the full matrix. Proxies only.

Prefix ``aop_*`` — not orthogonal-projection OPLoRA (``opl_*``) /
OLoRA (``olr_*``) / LoRAShear (``lsh_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def aop_sub(*, task: str) -> dict[str, Any]:
    """Declare LoRSum / ALS LoRA subproblem state."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sub_id": sid,
        "ok": True,
        "note": "aop aop_sub",
    }


def aop_alt(*, sub_id: str, steps: int) -> dict[str, Any]:
    """Run alternating least-squares steps (1–8)."""
    sid = sub_id.strip()
    if not sid:
        raise SchemaError("sub_id required")
    if steps < 1 or steps > 8:
        raise SchemaError("steps must be 1..8")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid, "k": steps}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "alt_id": aid,
        "steps": steps,
        "ok": True,
        "note": "aop aop_alt",
    }


def aop_train(*, alt_id: str) -> dict[str, Any]:
    """Apply alternating OPLoRA update to adapters."""
    aid = alt_id.strip()
    if not aid:
        raise SchemaError("alt_id required")
    tid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "aop aop_train",
    }


def aop_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score alternating OPLoRA (0–100)."""
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
        "note": "aop aop_score",
    }


def aop_svd(*, near_svd: bool) -> dict[str, Any]:
    """Flag near-SVDLoRA direction without full matrix (report-only)."""
    return {
        "near_svd": near_svd,
        "apply": False,
        "ok": True,
        "note": "aop aop_svd",
    }


def aop_loop_plan(*, phase: str) -> dict[str, Any]:
    """Sub → alt → train → score."""
    order = ("sub", "alt", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "sub"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "aop aop_loop_plan",
    }
