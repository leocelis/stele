"""Delta-LoRA proxies (stdlib; no LLM).

Shaped by Delta-LoRA (arXiv:2309.02411): update A/B and propagate
Δ(AB) into pretrained W without storing W gradients. Proxies only.

Prefix ``dlo_*`` — not DoRA (``dora_*``) / DropLoRA (``drl_*``) / LoRA-One.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dlo_adapters(*, task: str, rank: int) -> dict[str, Any]:
    """Declare low-rank A/B adapters (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapters_id": aid,
        "rank": rank,
        "ok": True,
        "note": "dlo dlo_adapters",
    }


def dlo_delta(*, adapters_id: str) -> dict[str, Any]:
    """Compute delta of AB across steps for W update."""
    aid = adapters_id.strip()
    if not aid:
        raise SchemaError("adapters_id required")
    did = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "delta_id": did,
        "ok": True,
        "note": "dlo dlo_delta",
    }


def dlo_propagate(*, delta_id: str) -> dict[str, Any]:
    """Propagate Δ(AB) into pretrained W (no W optimizer state)."""
    did = delta_id.strip()
    if not did:
        raise SchemaError("delta_id required")
    pid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "propagate_id": pid,
        "ok": True,
        "note": "dlo dlo_propagate",
    }


def dlo_score(*, propagate_id: str, score: int) -> dict[str, Any]:
    """Score Delta-LoRA adaptation (0–100)."""
    pid = propagate_id.strip()
    if not pid:
        raise SchemaError("propagate_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "dlo dlo_score",
    }


def dlo_highrank(*, high_rank_capacity: bool) -> dict[str, Any]:
    """Flag high-rank capacity via W delta (report-only)."""
    return {
        "high_rank_capacity": high_rank_capacity,
        "apply": False,
        "ok": True,
        "note": "dlo dlo_highrank",
    }


def dlo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Adapters → delta → propagate → score."""
    order = ("adapters", "delta", "propagate", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "adapters"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dlo dlo_loop_plan",
    }
