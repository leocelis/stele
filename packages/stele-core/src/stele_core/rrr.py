"""Rewrite-Retrieve-Read shaped query rewrite RAG (stdlib; no LLM).

Shaped by Rewrite-Retrieve-Read (arXiv:2305.14283): rewrite query,
retrieve, read with frozen LLM, reader feedback, rewriter train plan.
Proxies only — not RL-trained rewriter.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rrr_rewrite_query(*, query: str) -> dict[str, Any]:
    """Rewrite the search query before retrieve."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    rid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rewrite_id": rid,
        "ok": True,
        "note": "rrr rrr_rewrite_query",
    }


def rrr_retrieve(*, rewrite_id: str, k: int = 5) -> dict[str, Any]:
    """Retrieve using rewritten query."""
    rid = rewrite_id.strip()
    if not rid:
        raise SchemaError("rewrite_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "rewrite_id": rid[:64],
        "ok": True,
        "note": "rrr rrr_retrieve",
    }


def rrr_read(*, hits: int) -> dict[str, Any]:
    """Read retrieved contexts with frozen LLM reader (proxy)."""
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "read": hits >= 1,
        "hits": hits,
        "ok": True,
        "note": "rrr rrr_read",
    }


def rrr_reader_feedback(*, reward: float) -> dict[str, Any]:
    """LLM reader feedback signal for rewriter (0–1)."""
    if not (0.0 <= reward <= 1.0):
        raise SchemaError("reward must be in [0, 1]")
    return {
        "reward": round(reward, 4),
        "ok": True,
        "note": "rrr rrr_reader_feedback",
    }


def rrr_train_rewriter_plan(*, improve: bool) -> dict[str, Any]:
    """Trainable rewriter update plan (report-only)."""
    return {
        "train": improve,
        "apply": False,
        "ok": True,
        "note": "rrr rrr_train_rewriter_plan",
    }


def rrr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Rewrite → retrieve → read → feedback."""
    order = ("rewrite", "retrieve", "read", "feedback")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "rewrite"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rrr rrr_loop_plan",
    }
