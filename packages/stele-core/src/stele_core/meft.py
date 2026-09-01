"""MEFT proxies (stdlib; no LLM).

Shaped by *MEFT: Memory-Efficient Fine-Tuning through Sparse Adapter*
(arXiv:2406.04984): large sparse adapters on CPU with MoE-like routing
to cut GPU memory. Proxies only.

Prefix ``mef_*`` — unused at ship time (grep CLI + ops + modules).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mef_adapt(*, task: str) -> dict[str, Any]:
    """Open a sparse parallel adapter."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    aid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": aid,
        "ok": True,
        "note": "mef mef_adapt",
    }


def mef_route(*, adapt_id: str) -> dict[str, Any]:
    """MoE / key-expert router over the sparse adapter."""
    aid = adapt_id.strip()
    if not aid:
        raise SchemaError("adapt_id required")
    rid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "route_id": rid,
        "ok": True,
        "note": "mef mef_route",
    }


def mef_fetch(*, route_id: str) -> dict[str, Any]:
    """Fetch sparse neurons from CPU-side capacity."""
    rid = route_id.strip()
    if not rid:
        raise SchemaError("route_id required")
    fid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fetch_id": fid,
        "ok": True,
        "note": "mef mef_fetch",
    }


def mef_score(*, fetch_id: str, score: int) -> dict[str, Any]:
    """Score MEFT run (0–100)."""
    fid = fetch_id.strip()
    if not fid:
        raise SchemaError("fetch_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mef mef_score",
    }


def mef_cpu(*, cpu_offload: bool) -> dict[str, Any]:
    """Flag CPU-offloaded large adapter (report-only)."""
    return {
        "cpu_offload": cpu_offload,
        "apply": False,
        "ok": True,
        "note": "mef mef_cpu",
    }


def mef_loop_plan(*, phase: str) -> dict[str, Any]:
    """Adapt → route → fetch → score."""
    order = ("adapt", "route", "fetch", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "adapt"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mef mef_loop_plan",
    }
