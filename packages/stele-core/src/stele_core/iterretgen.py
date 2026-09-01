"""Iter-RetGen-shaped iterative retrieve–generate synergy (stdlib; no LLM).

Shaped by Iter-RetGen (arXiv:2305.15294): generation becomes next
retrieval query; retrieve better docs; iterate; optional retriever adapt.
Proxies only — not live LLM iterations.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def iterretgen_generate(*, iteration: int, draft: str) -> dict[str, Any]:
    """Record a generation draft used to guide the next retrieve."""
    if iteration < 0:
        raise SchemaError("iteration must be >= 0")
    d = draft.strip()
    if not d:
        raise SchemaError("draft required")
    gen_id = hashlib.sha256(
        canonical_dumps({"i": iteration, "d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gen_id": gen_id,
        "iteration": iteration,
        "ok": True,
        "note": "iterretgen iterretgen_generate",
    }


def iterretgen_use_as_query(*, gen_id: str) -> dict[str, Any]:
    """Treat prior generation as the next retrieval query context."""
    gid = gen_id.strip()
    if not gid:
        raise SchemaError("gen_id required")
    return {
        "query_from": gid[:64],
        "ok": True,
        "note": "iterretgen iterretgen_use_as_query",
    }


def iterretgen_retrieve_next(*, query_from: str, k: int = 5) -> dict[str, Any]:
    """Retrieve using generation-augmented context."""
    qf = query_from.strip()
    if not qf:
        raise SchemaError("query_from required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "ok": True,
        "note": "iterretgen iterretgen_retrieve_next",
    }


def iterretgen_iterate(*, round_n: int, max_rounds: int = 3) -> dict[str, Any]:
    """Advance or stop the retrieve–generate loop."""
    if round_n < 0 or max_rounds < 1:
        raise SchemaError("round_n >= 0 and max_rounds >= 1")
    cont = round_n < max_rounds
    return {
        "continue": cont,
        "round": round_n,
        "ok": True,
        "note": "iterretgen iterretgen_iterate",
    }


def iterretgen_adapt_retriever(*, improve: bool) -> dict[str, Any]:
    """Generation-augmented retrieval adaptation plan (report-only)."""
    return {
        "adapt": improve,
        "apply": False,
        "ok": True,
        "note": "iterretgen iterretgen_adapt_retriever",
    }


def iterretgen_loop_plan(*, phase: str) -> dict[str, Any]:
    """Generate → query → retrieve → iterate."""
    order = ("generate", "query", "retrieve", "iterate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "generate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "iterretgen iterretgen_loop_plan",
    }
