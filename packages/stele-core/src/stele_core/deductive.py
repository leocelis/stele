"""Deductive Verification / Natural Program proxies (stdlib; no LLM).

Shaped by Deductive Verification of CoT (arXiv:2306.03872): Natural
Program steps, premise-scoped verify, unanimity gate. Proxies only —
≠ Faithful CoT / Reflexion.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dv_natural_program(*, claim: str, steps: int) -> dict[str, Any]:
    """Emit a Natural Program-shaped deductive chain."""
    c = claim.strip()
    if not c:
        raise SchemaError("claim required")
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"c": c, "s": steps}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "program_id": pid,
        "steps": steps,
        "ok": True,
        "note": "deductive dv_natural_program",
    }


def dv_step_verify(*, program_id: str, step: int) -> dict[str, Any]:
    """Verify one step with only its necessary premises (proxy)."""
    pid = program_id.strip()
    if not pid:
        raise SchemaError("program_id required")
    if step < 0:
        raise SchemaError("step must be >= 0")
    vid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": step}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "verify_id": vid,
        "step": step,
        "ok": True,
        "note": "deductive dv_step_verify",
    }


def dv_premise_scope(*, premises: int) -> dict[str, Any]:
    """Count premises in scope for a verification subprocess."""
    if premises < 0:
        raise SchemaError("premises must be >= 0")
    return {
        "premises": premises,
        "ok": True,
        "note": "deductive dv_premise_scope",
    }


def dv_unanimity(*, all_pass: bool) -> dict[str, Any]:
    """Require unanimity across step verifications (report-only)."""
    return {
        "all_pass": all_pass,
        "apply": False,
        "ok": True,
        "note": "deductive dv_unanimity",
    }


def dv_ground(*, grounded: bool) -> dict[str, Any]:
    """Flag that later steps are grounded on prior verified steps."""
    return {
        "grounded": grounded,
        "ok": True,
        "note": "deductive dv_ground",
    }


def dv_loop_plan(*, phase: str) -> dict[str, Any]:
    """Program → verify → unanimity → ground."""
    order = ("program", "verify", "unanimity", "ground")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "program"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "deductive dv_loop_plan",
    }
