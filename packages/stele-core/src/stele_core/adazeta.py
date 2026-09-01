"""AdaZeta proxies (stdlib; no LLM).

Shaped by AdaZeta (arXiv:2406.18060): tensor-train adapters plus
zeroth-order queries with an adaptive schedule. Proxies only.

Prefix ``azt_*`` — not AdaLoRA (``adl_*``) / TensLoRA (``tnl_*``) /
TeRA (``ter_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def azt_tt(*, task: str, cores: int) -> dict[str, Any]:
    """Open a tensor-train adapter (cores >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if cores < 2:
        raise SchemaError("cores must be >= 2")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "c": cores}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tt_id": tid,
        "cores": cores,
        "ok": True,
        "note": "azt azt_tt",
    }


def azt_ff(*, tt_id: str) -> dict[str, Any]:
    """Fast-forward / parallel TT contraction."""
    tid = tt_id.strip()
    if not tid:
        raise SchemaError("tt_id required")
    fid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ff_id": fid,
        "ok": True,
        "note": "azt azt_ff",
    }


def azt_query(*, ff_id: str) -> dict[str, Any]:
    """Adaptive zeroth-order query schedule."""
    fid = ff_id.strip()
    if not fid:
        raise SchemaError("ff_id required")
    qid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "query_id": qid,
        "ok": True,
        "note": "azt azt_query",
    }


def azt_score(*, query_id: str, score: int) -> dict[str, Any]:
    """Score AdaZeta run (0–100)."""
    qid = query_id.strip()
    if not qid:
        raise SchemaError("query_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"q": qid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "azt azt_score",
    }


def azt_mem(*, zo_memory: bool) -> dict[str, Any]:
    """Flag ZO memory savings vs FO LoRA (report-only)."""
    return {
        "zo_memory": zo_memory,
        "apply": False,
        "ok": True,
        "note": "azt azt_mem",
    }


def azt_loop_plan(*, phase: str) -> dict[str, Any]:
    """TT → ff → query → score."""
    order = ("tt", "ff", "query", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tt"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "azt azt_loop_plan",
    }
