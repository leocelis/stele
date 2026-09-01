"""Chain-of-Verification proxies (stdlib; no LLM).

Shaped by CoVe (arXiv:2309.11495): draft → plan verification questions
→ answer independently → verified response. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cove_draft(*, claim: str) -> dict[str, Any]:
    """Draft an initial response that may contain hallucinations."""
    c = claim.strip()
    if not c:
        raise SchemaError("claim required")
    did = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "draft_id": did,
        "ok": True,
        "note": "cove cove_draft",
    }


def cove_plan(*, draft_id: str) -> dict[str, Any]:
    """Plan verification questions to fact-check the draft."""
    did = draft_id.strip()
    if not did:
        raise SchemaError("draft_id required")
    pid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "ok": True,
        "note": "cove cove_plan",
    }


def cove_answer(*, plan_id: str) -> dict[str, Any]:
    """Answer verification questions independently (unbiased)."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    aid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "verify_id": aid,
        "ok": True,
        "note": "cove cove_answer",
    }


def cove_final(*, verify_id: str) -> dict[str, Any]:
    """Generate the final verified response."""
    vid = verify_id.strip()
    if not vid:
        raise SchemaError("verify_id required")
    fid = hashlib.sha256(
        canonical_dumps({"v": vid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "final_id": fid,
        "ok": True,
        "note": "cove cove_final",
    }


def cove_hallucination(*, reduced: bool) -> dict[str, Any]:
    """Flag reduced hallucination after CoVe (report-only)."""
    return {
        "reduced": reduced,
        "apply": False,
        "ok": True,
        "note": "cove cove_hallucination",
    }


def cove_loop_plan(*, phase: str) -> dict[str, Any]:
    """Draft → plan → answer → final."""
    order = ("draft", "plan", "answer", "final")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "draft"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cove cove_loop_plan",
    }
