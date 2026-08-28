"""GeLoRA proxies (stdlib; no LLM).

Shaped by GeLoRA (arXiv:2412.09250): geometric adaptive ranks from
intrinsic dimensionality of hidden states — principled rank lower
bound per layer. Proxies only.

Prefix ``gel_*`` — not GeoLoRA (``geo_*`` reserved) / OPLoRA (``opl_*``) /
GaLore (``gal_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def gel_idim(*, task: str, layer: int) -> dict[str, Any]:
    """Estimate intrinsic dimensionality for a layer (layer >= 0)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if layer < 0:
        raise SchemaError("layer must be >= 0")
    iid = hashlib.sha256(
        canonical_dumps({"t": t, "l": layer}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "idim_id": iid,
        "layer": layer,
        "ok": True,
        "note": "gel gel_idim",
    }


def gel_rank(*, idim_id: str, rank: int) -> dict[str, Any]:
    """Select adaptive LoRA rank from intrinsic-dim lower bound."""
    iid = idim_id.strip()
    if not iid:
        raise SchemaError("idim_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"i": iid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rank_id": rid,
        "rank": rank,
        "ok": True,
        "note": "gel gel_rank",
    }


def gel_train(*, rank_id: str) -> dict[str, Any]:
    """Train GeLoRA at the selected adaptive rank."""
    rid = rank_id.strip()
    if not rid:
        raise SchemaError("rank_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "gel gel_train",
    }


def gel_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score GeLoRA adaptation (0–100)."""
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
        "note": "gel gel_score",
    }


def gel_budget(*, within_budget: bool) -> dict[str, Any]:
    """Flag better accuracy within same param budget (report-only)."""
    return {
        "within_budget": within_budget,
        "apply": False,
        "ok": True,
        "note": "gel gel_budget",
    }


def gel_loop_plan(*, phase: str) -> dict[str, Any]:
    """Idim → rank → train → score."""
    order = ("idim", "rank", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "idim"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "gel gel_loop_plan",
    }
