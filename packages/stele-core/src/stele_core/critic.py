"""CRITIC-shaped tool-interactive self-correct (stdlib; no LLM).

Shaped by CRITIC (arXiv:2305.11738): draft, tool critique, revise,
iterate verify→correct. Proxies only — ≠ Reflexion.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def critic_draft(*, question: str) -> dict[str, Any]:
    """Emit an initial draft answer."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    did = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "draft_id": did,
        "ok": True,
        "note": "critic critic_draft",
    }


def critic_tool_check(*, draft_id: str, tool: str) -> dict[str, Any]:
    """Interact with an external tool to critique the draft."""
    did = draft_id.strip()
    t = tool.strip()
    if not did or not t:
        raise SchemaError("draft_id and tool required")
    cid = hashlib.sha256(
        canonical_dumps({"d": did, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "critique_id": cid,
        "ok": True,
        "note": "critic critic_tool_check",
    }


def critic_revise(*, draft_id: str, critique_id: str) -> dict[str, Any]:
    """Revise draft from tool critiques."""
    did = draft_id.strip()
    cid = critique_id.strip()
    if not did or not cid:
        raise SchemaError("draft_id and critique_id required")
    rid = hashlib.sha256(
        canonical_dumps({"d": did, "c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "revised_id": rid,
        "ok": True,
        "note": "critic critic_revise",
    }


def critic_iterate(*, rounds: int) -> dict[str, Any]:
    """Count verify→correct iteration rounds."""
    if rounds < 0:
        raise SchemaError("rounds must be >= 0")
    return {
        "rounds": rounds,
        "ok": True,
        "note": "critic critic_iterate",
    }


def critic_stop(*, satisfied: bool) -> dict[str, Any]:
    """Stop when critiques are satisfied (report-only)."""
    return {
        "satisfied": satisfied,
        "apply": False,
        "ok": True,
        "note": "critic critic_stop",
    }


def critic_loop_plan(*, phase: str) -> dict[str, Any]:
    """Draft → check → revise → stop."""
    order = ("draft", "check", "revise", "stop")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "draft"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "critic critic_loop_plan",
    }
