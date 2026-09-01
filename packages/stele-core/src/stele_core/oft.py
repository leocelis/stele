"""OFT proxies (stdlib; no LLM).

Shaped by OFT / BOFT (arXiv:2306.07280 · arXiv:2311.06243): multiplicative
orthogonal transforms of pretrained weights — preserve hyperspherical
energy; BOFT uses butterfly factorization for parameter efficiency. Proxies only.

Prefix ``oft_*`` — not BitFit (``bft_*``) / MiSS (``mss_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def oft_ortho(*, task: str, block: int) -> dict[str, Any]:
    """Declare orthogonal block transform (block >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if block < 1:
        raise SchemaError("block must be >= 1")
    oid = hashlib.sha256(
        canonical_dumps({"t": t, "b": block}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ortho_id": oid,
        "block": block,
        "ok": True,
        "note": "oft oft_ortho",
    }


def oft_butterfly(*, ortho_id: str, factors: int) -> dict[str, Any]:
    """Butterfly factorization (BOFT; factors >= 1; 1 ≡ classic OFT)."""
    oid = ortho_id.strip()
    if not oid:
        raise SchemaError("ortho_id required")
    if factors < 1:
        raise SchemaError("factors must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"o": oid, "f": factors}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "butterfly_id": bid,
        "factors": factors,
        "ok": True,
        "note": "oft oft_butterfly",
    }


def oft_train(*, butterfly_id: str) -> dict[str, Any]:
    """Train orthogonal / butterfly factors."""
    bid = butterfly_id.strip()
    if not bid:
        raise SchemaError("butterfly_id required")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "oft oft_train",
    }


def oft_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score OFT/BOFT adaptation (0–100)."""
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
        "note": "oft oft_score",
    }


def oft_energy(*, hypersphere_preserved: bool) -> dict[str, Any]:
    """Flag hyperspherical energy preservation (report-only)."""
    return {
        "hypersphere_preserved": hypersphere_preserved,
        "apply": False,
        "ok": True,
        "note": "oft oft_energy",
    }


def oft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Ortho → butterfly → train → score."""
    order = ("ortho", "butterfly", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "ortho"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "oft oft_loop_plan",
    }
