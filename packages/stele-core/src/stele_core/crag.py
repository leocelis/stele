"""CRAG-shaped corrective retrieval (stdlib; no LLM / no web).

Shaped by Corrective Retrieval Augmented Generation (arXiv:2401.15884):
evaluate retrieval confidence → Correct / Incorrect / Ambiguous;
decompose-then-recompose; web fallback as report-only plan.
Proxies only — not CRAG T5 evaluator or live search.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError


def crag_evaluate_retrieval(*, confidence: float) -> dict[str, Any]:
    """Map retrieval confidence to Correct / Incorrect / Ambiguous."""
    if not (0.0 <= confidence <= 1.0):
        raise SchemaError("confidence must be in [0, 1]")
    if confidence >= 0.7:
        action = "Correct"
    elif confidence < 0.3:
        action = "Incorrect"
    else:
        action = "Ambiguous"
    return {
        "action": action,
        "confidence": round(confidence, 4),
        "ok": True,
        "note": "crag crag_evaluate_retrieval",
    }


def crag_correct_refine(*, chunks: int) -> dict[str, Any]:
    """Decompose-then-recompose refine for Correct action."""
    if chunks < 0:
        raise SchemaError("chunks must be >= 0")
    return {
        "chunks": chunks,
        "refined": chunks >= 1,
        "ok": True,
        "note": "crag crag_correct_refine",
    }


def crag_web_fallback_plan(*, trigger: bool) -> dict[str, Any]:
    """Plan web search fallback (report-only; no live network)."""
    return {
        "trigger": trigger,
        "apply": False,
        "ok": True,
        "note": "crag crag_web_fallback_plan",
    }


def crag_ambiguous_blend(*, local_hits: int, web_hits: int) -> dict[str, Any]:
    """Blend refined local + planned web hits for Ambiguous."""
    if local_hits < 0 or web_hits < 0:
        raise SchemaError("local_hits and web_hits must be >= 0")
    return {
        "total": local_hits + web_hits,
        "ok": True,
        "note": "crag crag_ambiguous_blend",
    }


def crag_action_select(*, action: str) -> dict[str, Any]:
    """Validate and echo corrective action."""
    allowed = ("Correct", "Incorrect", "Ambiguous")
    if action not in allowed:
        raise SchemaError(f"action must be one of {list(allowed)}")
    return {
        "action": action,
        "ok": True,
        "note": "crag crag_action_select",
    }


def crag_loop_plan(*, phase: str) -> dict[str, Any]:
    """Evaluate → refine → fallback → blend."""
    order = ("evaluate", "refine", "fallback", "blend")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "evaluate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "crag crag_loop_plan",
    }
