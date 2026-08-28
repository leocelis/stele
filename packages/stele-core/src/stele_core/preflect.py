"""PreFlect-shaped prospective reflection (stdlib; no LLM).

Shaped by PreFlect (arXiv:2602.07187): distill planning errors,
critique plans before execution, revise, dynamic re-plan on deviation.
Proxies only — not PreFlect paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def distill_planning_error(
    *,
    error_id: str,
    pattern: str,
    success_hint: str = "",
    failure_hint: str = "",
) -> dict[str, Any]:
    """Offline: capture a recurring planning-level failure mode."""
    if not error_id.strip() or not pattern.strip():
        raise SchemaError("error_id and pattern required")
    eid = hashlib.sha256(
        canonical_dumps({"id": error_id.strip(), "p": pattern.strip()}).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return {
        "error_key": eid,
        "error_id": error_id.strip()[:64],
        "pattern": pattern.strip()[:200],
        "success_hint": success_hint.strip()[:120],
        "failure_hint": failure_hint.strip()[:120],
        "ok": True,
        "note": "preflect distill_planning_error",
    }


def prospective_critique_plan(
    *,
    plan_steps: Sequence[str],
    planning_errors: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    """Pre-execution: match plan text against distilled planning errors."""
    if not isinstance(plan_steps, Sequence) or isinstance(plan_steps, (str, bytes)):
        raise SchemaError("plan_steps sequence required")
    steps = [str(s).strip().lower() for s in plan_steps if str(s).strip()]
    if not steps:
        raise SchemaError("plan_steps required")
    hits: list[dict[str, Any]] = []
    for err in planning_errors:
        if not isinstance(err, dict):
            continue
        pat = str(err.get("pattern") or "").strip().lower()
        if not pat:
            continue
        tokens = [t for t in pat.split() if len(t) > 2][:6]
        if tokens and any(any(t in step for t in tokens) for step in steps):
            hits.append(
                {
                    "error_id": err.get("error_id") or err.get("error_key"),
                    "pattern": pat[:80],
                }
            )
    return {
        "critical_hits": hits,
        "hit_count": len(hits),
        "needs_revise": len(hits) > 0,
        "apply": False,
        "ok": True,
        "note": "preflect prospective_critique_plan",
    }


def revise_plan_proposal(
    *,
    original_steps: Sequence[str],
    avoid_patterns: Sequence[str],
    insert_guard: str = "verify precondition",
) -> dict[str, Any]:
    """Propose a revised plan that inserts a guard and drops matching steps."""
    if not isinstance(original_steps, Sequence) or isinstance(
        original_steps, (str, bytes)
    ):
        raise SchemaError("original_steps sequence required")
    steps = [str(s).strip() for s in original_steps if str(s).strip()]
    if not steps:
        raise SchemaError("original_steps required")
    avoid = [str(a).strip().lower() for a in avoid_patterns if str(a).strip()]
    revised: list[str] = []
    dropped = 0
    for s in steps:
        low = s.lower()
        if avoid and any(a in low for a in avoid):
            dropped += 1
            continue
        revised.append(s)
    if insert_guard.strip():
        revised.insert(0, insert_guard.strip()[:80])
    return {
        "revised_steps": revised,
        "dropped": dropped,
        "changed": dropped > 0 or bool(insert_guard.strip()),
        "apply": False,
        "ok": True,
        "note": "preflect revise_plan_proposal",
    }


def replan_on_deviation(
    *,
    expected_observation: str,
    actual_observation: str,
    remaining_steps: int,
) -> dict[str, Any]:
    """Execution-time: trigger re-plan when observation diverges."""
    if remaining_steps < 0:
        raise SchemaError("remaining_steps must be >= 0")
    exp = expected_observation.strip().lower()
    act = actual_observation.strip().lower()
    if not exp or not act:
        raise SchemaError("observations required")
    exp_tok = set(exp.split())
    act_tok = set(act.split())
    if not exp_tok:
        overlap = 0.0
    else:
        overlap = len(exp_tok & act_tok) / len(exp_tok)
    deviate = overlap < 0.4
    return {
        "deviation": deviate,
        "overlap": round(overlap, 4),
        "trigger_replan": deviate and remaining_steps > 0,
        "reinvoke_prospective": deviate and remaining_steps > 0,
        "apply": False,
        "ok": True,
        "note": "preflect replan_on_deviation",
    }


def preflect_before_execute_gate(
    *,
    critique_needs_revise: bool,
    revised_ready: bool,
) -> dict[str, Any]:
    """Block execute until prospective revise completes when needed."""
    if critique_needs_revise and not revised_ready:
        return {
            "allowed": False,
            "reason": "revise_required_before_execute",
            "ok": True,
            "note": "preflect preflect_before_execute_gate",
        }
    return {
        "allowed": True,
        "reason": "clear",
        "ok": True,
        "note": "preflect preflect_before_execute_gate",
    }
