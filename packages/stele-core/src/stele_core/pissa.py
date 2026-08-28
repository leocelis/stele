"""PiSSA proxies (stdlib; no LLM).

Shaped by PiSSA (arXiv:2404.02948): SVD-init A,B from principal components of W;
freeze residual W^res — same architecture as LoRA, faster convergence.
Proxies only.

Prefix ``psa_*`` — not Diff Pruning (``dpr_*``) / LoRA (``lora_*``) / AdaLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def psa_svd(*, task: str, rank: int) -> dict[str, Any]:
    """Factor W via SVD; allocate principal rank r (>=1)."""
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
        "note": "psa psa_svd",
    }


def psa_principal(*, svd_id: str) -> dict[str, Any]:
    """Initialize A,B from principal singular values/vectors."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    pid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "principal_id": pid,
        "ok": True,
        "note": "psa psa_principal",
    }


def psa_residual(*, principal_id: str) -> dict[str, Any]:
    """Freeze residual W^res from remaining singular components."""
    pid = principal_id.strip()
    if not pid:
        raise SchemaError("principal_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "residual_id": rid,
        "ok": True,
        "note": "psa psa_residual",
    }


def psa_score(*, residual_id: str, score: int) -> dict[str, Any]:
    """Score PiSSA adaptation (0–100)."""
    rid = residual_id.strip()
    if not rid:
        raise SchemaError("residual_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "psa psa_score",
    }


def psa_fast(*, faster_than_lora: bool) -> dict[str, Any]:
    """Flag faster convergence vs Gaussian/zero LoRA init (report-only)."""
    return {
        "faster_than_lora": faster_than_lora,
        "apply": False,
        "ok": True,
        "note": "psa psa_fast",
    }


def psa_loop_plan(*, phase: str) -> dict[str, Any]:
    """SVD → principal → residual → score."""
    order = ("svd", "principal", "residual", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "svd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "psa psa_loop_plan",
    }
