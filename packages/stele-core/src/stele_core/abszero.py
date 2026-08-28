"""Absolute Zero Reasoner-shaped self-play (stdlib; no LLM / no executor).

Shaped by Absolute Zero / AZR (arXiv:2505.03335): propose+solve loop,
induction/abduction/deduction modes, learnability reward, executor verify.
Proxies only — not AZR paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

TASK_MODES = frozenset({"induction", "abduction", "deduction"})


def propose_reasoning_task(
    *,
    mode: str,
    seed_hint: str = "",
) -> dict[str, Any]:
    """Proposer samples a task of a given reasoning mode."""
    if mode not in TASK_MODES:
        raise SchemaError(f"mode must be one of {sorted(TASK_MODES)}")
    hint = seed_hint.strip()[:80]
    body = f"{mode} task"
    if hint:
        body = f"{body}: {hint}"
    tid = hashlib.sha256(
        canonical_dumps({"m": mode, "b": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "mode": mode,
        "query": body[:160],
        "ok": True,
        "note": "abszero propose_reasoning_task",
    }


def validate_task_structure(
    *,
    has_program: bool,
    has_input: bool,
    has_output: bool,
    mode: str,
) -> dict[str, Any]:
    """
    Validate (program, input, output) triplet completeness by mode.
    induction: program+input → output; deduction: program+output → input;
    abduction: input+output → program (proxy flags).
    """
    if mode not in TASK_MODES:
        raise SchemaError(f"mode must be one of {sorted(TASK_MODES)}")
    if mode == "induction":
        valid = has_program and has_input
    elif mode == "deduction":
        valid = has_program and has_output
    else:  # abduction
        valid = has_input and has_output
    return {
        "valid": valid,
        "mode": mode,
        "ok": True,
        "note": "abszero validate_task_structure",
    }


def learnability_reward(
    *,
    mean_solve_rate: float,
) -> dict[str, Any]:
    """r_propose = 0 if mean_solve=0 else 1 − mean_solve (neither trivial nor impossible)."""
    if not (0.0 <= mean_solve_rate <= 1.0):
        raise SchemaError("mean_solve_rate must be in [0, 1]")
    if mean_solve_rate == 0.0:
        r = 0.0
    else:
        r = 1.0 - mean_solve_rate
    return {
        "r_propose": round(r, 4),
        "mean_solve_rate": mean_solve_rate,
        "sweet_spot": 0.3 <= mean_solve_rate <= 0.7,
        "ok": True,
        "note": "abszero learnability_reward",
    }


def solve_reward(
    *,
    answer_match: bool,
) -> dict[str, Any]:
    """r_solve binary from executor match."""
    return {
        "r_solve": 1.0 if answer_match else 0.0,
        "ok": True,
        "note": "abszero solve_reward",
    }


def abszero_joint_objective(
    *,
    r_propose: float,
    r_solve: float,
    lambda_propose: float = 0.5,
) -> dict[str, Any]:
    """λ r_propose + r_solve joint objective proxy."""
    if not (0.0 <= lambda_propose <= 1.0):
        raise SchemaError("lambda_propose must be in [0, 1]")
    total = lambda_propose * r_propose + r_solve
    return {
        "total": round(total, 4),
        "r_propose": r_propose,
        "r_solve": r_solve,
        "ok": True,
        "note": "abszero abszero_joint_objective",
    }


def executor_verify_gate(
    *,
    task_valid: bool,
    answer_match: bool,
) -> dict[str, Any]:
    """Environment as unified verifier for propose+solve."""
    return {
        "accept_pair": task_valid and answer_match,
        "task_valid": task_valid,
        "answer_match": answer_match,
        "apply": False,
        "ok": True,
        "note": "abszero executor_verify_gate",
    }
