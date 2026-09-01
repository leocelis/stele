"""Self-RAG-shaped on-demand retrieve + critique (stdlib; no LLM).

Shaped by Self-RAG (arXiv:2310.11511): decide whether to retrieve,
critique relevance/support/utility, select best continuation.
Proxies only — not Self-RAG trained reflection tokens.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError


def selfrag_need_retrieve(*, confidence: float, threshold: float = 0.5) -> dict[str, Any]:
    """Decide whether retrieval would help continued generation."""
    if not (0.0 <= confidence <= 1.0) or not (0.0 <= threshold <= 1.0):
        raise SchemaError("confidence and threshold must be in [0, 1]")
    retrieve = confidence < threshold
    return {
        "retrieve": retrieve,
        "confidence": round(confidence, 4),
        "ok": True,
        "note": "selfrag selfrag_need_retrieve",
    }


def selfrag_relevance_critique(*, relevant: bool) -> dict[str, Any]:
    """Critique: is the retrieved passage relevant?"""
    return {
        "relevant": relevant,
        "ok": True,
        "note": "selfrag selfrag_relevance_critique",
    }


def selfrag_support_critique(*, supported: bool) -> dict[str, Any]:
    """Critique: does the passage support the generation?"""
    return {
        "supported": supported,
        "ok": True,
        "note": "selfrag selfrag_support_critique",
    }


def selfrag_utility_critique(*, utility: float) -> dict[str, Any]:
    """Critique overall utility of a candidate response."""
    if not (0.0 <= utility <= 1.0):
        raise SchemaError("utility must be in [0, 1]")
    return {
        "utility": round(utility, 4),
        "ok": True,
        "note": "selfrag selfrag_utility_critique",
    }


def selfrag_select_best(*, scores: int, pick: int) -> dict[str, Any]:
    """Select best candidate among scored continuations."""
    if scores < 1 or pick < 0:
        raise SchemaError("scores >= 1 and pick >= 0")
    if pick >= scores:
        raise SchemaError("pick must be < scores")
    return {
        "pick": pick,
        "scores": scores,
        "ok": True,
        "note": "selfrag selfrag_select_best",
    }


def selfrag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Decide → critique → select → generate."""
    order = ("decide", "critique", "select", "generate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "decide"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "selfrag selfrag_loop_plan",
    }
