"""FLARE-shaped forward-looking active retrieval (stdlib; no LLM).

Shaped by FLARE / Active RAG (arXiv:2305.06983): anticipate upcoming
sentence, detect low-confidence tokens, retrieve for regen, regenerate.
Proxies only — not live LM confidence scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def flare_anticipate_sentence(*, context: str) -> dict[str, Any]:
    """Predict upcoming sentence id from context (proxy)."""
    c = context.strip()
    if not c:
        raise SchemaError("context required")
    sent_id = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sent_id": sent_id,
        "ok": True,
        "note": "flare flare_anticipate_sentence",
    }


def flare_low_confidence(*, confidence: float, threshold: float = 0.4) -> dict[str, Any]:
    """Detect low-confidence tokens that should trigger retrieval."""
    if not (0.0 <= confidence <= 1.0) or not (0.0 <= threshold <= 1.0):
        raise SchemaError("confidence and threshold must be in [0, 1]")
    return {
        "low": confidence < threshold,
        "confidence": round(confidence, 4),
        "ok": True,
        "note": "flare flare_low_confidence",
    }


def flare_retrieve_for_regen(*, query: str, k: int = 3) -> dict[str, Any]:
    """Retrieve docs using anticipated sentence as query."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "ok": True,
        "note": "flare flare_retrieve_for_regen",
    }


def flare_regenerate_sentence(*, sent_id: str, with_docs: bool) -> dict[str, Any]:
    """Regenerate sentence after retrieval (report-only apply)."""
    sid = sent_id.strip()
    if not sid:
        raise SchemaError("sent_id required")
    return {
        "sent_id": sid[:64],
        "regenerated": with_docs,
        "apply": False,
        "ok": True,
        "note": "flare flare_regenerate_sentence",
    }


def flare_active_step(*, step: int, retrieved: bool) -> dict[str, Any]:
    """Record one active retrieval step in long-form generation."""
    if step < 0:
        raise SchemaError("step must be >= 0")
    return {
        "step": step,
        "retrieved": retrieved,
        "ok": True,
        "note": "flare flare_active_step",
    }


def flare_loop_plan(*, phase: str) -> dict[str, Any]:
    """Anticipate → confidence → retrieve → regenerate."""
    order = ("anticipate", "confidence", "retrieve", "regenerate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "anticipate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "flare flare_loop_plan",
    }
