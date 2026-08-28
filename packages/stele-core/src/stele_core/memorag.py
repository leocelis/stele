"""MemoRAG-shaped memory-clued retrieval (stdlib; no LLM).

Shaped by MemoRAG (arXiv:2409.05591): global memorize, clue/draft
generation, clue-guided retrieve, dual light/expressive system.
Proxies only — not MemoRAG paper scores. No LLM on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def memorag_memorize(*, corpus_chars: int) -> dict[str, Any]:
    """Form a compressed global memory of the database."""
    if corpus_chars < 0:
        raise SchemaError("corpus_chars must be >= 0")
    mid = hashlib.sha256(
        canonical_dumps({"n": corpus_chars}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "corpus_chars": corpus_chars,
        "ok": True,
        "note": "memorag memorag_memorize",
    }


def memorag_clue(*, query: str, draft: str) -> dict[str, Any]:
    """Generate retrieval clues (draft answer) from global memory."""
    q = query.strip()
    d = draft.strip()
    if not q or not d:
        raise SchemaError("query and draft required")
    cid = hashlib.sha256(
        canonical_dumps({"q": q, "d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "clue_id": cid,
        "query": q[:120],
        "ok": True,
        "note": "memorag memorag_clue",
    }


def memorag_retrieve_by_clue(*, clue_id: str, hits: int) -> dict[str, Any]:
    """Retrieve evidence using memory clues instead of raw query alone."""
    cid = clue_id.strip()
    if not cid:
        raise SchemaError("clue_id required")
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "clue_id": cid[:64],
        "hits": hits,
        "ok": True,
        "note": "memorag memorag_retrieve_by_clue",
    }


def memorag_dual_system(*, role: str) -> dict[str, Any]:
    """Dual-system role: light memory model vs expressive generator."""
    r = role.strip().lower()
    if r not in ("memory", "generator"):
        raise SchemaError("role must be memory or generator")
    return {
        "role": r,
        "ok": True,
        "note": "memorag memorag_dual_system",
    }


def memorag_generate_plan(*, evidence: int) -> dict[str, Any]:
    """Final answer generation plan (report-only; no LLM on core)."""
    if evidence < 0:
        raise SchemaError("evidence must be >= 0")
    return {
        "evidence": evidence,
        "ready": evidence >= 1,
        "apply": False,
        "ok": True,
        "note": "memorag memorag_generate_plan",
    }


def memorag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Memorize → clue → retrieve → generate."""
    order = ("memorize", "clue", "retrieve", "generate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "memorize"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memorag memorag_loop_plan",
    }
