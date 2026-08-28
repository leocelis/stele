"""Cumulative-Reasoning-shaped proposer/verifier/reporter (stdlib; no LLM).

Shaped by Cumulative Reasoning (arXiv:2308.04371): propose steps, verify,
accumulate, report. Proxies only — not Zhang et al. CR runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cr_propose(*, step: str) -> dict[str, Any]:
    """Proposer emits a candidate reasoning step."""
    s = step.strip()
    if not s:
        raise SchemaError("step required")
    pid = hashlib.sha256(
        canonical_dumps({"s": s}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proposal_id": pid,
        "ok": True,
        "note": "cr cr_propose",
    }


def cr_verify(*, proposal_id: str, valid: bool) -> dict[str, Any]:
    """Verifier accepts or rejects a proposal (report-only)."""
    pid = proposal_id.strip()
    if not pid:
        raise SchemaError("proposal_id required")
    return {
        "proposal_id": pid[:64],
        "valid": valid,
        "apply": False,
        "ok": True,
        "note": "cr cr_verify",
    }


def cr_accumulate(*, accepted: int) -> dict[str, Any]:
    """Accumulate validated steps into working memory."""
    if accepted < 0:
        raise SchemaError("accepted must be >= 0")
    return {
        "accepted": accepted,
        "ok": True,
        "note": "cr cr_accumulate",
    }


def cr_report(*, steps: int) -> dict[str, Any]:
    """Reporter compiles accumulated steps into a final answer."""
    if steps < 0:
        raise SchemaError("steps must be >= 0")
    return {
        "steps": steps,
        "reported": True,
        "ok": True,
        "note": "cr cr_report",
    }


def cr_roles(*, roles: int = 3) -> dict[str, Any]:
    """Count specialized roles (proposer/verifier/reporter)."""
    if roles < 1:
        raise SchemaError("roles must be >= 1")
    return {
        "roles": roles,
        "ok": True,
        "note": "cr cr_roles",
    }


def cr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Propose → verify → accumulate → report."""
    order = ("propose", "verify", "accumulate", "report")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cr cr_loop_plan",
    }
