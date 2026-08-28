"""NOLA proxies (stdlib; no LLM).

Shaped by NOLA (arXiv:2310.02556): reparameterize LoRA A/B as linear
combinations of frozen random bases; train coefficients only — breaks
the rank-1 parameter floor. Proxies only.

Prefix ``nla_*`` — not FlyLoRA (``fly_*``) / VeRA / VB-LoRA (``vbl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def nla_basis(*, task: str, n_basis: int) -> dict[str, Any]:
    """Draw frozen random bases (n_basis >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_basis < 1:
        raise SchemaError("n_basis must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_basis}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "basis_id": bid,
        "n_basis": n_basis,
        "ok": True,
        "note": "nla nla_basis",
    }


def nla_coeff(*, basis_id: str) -> dict[str, Any]:
    """Allocate trainable mixture coefficients."""
    bid = basis_id.strip()
    if not bid:
        raise SchemaError("basis_id required")
    cid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "coeff_id": cid,
        "ok": True,
        "note": "nla nla_coeff",
    }


def nla_train(*, coeff_id: str) -> dict[str, Any]:
    """Train NOLA coefficients only."""
    cid = coeff_id.strip()
    if not cid:
        raise SchemaError("coeff_id required")
    tid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "nla nla_train",
    }


def nla_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score NOLA run (0–100)."""
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
        "note": "nla nla_score",
    }


def nla_compact(*, beyond_rank1: bool) -> dict[str, Any]:
    """Flag compression beyond LoRA rank-1 (report-only)."""
    return {
        "beyond_rank1": beyond_rank1,
        "apply": False,
        "ok": True,
        "note": "nla nla_compact",
    }


def nla_loop_plan(*, phase: str) -> dict[str, Any]:
    """Basis → coeff → train → score."""
    order = ("basis", "coeff", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "basis"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "nla nla_loop_plan",
    }
