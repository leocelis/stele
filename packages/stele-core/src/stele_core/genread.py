"""GenRead-shaped generate-then-read (stdlib; no LLM).

Shaped by GenRead (arXiv:2302.08468): generate context from parametric
memory instead of (or before) retrieve; optional ground; answer; hybrid.
Proxies only — not live LLM context generation.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def genread_generate_context(*, question: str) -> dict[str, Any]:
    """Generate a contextual document from the question (parametric)."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    ctx_id = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ctx_id": ctx_id,
        "ok": True,
        "note": "genread genread_generate_context",
    }


def genread_ground_optional(*, ctx_id: str, use_retriever: bool) -> dict[str, Any]:
    """Optionally ground generated context with a retriever."""
    cid = ctx_id.strip()
    if not cid:
        raise SchemaError("ctx_id required")
    return {
        "ctx_id": cid[:64],
        "grounded": use_retriever,
        "ok": True,
        "note": "genread genread_ground_optional",
    }


def genread_answer(*, ctx_id: str) -> dict[str, Any]:
    """Answer using generated (and optional grounded) context."""
    cid = ctx_id.strip()
    if not cid:
        raise SchemaError("ctx_id required")
    return {
        "ctx_id": cid[:64],
        "answered": True,
        "ok": True,
        "note": "genread genread_answer",
    }


def genread_compare_retrieve(*, gen_hits: int, retrieve_hits: int) -> dict[str, Any]:
    """Compare generate-path vs retrieve-then-read hit counts."""
    if gen_hits < 0 or retrieve_hits < 0:
        raise SchemaError("hit counts must be >= 0")
    return {
        "prefer_generate": gen_hits >= retrieve_hits,
        "ok": True,
        "note": "genread genread_compare_retrieve",
    }


def genread_hybrid(*, generate: bool, retrieve: bool) -> dict[str, Any]:
    """Hybrid: use both generated and retrieved contexts."""
    return {
        "hybrid": generate and retrieve,
        "ok": True,
        "note": "genread genread_hybrid",
    }


def genread_loop_plan(*, phase: str) -> dict[str, Any]:
    """Generate → ground → answer → compare."""
    order = ("generate", "ground", "answer", "compare")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "generate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "genread genread_loop_plan",
    }
