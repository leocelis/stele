"""MiLoRA proxies (stdlib; no LLM).

Shaped by MiLoRA (arXiv:2406.09044): update minor singular components
while freezing principal ones — preserves pretrained knowledge in an
orthogonal subspace. Proxies only.

Prefix ``mil_*`` — not PiSSA (``psa_*``) / MoRA (``mor_*``) / mixture-MiLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mil_svd(*, task: str, rank: int) -> dict[str, Any]:
    """Declare SVD split for minor-component adaptation (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "svd_id": sid,
        "rank": rank,
        "ok": True,
        "note": "mil mil_svd",
    }


def mil_minor(*, svd_id: str) -> dict[str, Any]:
    """Select minor singular components for training."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "minor_id": mid,
        "ok": True,
        "note": "mil mil_minor",
    }


def mil_freeze(*, minor_id: str) -> dict[str, Any]:
    """Freeze principal components (knowledge preserve)."""
    mid = minor_id.strip()
    if not mid:
        raise SchemaError("minor_id required")
    fid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "freeze_id": fid,
        "ok": True,
        "note": "mil mil_freeze",
    }


def mil_score(*, freeze_id: str, score: int) -> dict[str, Any]:
    """Score MiLoRA adaptation (0–100)."""
    fid = freeze_id.strip()
    if not fid:
        raise SchemaError("freeze_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mil mil_score",
    }


def mil_preserve(*, preserves_principal: bool) -> dict[str, Any]:
    """Flag principal-knowledge preserve (report-only)."""
    return {
        "preserves_principal": preserves_principal,
        "apply": False,
        "ok": True,
        "note": "mil mil_preserve",
    }


def mil_loop_plan(*, phase: str) -> dict[str, Any]:
    """Svd → minor → freeze → score."""
    order = ("svd", "minor", "freeze", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "svd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mil mil_loop_plan",
    }
