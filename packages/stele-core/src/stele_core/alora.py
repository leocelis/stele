"""ALoRA proxies (stdlib; no LLM).

Shaped by ALoRA (arXiv:2403.16187): AB-LoRA scores each rank,
prunes dead ones, and reallocates budget to hotter modules.
Proxies only.

Prefix ``alo_*`` — not AdaLoRA (``adl_*``) / LoRA (``lra_*``) /
C-LoRA (``clo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def alo_init(*, task: str, rank: int) -> dict[str, Any]:
    """Start equal-rank gates (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "rank": rank,
        "ok": True,
        "note": "alo alo_init",
    }


def alo_ablate(*, init_id: str) -> dict[str, Any]:
    """AB-LoRA rank-importance scores."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    aid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ablate_id": aid,
        "ok": True,
        "note": "alo alo_ablate",
    }


def alo_prune(*, ablate_id: str) -> dict[str, Any]:
    """Prune dead ranks; grow budget on hot modules."""
    aid = ablate_id.strip()
    if not aid:
        raise SchemaError("ablate_id required")
    pid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prune_id": pid,
        "ok": True,
        "note": "alo alo_prune",
    }


def alo_score(*, prune_id: str, score: int) -> dict[str, Any]:
    """Score ALoRA run (0–100)."""
    pid = prune_id.strip()
    if not pid:
        raise SchemaError("prune_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "alo alo_score",
    }


def alo_realloc(*, dynamic: bool) -> dict[str, Any]:
    """Flag dynamic rank reallocation (report-only)."""
    return {
        "dynamic": dynamic,
        "apply": False,
        "ok": True,
        "note": "alo alo_realloc",
    }


def alo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → ablate → prune → score."""
    order = ("init", "ablate", "prune", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "alo alo_loop_plan",
    }
