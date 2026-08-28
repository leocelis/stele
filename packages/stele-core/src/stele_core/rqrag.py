"""RQ-RAG-shaped query refine for RAG (stdlib; no LLM).

Shaped by RQ-RAG (arXiv:2404.00610): rewrite, decompose, disambiguate
queries before retrieve. Proxies only — not trained refine tokens.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_MODES = ("rewrite", "decompose", "disambiguate")


def rqrag_rewrite(*, query: str) -> dict[str, Any]:
    """Rewrite query for clearer retrieval."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    rid = hashlib.sha256(
        canonical_dumps({"q": q, "m": "rewrite"}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "refined_id": rid,
        "mode": "rewrite",
        "ok": True,
        "note": "rqrag rqrag_rewrite",
    }


def rqrag_decompose(*, query: str, parts: int) -> dict[str, Any]:
    """Decompose complex query into sub-queries."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if parts < 1:
        raise SchemaError("parts must be >= 1")
    return {
        "parts": parts,
        "mode": "decompose",
        "ok": True,
        "note": "rqrag rqrag_decompose",
    }


def rqrag_disambiguate(*, query: str, intents: int) -> dict[str, Any]:
    """Disambiguate ambiguous query into intent variants."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if intents < 1:
        raise SchemaError("intents must be >= 1")
    return {
        "intents": intents,
        "mode": "disambiguate",
        "ok": True,
        "note": "rqrag rqrag_disambiguate",
    }


def rqrag_refine_mode(*, mode: str) -> dict[str, Any]:
    """Select refine mode."""
    if mode not in _MODES:
        raise SchemaError(f"mode must be one of {list(_MODES)}")
    return {
        "mode": mode,
        "ok": True,
        "note": "rqrag rqrag_refine_mode",
    }


def rqrag_retrieve_refined(*, refined_id: str, k: int = 5) -> dict[str, Any]:
    """Retrieve using refined query id."""
    rid = refined_id.strip()
    if not rid:
        raise SchemaError("refined_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "refined_id": rid[:64],
        "ok": True,
        "note": "rqrag rqrag_retrieve_refined",
    }


def rqrag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Mode → refine → retrieve → answer."""
    order = ("mode", "refine", "retrieve", "answer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "mode"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rqrag rqrag_loop_plan",
    }
