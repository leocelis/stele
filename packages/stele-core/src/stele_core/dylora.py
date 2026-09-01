"""DyLoRA proxies (stdlib; no LLM).

Shaped by DyLoRA (arXiv:2210.07558): train across a range of ranks;
select rank at inference without search. Proxies only.

Prefix ``dyl_*`` — not LoRA-FA (``lfa_*``) / AdaLoRA (``adl_*``) / LoRA+.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dyl_range(*, task: str, r_min: int, r_max: int) -> dict[str, Any]:
    """Declare a dynamic rank range [r_min, r_max] (1 <= r_min <= r_max)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if r_min < 1 or r_max < r_min:
        raise SchemaError("require 1 <= r_min <= r_max")
    rid = hashlib.sha256(
        canonical_dumps({"t": t, "lo": r_min, "hi": r_max}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "range_id": rid,
        "r_min": r_min,
        "r_max": r_max,
        "ok": True,
        "note": "dyl dyl_range",
    }


def dyl_sample(*, range_id: str) -> dict[str, Any]:
    """Sample a truncated rank from the trained range during training."""
    rid = range_id.strip()
    if not rid:
        raise SchemaError("range_id required")
    sid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sample_id": sid,
        "ok": True,
        "note": "dyl dyl_sample",
    }


def dyl_select(*, sample_id: str, rank: int) -> dict[str, Any]:
    """Select an inference rank within the trained range (rank >= 1)."""
    sid = sample_id.strip()
    if not sid:
        raise SchemaError("sample_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid, "k": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "select_id": xid,
        "rank": rank,
        "ok": True,
        "note": "dyl dyl_select",
    }


def dyl_score(*, select_id: str, score: int) -> dict[str, Any]:
    """Score DyLoRA adaptation (0–100)."""
    sid = select_id.strip()
    if not sid:
        raise SchemaError("select_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid, "sc": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "dyl dyl_score",
    }


def dyl_searchfree(*, search_free: bool) -> dict[str, Any]:
    """Flag search-free rank selection at inference (report-only)."""
    return {
        "search_free": search_free,
        "apply": False,
        "ok": True,
        "note": "dyl dyl_searchfree",
    }


def dyl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Range → sample → select → score."""
    order = ("range", "sample", "select", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "range"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dyl dyl_loop_plan",
    }
