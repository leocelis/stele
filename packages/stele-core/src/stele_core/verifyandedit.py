"""Verify-and-Edit proxies (stdlib; no LLM / no retrieval).

Shaped by Verify-and-Edit (arXiv:2305.03268): detect uncertain CoT,
search supporting facts, edit rationale. Proxies only.

Prefix ``ved_*`` — not CoVe (``cove_*``) / CRITIC / Deductive Verification.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ved_uncertain(*, consistency: int) -> dict[str, Any]:
    """Flag uncertain prediction from low self-consistency (0–100)."""
    if consistency < 0 or consistency > 100:
        raise SchemaError("consistency must be 0..100")
    return {
        "consistency": consistency,
        "uncertain": consistency < 50,
        "ok": True,
        "note": "ved ved_uncertain",
    }


def ved_search(*, query: str) -> dict[str, Any]:
    """Search supporting facts for uncertain rationale (proxy id)."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    sid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fact_id": sid,
        "ok": True,
        "note": "ved ved_search",
    }


def ved_edit(*, fact_id: str, rationale: str) -> dict[str, Any]:
    """Edit the CoT rationale using retrieved facts."""
    fid = fact_id.strip()
    r = rationale.strip()
    if not fid or not r:
        raise SchemaError("fact_id and rationale required")
    eid = hashlib.sha256(
        canonical_dumps({"f": fid, "r": r}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edit_id": eid,
        "ok": True,
        "note": "ved ved_edit",
    }


def ved_predict(*, edit_id: str) -> dict[str, Any]:
    """Predict final answer from the edited rationale."""
    eid = edit_id.strip()
    if not eid:
        raise SchemaError("edit_id required")
    pid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pred_id": pid,
        "ok": True,
        "note": "ved ved_predict",
    }


def ved_knowledge(*, enhanced: bool) -> dict[str, Any]:
    """Flag knowledge-enhanced CoT (report-only)."""
    return {
        "enhanced": enhanced,
        "apply": False,
        "ok": True,
        "note": "ved ved_knowledge",
    }


def ved_loop_plan(*, phase: str) -> dict[str, Any]:
    """Uncertain → search → edit → predict."""
    order = ("uncertain", "search", "edit", "predict")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "uncertain"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ved ved_loop_plan",
    }
