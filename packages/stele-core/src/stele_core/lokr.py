"""LoKr proxies (stdlib; no LLM).

Shaped by LoKr (arXiv:2309.14859): replace BA matrix product with a
Kronecker product of factors — preserves rank structure, vectorizable,
often used for diffusion adapters. Proxies only.

Prefix ``lkr_*`` — not Kron-LoRA / rsLoRA (``rsl_*``) / LoRA-GA (``lga_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lkr_factors(*, task: str, factor_a: int, factor_b: int) -> dict[str, Any]:
    """Declare Kronecker factors (both >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if factor_a < 1 or factor_b < 1:
        raise SchemaError("factor_a and factor_b must be >= 1")
    fid = hashlib.sha256(
        canonical_dumps({"t": t, "a": factor_a, "b": factor_b}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "factors_id": fid,
        "factor_a": factor_a,
        "factor_b": factor_b,
        "ok": True,
        "note": "lkr lkr_factors",
    }


def lkr_kron(*, factors_id: str) -> dict[str, Any]:
    """Form Kronecker product of the two factors."""
    fid = factors_id.strip()
    if not fid:
        raise SchemaError("factors_id required")
    kid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "kron_id": kid,
        "ok": True,
        "note": "lkr lkr_kron",
    }


def lkr_vectorize(*, kron_id: str) -> dict[str, Any]:
    """Vectorize via column-stack (avoid full ΔW reconstruct)."""
    kid = kron_id.strip()
    if not kid:
        raise SchemaError("kron_id required")
    vid = hashlib.sha256(
        canonical_dumps({"k": kid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "vector_id": vid,
        "ok": True,
        "note": "lkr lkr_vectorize",
    }


def lkr_score(*, vector_id: str, score: int) -> dict[str, Any]:
    """Score LoKr adaptation (0–100)."""
    vid = vector_id.strip()
    if not vid:
        raise SchemaError("vector_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"v": vid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lkr lkr_score",
    }


def lkr_preserve(*, rank_preserved: bool) -> dict[str, Any]:
    """Flag that Kronecker form preserves rank structure (report-only)."""
    return {
        "rank_preserved": rank_preserved,
        "apply": False,
        "ok": True,
        "note": "lkr lkr_preserve",
    }


def lkr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Factors → kron → vectorize → score."""
    order = ("factors", "kron", "vectorize", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "factors"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lkr lkr_loop_plan",
    }
