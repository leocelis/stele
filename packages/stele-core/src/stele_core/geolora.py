"""GeoLoRA proxies (stdlib; no LLM).

Shaped by GeoLoRA (arXiv:2410.18720 · ICLR 2025): dynamical low-rank
integration with a single backprop over adapters — adaptive budget,
orthonormal factors, faster than AdaLoRA-style dynamical methods.
Proxies only.

Prefix ``geo_*`` — not GeLoRA (``gel_*``) / GaLore (``gal_*``) / RandLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def geo_dyn(*, task: str) -> dict[str, Any]:
    """Declare dynamical low-rank integration state."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    did = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dyn_id": did,
        "ok": True,
        "note": "geo geo_dyn",
    }


def geo_budget(*, dyn_id: str, layers: int) -> dict[str, Any]:
    """Allocate parameter budget across layers (layers >= 1)."""
    did = dyn_id.strip()
    if not did:
        raise SchemaError("dyn_id required")
    if layers < 1:
        raise SchemaError("layers must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"d": did, "l": layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "budget_id": bid,
        "layers": layers,
        "ok": True,
        "note": "geo geo_budget",
    }


def geo_train(*, budget_id: str) -> dict[str, Any]:
    """Train with single-pass backprop over adapters."""
    bid = budget_id.strip()
    if not bid:
        raise SchemaError("budget_id required")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "geo geo_train",
    }


def geo_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score GeoLoRA adaptation (0–100)."""
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
        "note": "geo geo_score",
    }


def geo_ortho(*, exact_ortho: bool) -> dict[str, Any]:
    """Flag exact orthonormal factors (report-only)."""
    return {
        "exact_ortho": exact_ortho,
        "apply": False,
        "ok": True,
        "note": "geo geo_ortho",
    }


def geo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Dyn → budget → train → score."""
    order = ("dyn", "budget", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "dyn"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "geo geo_loop_plan",
    }
