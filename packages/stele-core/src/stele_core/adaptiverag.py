"""Adaptive-RAG-shaped complexity-routed retrieval (stdlib; no LLM).

Shaped by Adaptive-RAG (arXiv:2403.14403): classify query complexity,
select no-retrieval / single-step / multi-step strategy.
Proxies only — not the paper's trained complexity classifier.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError

_STRATEGIES = ("no_retrieval", "single_step", "multi_step")


def adaptiverag_classify_complexity(*, hops: int) -> dict[str, Any]:
    """Map hop count to complexity level 0/1/2."""
    if hops < 0:
        raise SchemaError("hops must be >= 0")
    if hops == 0:
        level = 0
    elif hops == 1:
        level = 1
    else:
        level = 2
    return {
        "level": level,
        "hops": hops,
        "ok": True,
        "note": "adaptiverag adaptiverag_classify_complexity",
    }


def adaptiverag_select_strategy(*, level: int) -> dict[str, Any]:
    """Select strategy from complexity level."""
    if level not in (0, 1, 2):
        raise SchemaError("level must be 0, 1, or 2")
    return {
        "strategy": _STRATEGIES[level],
        "level": level,
        "ok": True,
        "note": "adaptiverag adaptiverag_select_strategy",
    }


def adaptiverag_no_retrieve(*, parametric_ok: bool) -> dict[str, Any]:
    """No-retrieval path for simple queries."""
    return {
        "retrieve": False,
        "parametric_ok": parametric_ok,
        "ok": True,
        "note": "adaptiverag adaptiverag_no_retrieve",
    }


def adaptiverag_single_step(*, hits: int) -> dict[str, Any]:
    """Single-step retrieve-and-generate."""
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "hits": hits,
        "ok": True,
        "note": "adaptiverag adaptiverag_single_step",
    }


def adaptiverag_multi_step(*, steps: int) -> dict[str, Any]:
    """Multi-step iterative retrieval for complex queries."""
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    return {
        "steps": steps,
        "ok": True,
        "note": "adaptiverag adaptiverag_multi_step",
    }


def adaptiverag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Classify → select → execute → adapt."""
    order = ("classify", "select", "execute", "adapt")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "classify"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "adaptiverag adaptiverag_loop_plan",
    }
