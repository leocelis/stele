"""Progressive-Hint Prompting proxies (stdlib; no LLM).

Shaped by Progressive-Hint Prompting (arXiv:2304.09797): base answer,
emit hint, re-ask with hints, stop on stable answer. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def php_base_answer(*, question: str) -> dict[str, Any]:
    """Generate an initial base answer."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    aid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": aid,
        "ok": True,
        "note": "php php_base_answer",
    }


def php_emit_hint(*, answer_id: str, hint: str) -> dict[str, Any]:
    """Turn a prior answer into a progressive hint."""
    aid = answer_id.strip()
    h = hint.strip()
    if not aid or not h:
        raise SchemaError("answer_id and hint required")
    hid = hashlib.sha256(
        canonical_dumps({"a": aid, "h": h}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hint_id": hid,
        "ok": True,
        "note": "php php_emit_hint",
    }


def php_reask(*, hints: int) -> dict[str, Any]:
    """Re-ask with accumulated answer hints."""
    if hints < 0:
        raise SchemaError("hints must be >= 0")
    return {
        "hints": hints,
        "ok": True,
        "note": "php php_reask",
    }


def php_stable_stop(*, same_twice: bool) -> dict[str, Any]:
    """Stop when two consecutive answers match (report-only)."""
    return {
        "stop": same_twice,
        "apply": False,
        "ok": True,
        "note": "php php_stable_stop",
    }


def php_combine_sc(*, reduced_paths: bool) -> dict[str, Any]:
    """Flag PHP combining with self-consistency path reduction."""
    return {
        "reduced_paths": reduced_paths,
        "ok": True,
        "note": "php php_combine_sc",
    }


def php_loop_plan(*, phase: str) -> dict[str, Any]:
    """Base → hint → reask → stop."""
    order = ("base", "hint", "reask", "stop")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "base"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "php php_loop_plan",
    }
