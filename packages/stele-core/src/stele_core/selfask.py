"""Self-Ask-shaped follow-up question pipeline (stdlib; no LLM).

Shaped by Self-Ask (Press et al., arXiv:2210.04695): ask follow-ups,
intercept search, compose final answer. Proxies only — not Google Search.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def selfask_followup(*, question: str, hop: int = 0) -> dict[str, Any]:
    """Emit a follow-up question for missing information."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    if hop < 0:
        raise SchemaError("hop must be >= 0")
    fid = hashlib.sha256(
        canonical_dumps({"q": q, "h": hop}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "followup_id": fid,
        "hop": hop,
        "ok": True,
        "note": "selfask selfask_followup",
    }


def selfask_search_intercept(*, followup_id: str, k: int = 3) -> dict[str, Any]:
    """Intercept follow-up and search (proxy hits)."""
    fid = followup_id.strip()
    if not fid:
        raise SchemaError("followup_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    return {
        "hits": k,
        "followup_id": fid[:64],
        "ok": True,
        "note": "selfask selfask_search_intercept",
    }


def selfask_compose_answer(*, followups: int) -> dict[str, Any]:
    """Compose final answer after follow-up searches."""
    if followups < 0:
        raise SchemaError("followups must be >= 0")
    return {
        "followups": followups,
        "composed": True,
        "ok": True,
        "note": "selfask selfask_compose_answer",
    }


def selfask_stop(*, enough: bool) -> dict[str, Any]:
    """Stop asking follow-ups (report-only)."""
    return {
        "stop": enough,
        "apply": False,
        "ok": True,
        "note": "selfask selfask_stop",
    }


def selfask_demo_prompt(*, demos: int) -> dict[str, Any]:
    """Count in-context Self-Ask demonstrations."""
    if demos < 0:
        raise SchemaError("demos must be >= 0")
    return {
        "demos": demos,
        "ok": True,
        "note": "selfask selfask_demo_prompt",
    }


def selfask_loop_plan(*, phase: str) -> dict[str, Any]:
    """Followup → search → compose → stop."""
    order = ("followup", "search", "compose", "stop")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "followup"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "selfask selfask_loop_plan",
    }
