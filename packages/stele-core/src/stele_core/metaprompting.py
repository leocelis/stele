"""Meta-Prompting-shaped conductor+experts (stdlib; no LLM).

Shaped by Meta-Prompting (arXiv:2401.12954): break task, assign experts,
oversee history, verify. Proxies only — same LM as conductor+experts.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mp_break_task(*, query: str, pieces: int) -> dict[str, Any]:
    """Break a complex query into manageable pieces."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if pieces < 1:
        raise SchemaError("pieces must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"q": q, "p": pieces}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "break_id": bid,
        "pieces": pieces,
        "ok": True,
        "note": "metaprompt mp_break_task",
    }


def mp_assign_expert(*, piece_idx: int, expert: str) -> dict[str, Any]:
    """Assign a piece to a specialized expert persona."""
    if piece_idx < 0:
        raise SchemaError("piece_idx must be >= 0")
    e = expert.strip()
    if not e:
        raise SchemaError("expert required")
    eid = hashlib.sha256(
        canonical_dumps({"i": piece_idx, "e": e}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "assign_id": eid,
        "piece_idx": piece_idx,
        "expert": e[:64],
        "ok": True,
        "note": "metaprompt mp_assign_expert",
    }


def mp_oversee(*, messages: int) -> dict[str, Any]:
    """Oversee conductor/expert message history length."""
    if messages < 0:
        raise SchemaError("messages must be >= 0")
    return {
        "messages": messages,
        "ok": True,
        "note": "metaprompt mp_oversee",
    }


def mp_verify(*, claim: str) -> dict[str, Any]:
    """Critical verification step (report-only)."""
    c = claim.strip()
    if not c:
        raise SchemaError("claim required")
    vid = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "verify_id": vid,
        "apply": False,
        "ok": True,
        "note": "metaprompt mp_verify",
    }


def mp_task_agnostic(*, scaffold: bool) -> dict[str, Any]:
    """Flag that scaffolding is task-agnostic."""
    return {
        "scaffold": scaffold,
        "ok": True,
        "note": "metaprompt mp_task_agnostic",
    }


def mp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Break → assign → oversee → verify."""
    order = ("break", "assign", "oversee", "verify")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "break"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "metaprompt mp_loop_plan",
    }
