"""Thread of Thought proxies (stdlib; no LLM).

Shaped by Thread of Thought (arXiv:2311.08734): segment chaotic
context → analyze → select pertinent → synthesize. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def thot_segment(*, context: str, pieces: int) -> dict[str, Any]:
    """Segment chaotic/extended context into manageable pieces."""
    c = context.strip()
    if not c:
        raise SchemaError("context required")
    if pieces < 1:
        raise SchemaError("pieces must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"c": c, "p": pieces}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "segment_id": sid,
        "pieces": pieces,
        "ok": True,
        "note": "thot thot_segment",
    }


def thot_analyze(*, segment_id: str) -> dict[str, Any]:
    """Analyze each segment for pertinent information."""
    sid = segment_id.strip()
    if not sid:
        raise SchemaError("segment_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "analyze_id": aid,
        "ok": True,
        "note": "thot thot_analyze",
    }


def thot_select(*, analyze_id: str) -> dict[str, Any]:
    """Select pertinent details; ignore distractors."""
    aid = analyze_id.strip()
    if not aid:
        raise SchemaError("analyze_id required")
    tid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "select_id": tid,
        "ok": True,
        "note": "thot thot_select",
    }


def thot_synthesize(*, select_id: str) -> dict[str, Any]:
    """Synthesize a final conclusion from selected threads."""
    tid = select_id.strip()
    if not tid:
        raise SchemaError("select_id required")
    oid = hashlib.sha256(
        canonical_dumps({"s": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "synth_id": oid,
        "ok": True,
        "note": "thot thot_synthesize",
    }


def thot_plug(*, plug_and_play: bool) -> dict[str, Any]:
    """Flag plug-and-play composition with other prompts (report-only)."""
    return {
        "plug_and_play": plug_and_play,
        "apply": False,
        "ok": True,
        "note": "thot thot_plug",
    }


def thot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Segment → analyze → select → synthesize."""
    order = ("segment", "analyze", "select", "synthesize")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "segment"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "thot thot_loop_plan",
    }
