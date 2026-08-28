"""Toolformer-shaped API call selection (stdlib; no LLM / no live APIs).

Shaped by Toolformer (arXiv:2302.04761): propose API calls, filter by
usefulness, execute proxy, incorporate result. Proxies only — not Meta
Toolformer training.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tf_api_candidate(*, api: str, args: str) -> dict[str, Any]:
    """Propose a candidate API call."""
    a = api.strip()
    g = args.strip()
    if not a:
        raise SchemaError("api required")
    cid = hashlib.sha256(
        canonical_dumps({"a": a, "g": g}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "candidate_id": cid,
        "api": a[:64],
        "ok": True,
        "note": "toolformer tf_api_candidate",
    }


def tf_filter_call(*, candidate_id: str, useful: bool) -> dict[str, Any]:
    """Filter call by self-supervised usefulness (report-only)."""
    cid = candidate_id.strip()
    if not cid:
        raise SchemaError("candidate_id required")
    return {
        "candidate_id": cid[:64],
        "keep": useful,
        "apply": False,
        "ok": True,
        "note": "toolformer tf_filter_call",
    }


def tf_execute_proxy(*, api: str) -> dict[str, Any]:
    """Execute API via local proxy (no network)."""
    a = api.strip()
    if not a:
        raise SchemaError("api required")
    rid = hashlib.sha256(
        canonical_dumps({"a": a}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "result_id": rid,
        "api": a[:64],
        "apply": False,
        "ok": True,
        "note": "toolformer tf_execute_proxy",
    }


def tf_incorporate_result(*, result_id: str) -> dict[str, Any]:
    """Incorporate tool result into next-token prediction context."""
    rid = result_id.strip()
    if not rid:
        raise SchemaError("result_id required")
    return {
        "result_id": rid[:64],
        "incorporated": True,
        "ok": True,
        "note": "toolformer tf_incorporate_result",
    }


def tf_demo_apis(*, count: int) -> dict[str, Any]:
    """Count few-shot API demonstrations."""
    if count < 0:
        raise SchemaError("count must be >= 0")
    return {
        "demos": count,
        "ok": True,
        "note": "toolformer tf_demo_apis",
    }


def tf_loop_plan(*, phase: str) -> dict[str, Any]:
    """Candidate → filter → execute → incorporate."""
    order = ("candidate", "filter", "execute", "incorporate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "candidate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "toolformer tf_loop_plan",
    }
