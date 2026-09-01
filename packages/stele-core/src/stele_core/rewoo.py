"""ReWOO-shaped planner/worker/solver (stdlib; no LLM).

Shaped by ReWOO (arXiv:2305.18323): plan tools ahead, workers execute
without interleaving observations into reasoning, solver finishes.
Proxies only — ≠ ReAct.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rewoo_plan(*, task: str, steps: int) -> dict[str, Any]:
    """Planner emits a foresight tool plan."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "s": steps}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "steps": steps,
        "ok": True,
        "note": "rewoo rewoo_plan",
    }


def rewoo_worker(*, plan_id: str, step: int) -> dict[str, Any]:
    """Worker executes one planned tool call (proxy)."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    if step < 0:
        raise SchemaError("step must be >= 0")
    wid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": step}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "evidence_id": wid,
        "step": step,
        "ok": True,
        "note": "rewoo rewoo_worker",
    }


def rewoo_solver(*, plan_id: str, evidence: int) -> dict[str, Any]:
    """Solver combines evidence into a final answer (proxy)."""
    pid = plan_id.strip()
    if not pid:
        raise SchemaError("plan_id required")
    if evidence < 0:
        raise SchemaError("evidence must be >= 0")
    aid = hashlib.sha256(
        canonical_dumps({"p": pid, "e": evidence}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": aid,
        "evidence": evidence,
        "ok": True,
        "note": "rewoo rewoo_solver",
    }


def rewoo_decouple(*, from_observation: bool) -> dict[str, Any]:
    """Flag that reasoning is decoupled from observations."""
    return {
        "from_observation": from_observation,
        "ok": True,
        "note": "rewoo rewoo_decouple",
    }


def rewoo_token_save(*, reduced: bool) -> dict[str, Any]:
    """Flag token reduction vs Thought-Action-Observation (report-only)."""
    return {
        "reduced": reduced,
        "apply": False,
        "ok": True,
        "note": "rewoo rewoo_token_save",
    }


def rewoo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plan → worker → solve → flag."""
    order = ("plan", "worker", "solve", "flag")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plan"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rewoo rewoo_loop_plan",
    }
