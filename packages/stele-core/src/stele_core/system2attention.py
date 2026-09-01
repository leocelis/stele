"""System 2 Attention proxies (stdlib; no LLM).

Shaped by System 2 Attention (arXiv:2311.11829): regenerate context
to relevant portions, then attend/respond. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def s2a_regenerate(*, context: str) -> dict[str, Any]:
    """Regenerate input context keeping only relevant portions."""
    c = context.strip()
    if not c:
        raise SchemaError("context required")
    rid = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "regen_id": rid,
        "ok": True,
        "note": "s2a s2a_regenerate",
    }


def s2a_attend(*, regen_id: str) -> dict[str, Any]:
    """Attend to the regenerated context."""
    rid = regen_id.strip()
    if not rid:
        raise SchemaError("regen_id required")
    aid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "attend_id": aid,
        "ok": True,
        "note": "s2a s2a_attend",
    }


def s2a_respond(*, attend_id: str) -> dict[str, Any]:
    """Elicit final response from refined attention."""
    aid = attend_id.strip()
    if not aid:
        raise SchemaError("attend_id required")
    oid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "response_id": oid,
        "ok": True,
        "note": "s2a s2a_respond",
    }


def s2a_factuality(*, score: int) -> dict[str, Any]:
    """Factuality score after S2A (0–100)."""
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    return {
        "score": score,
        "ok": True,
        "note": "s2a s2a_factuality",
    }


def s2a_sycophancy(*, reduced: bool) -> dict[str, Any]:
    """Flag reduced sycophancy from irrelevant opinion (report-only)."""
    return {
        "reduced": reduced,
        "apply": False,
        "ok": True,
        "note": "s2a s2a_sycophancy",
    }


def s2a_loop_plan(*, phase: str) -> dict[str, Any]:
    """Regenerate → attend → respond → factuality."""
    order = ("regenerate", "attend", "respond", "factuality")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "regenerate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "s2a s2a_loop_plan",
    }
