"""Plan-and-Solve-shaped zero-shot CoT (stdlib; no LLM).

Shaped by Plan-and-Solve (arXiv:2305.04091): devise plan, execute
subtasks, PS+ variable extract. Proxies only — ≠ PlanRAG.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ps_devise_plan(*, problem: str, subtasks: int) -> dict[str, Any]:
    """Devise a plan that splits the problem into subtasks."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    if subtasks < 1:
        raise SchemaError("subtasks must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"p": p, "n": subtasks}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "subtasks": subtasks,
        "ok": True,
        "note": "planandsolve ps_devise_plan",
    }


def ps_execute(*, plan_id: str, step: int) -> dict[str, Any]:
    """Execute one planned subtask by index."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    if step < 0:
        raise SchemaError("step must be >= 0")
    eid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": step}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "exec_id": eid,
        "step": step,
        "ok": True,
        "note": "planandsolve ps_execute",
    }


def ps_plus_extract(*, variables: int) -> dict[str, Any]:
    """PS+ extract relevant variables and values."""
    if variables < 0:
        raise SchemaError("variables must be >= 0")
    return {
        "variables": variables,
        "ok": True,
        "note": "planandsolve ps_plus_extract",
    }


def ps_calc_guard(*, careful: bool) -> dict[str, Any]:
    """PS+ calculation/commonsense attention flag (report-only)."""
    return {
        "careful": careful,
        "apply": False,
        "ok": True,
        "note": "planandsolve ps_calc_guard",
    }


def ps_missing_step_fix(*, fixed: bool) -> dict[str, Any]:
    """Flag missing-step error mitigation."""
    return {
        "fixed": fixed,
        "ok": True,
        "note": "planandsolve ps_missing_step_fix",
    }


def ps_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plan → execute → extract → guard."""
    order = ("plan", "execute", "extract", "guard")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plan"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "planandsolve ps_loop_plan",
    }
