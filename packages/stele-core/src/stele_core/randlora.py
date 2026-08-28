"""RandLoRA proxies (stdlib; no LLM).

Shaped by RandLoRA (arXiv:2502.00987): full-rank updates via learned
diagonal scales on fixed random low-rank bases — closes LoRA↔FFT gap
without training the bases. Proxies only.

Prefix ``rlo_*`` — not LoRA (``lora_*``) / VeRA (``vra_*``) / GeoLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rlo_bases(*, task: str, count: int) -> dict[str, Any]:
    """Declare fixed random low-rank bases (count >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if count < 1:
        raise SchemaError("count must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"t": t, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "bases_id": bid,
        "count": count,
        "ok": True,
        "note": "rlo rlo_bases",
    }


def rlo_scale(*, bases_id: str) -> dict[str, Any]:
    """Learn diagonal scaling over frozen random bases."""
    bid = bases_id.strip()
    if not bid:
        raise SchemaError("bases_id required")
    sid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "rlo rlo_scale",
    }


def rlo_train(*, scale_id: str) -> dict[str, Any]:
    """Train RandLoRA scales for full-rank effective update."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "rlo rlo_train",
    }


def rlo_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score RandLoRA adaptation (0–100)."""
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
        "note": "rlo rlo_score",
    }


def rlo_fullrank(*, full_rank_update: bool) -> dict[str, Any]:
    """Flag full-rank effective update (report-only)."""
    return {
        "full_rank_update": full_rank_update,
        "apply": False,
        "ok": True,
        "note": "rlo rlo_fullrank",
    }


def rlo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Bases → scale → train → score."""
    order = ("bases", "scale", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "bases"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rlo rlo_loop_plan",
    }
