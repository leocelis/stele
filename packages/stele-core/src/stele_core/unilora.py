"""Uni-LoRA proxies (stdlib; no LLM).

Shaped by Uni-LoRA (arXiv:2506.00799): isometric global projection so
one trainable vector reconstructs all LoRA params. Proxies only.

Prefix ``ulo_*`` — not Tied-LoRA (``tlo_*`` / ``tld_*``) / VeRA (``vra_*``)
/ BoRA (``bor_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ulo_space(*, task: str, dim: int) -> dict[str, Any]:
    """Allocate the shared subspace (dim >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if dim < 1:
        raise SchemaError("dim must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "d": dim}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "space_id": sid,
        "dim": dim,
        "ok": True,
        "note": "ulo ulo_space",
    }


def ulo_iso(*, space_id: str) -> dict[str, Any]:
    """Build the isometric projection P."""
    sid = space_id.strip()
    if not sid:
        raise SchemaError("space_id required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "iso_id": iid,
        "ok": True,
        "note": "ulo ulo_iso",
    }


def ulo_vec(*, iso_id: str) -> dict[str, Any]:
    """Train the single shared vector."""
    iid = iso_id.strip()
    if not iid:
        raise SchemaError("iso_id required")
    vid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "vec_id": vid,
        "ok": True,
        "note": "ulo ulo_vec",
    }


def ulo_score(*, vec_id: str, score: int) -> dict[str, Any]:
    """Score Uni-LoRA run (0–100)."""
    vid = vec_id.strip()
    if not vid:
        raise SchemaError("vec_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"v": vid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "ulo ulo_score",
    }


def ulo_one(*, one_vector: bool) -> dict[str, Any]:
    """Flag one-vector reconstruction (report-only)."""
    return {
        "one_vector": one_vector,
        "apply": False,
        "ok": True,
        "note": "ulo ulo_one",
    }


def ulo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Space → iso → vec → score."""
    order = ("space", "iso", "vec", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "space"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ulo ulo_loop_plan",
    }
