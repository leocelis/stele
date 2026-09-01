"""SAGE multi-agent self-evolution shaped (stdlib; no LLM / no RL).

Shaped by SAGE (arXiv:2603.15255): Challenger–Planner–Solver–Critic closed
loop; Critic filters questions/plans to prevent curriculum drift.
Proxies only — not SAGE paper scores. Module name sagema avoids collision
with unrelated SAGE / Ebbinghaus literature.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sage_challenge_task(*, task: str, difficulty: float = 0.5) -> dict[str, Any]:
    """Challenger generates an increasingly difficult task."""
    body = task.strip()
    if not body:
        raise SchemaError("task required")
    if not (0.0 <= difficulty <= 1.0):
        raise SchemaError("difficulty must be in [0, 1]")
    tid = hashlib.sha256(
        canonical_dumps({"t": body, "d": difficulty}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "task": body[:200],
        "difficulty": difficulty,
        "ok": True,
        "note": "sagema sage_challenge_task",
    }


def sage_plan_steps(*, steps: Sequence[str]) -> dict[str, Any]:
    """Planner converts a task into a structured multi-step plan."""
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise SchemaError("steps sequence required")
    cleaned = [str(s).strip() for s in steps if str(s).strip()]
    if not cleaned:
        raise SchemaError("steps required")
    pid = hashlib.sha256(
        canonical_dumps({"s": cleaned}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plan_id": pid,
        "steps": cleaned[:20],
        "step_count": len(cleaned[:20]),
        "ok": True,
        "note": "sagema sage_plan_steps",
    }


def sage_solve_with_plan(
    *,
    plan_step_count: int,
    followed_steps: int,
    answer: str,
) -> dict[str, Any]:
    """Solver follows the plan to produce an answer."""
    if plan_step_count < 1 or followed_steps < 0:
        raise SchemaError("plan_step_count >= 1 and followed_steps >= 0")
    a = answer.strip()
    if not a:
        raise SchemaError("answer required")
    fidelity = min(1.0, followed_steps / plan_step_count)
    return {
        "answer": a[:200],
        "plan_fidelity": round(fidelity, 4),
        "ok": True,
        "note": "sagema sage_solve_with_plan",
    }


def sage_critic_filter(
    *,
    question_score: float,
    plan_score: float,
    min_score: float = 0.5,
) -> dict[str, Any]:
    """Critic scores and filters questions and plans."""
    for name, val in (
        ("question_score", question_score),
        ("plan_score", plan_score),
        ("min_score", min_score),
    ):
        if not (0.0 <= val <= 1.0):
            raise SchemaError(f"{name} must be in [0, 1]")
    keep = question_score >= min_score and plan_score >= min_score
    return {
        "keep": keep,
        "question_score": question_score,
        "plan_score": plan_score,
        "ok": True,
        "note": "sagema sage_critic_filter",
    }


def sage_drift_gate(
    *,
    difficulty_delta: float,
    max_delta: float = 0.3,
) -> dict[str, Any]:
    """Reject curriculum drift when difficulty jumps too far."""
    if difficulty_delta < 0 or max_delta < 0:
        raise SchemaError("difficulty_delta and max_delta must be >= 0")
    drifted = difficulty_delta > max_delta
    return {
        "drifted": drifted,
        "reject": drifted,
        "apply": False,
        "ok": True,
        "note": "sagema sage_drift_gate",
    }


def sage_closed_loop_round(
    *,
    round_index: int,
    phase: str,
) -> dict[str, Any]:
    """Closed loop: challenge → plan → solve → criticize."""
    if round_index < 0:
        raise SchemaError("round_index must be >= 0")
    order = ("challenge", "plan", "solve", "criticize")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "challenge"
    return {
        "round_index": round_index,
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "sagema sage_closed_loop_round",
    }
