"""Step-Back Prompting proxies (stdlib; no LLM).

Shaped by Step-Back Prompting (arXiv:2310.06117): abstract to
principles, then reason with them. Proxies only — ≠ Least-to-Most.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sb_abstract(*, instance: str) -> dict[str, Any]:
    """Step back: abstract high-level concepts from a detailed instance."""
    i = instance.strip()
    if not i:
        raise SchemaError("instance required")
    aid = hashlib.sha256(
        canonical_dumps({"i": i}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "concept_id": aid,
        "ok": True,
        "note": "stepback sb_abstract",
    }


def sb_principle(*, concept_id: str, principle: str) -> dict[str, Any]:
    """Derive a first principle from the abstraction."""
    cid = concept_id.strip()
    p = principle.strip()
    if not cid or not p:
        raise SchemaError("concept_id and principle required")
    pid = hashlib.sha256(
        canonical_dumps({"c": cid, "p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "principle_id": pid,
        "ok": True,
        "note": "stepback sb_principle",
    }


def sb_reason(*, principle_id: str) -> dict[str, Any]:
    """Reason toward the solution guided by principles."""
    pid = principle_id.strip()
    if not pid:
        raise SchemaError("principle_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": rid,
        "ok": True,
        "note": "stepback sb_reason",
    }


def sb_path(*, correct_path: bool) -> dict[str, Any]:
    """Flag improved ability to follow a correct reasoning path."""
    return {
        "correct_path": correct_path,
        "ok": True,
        "note": "stepback sb_path",
    }


def sb_detail_trap(*, escaped: bool) -> dict[str, Any]:
    """Flag escaping detail overload via abstraction (report-only)."""
    return {
        "escaped": escaped,
        "apply": False,
        "ok": True,
        "note": "stepback sb_detail_trap",
    }


def sb_loop_plan(*, phase: str) -> dict[str, Any]:
    """Abstract → principle → reason → path."""
    order = ("abstract", "principle", "reason", "path")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "abstract"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "stepback sb_loop_plan",
    }
