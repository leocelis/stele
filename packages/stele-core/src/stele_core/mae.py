"""Multi-Agent Evolve-shaped triad (stdlib; no LLM / no RL).

Shaped by Multi-Agent Evolve / MAE (arXiv:2510.23595): Proposer–Solver–Judge
from one backbone; Judge quality + difficulty rewards; no external verifier required.
Proxies only — not MAE paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mae_propose_question(*, question: str) -> dict[str, Any]:
    """Proposer generates a question."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    qid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "question_id": qid,
        "question": q[:200],
        "ok": True,
        "note": "mae mae_propose_question",
    }


def mae_solve_attempt(*, answer: str) -> dict[str, Any]:
    """Solver produces an answer attempt."""
    a = answer.strip()
    if not a:
        raise SchemaError("answer required")
    return {
        "answer": a[:200],
        "ok": True,
        "note": "mae mae_solve_attempt",
    }


def mae_judge_score(
    *,
    quality_score: float,
    correctness_score: float,
) -> dict[str, Any]:
    """Judge scores question quality and solver correctness (0–1 each)."""
    for name, val in (
        ("quality_score", quality_score),
        ("correctness_score", correctness_score),
    ):
        if not (0.0 <= val <= 1.0):
            raise SchemaError(f"{name} must be in [0, 1]")
    return {
        "quality_score": quality_score,
        "correctness_score": correctness_score,
        "ok": True,
        "note": "mae mae_judge_score",
    }


def mae_proposer_reward(
    *,
    quality_score: float,
    solver_failed: bool,
    difficulty_weight: float = 0.5,
) -> dict[str, Any]:
    """Proposer gets quality + difficulty (higher when Solver fails)."""
    if not (0.0 <= quality_score <= 1.0):
        raise SchemaError("quality_score must be in [0, 1]")
    if not (0.0 <= difficulty_weight <= 1.0):
        raise SchemaError("difficulty_weight must be in [0, 1]")
    diff = difficulty_weight if solver_failed else 0.0
    total = quality_score * (1.0 - difficulty_weight) + diff
    return {
        "r_proposer": round(total, 4),
        "difficulty_bonus": round(diff, 4),
        "ok": True,
        "note": "mae mae_proposer_reward",
    }


def mae_quality_filter(
    *,
    quality_score: float,
    min_quality: float = 0.5,
) -> dict[str, Any]:
    """Keep questions above Judge quality floor."""
    if not (0.0 <= quality_score <= 1.0):
        raise SchemaError("quality_score must be in [0, 1]")
    if not (0.0 <= min_quality <= 1.0):
        raise SchemaError("min_quality must be in [0, 1]")
    return {
        "keep": quality_score >= min_quality,
        "quality_score": quality_score,
        "min_quality": min_quality,
        "ok": True,
        "note": "mae mae_quality_filter",
    }


def mae_triad_round_plan(
    *,
    round_index: int,
    phase: str,
) -> dict[str, Any]:
    """Ordered triad: propose → solve → judge."""
    if round_index < 0:
        raise SchemaError("round_index must be >= 0")
    order = ("propose", "solve", "judge")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "round_index": round_index,
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mae mae_triad_round_plan",
    }
