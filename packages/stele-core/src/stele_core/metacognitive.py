"""Metacognitive Prompting proxies (stdlib; no LLM).

Shaped by Metacognitive Prompting (arXiv:2308.05342): introspective
recognition → interpret → re-evaluate → confidence. Proxies only.

Prefix ``mcp_*`` — not Meta-Prompting (``mp_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mcp_recognize(*, knowledge: str) -> dict[str, Any]:
    """Recognition of knowledge base for the task."""
    k = knowledge.strip()
    if not k:
        raise SchemaError("knowledge required")
    kid = hashlib.sha256(
        canonical_dumps({"k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "recognize_id": kid,
        "ok": True,
        "note": "metacognitive mcp_recognize",
    }


def mcp_interpret(*, recognize_id: str) -> dict[str, Any]:
    """Assessment of initial interpretation."""
    rid = recognize_id.strip()
    if not rid:
        raise SchemaError("recognize_id required")
    iid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "interpret_id": iid,
        "ok": True,
        "note": "metacognitive mcp_interpret",
    }


def mcp_reevaluate(*, interpret_id: str) -> dict[str, Any]:
    """Re-evaluation of the initial assessment."""
    iid = interpret_id.strip()
    if not iid:
        raise SchemaError("interpret_id required")
    eid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reeval_id": eid,
        "ok": True,
        "note": "metacognitive mcp_reevaluate",
    }


def mcp_confidence(*, score: int) -> dict[str, Any]:
    """Confidence score for the justified decision (0–100)."""
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    return {
        "score": score,
        "ok": True,
        "note": "metacognitive mcp_confidence",
    }


def mcp_justify(*, justified: bool) -> dict[str, Any]:
    """Flag decision justification (report-only)."""
    return {
        "justified": justified,
        "apply": False,
        "ok": True,
        "note": "metacognitive mcp_justify",
    }


def mcp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Recognize → interpret → reevaluate → confidence."""
    order = ("recognize", "interpret", "reevaluate", "confidence")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "recognize"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "metacognitive mcp_loop_plan",
    }
