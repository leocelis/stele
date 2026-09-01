"""Socratic-Zero-shaped Teacher–Solver–Generator (stdlib; no LLM).

Shaped by Socratic-Zero (arXiv:2509.24726): Teacher crafts hard questions from
Solver weaknesses; Solver learns from preference on win/fail; Generator
distills Teacher strategy for scalable curriculum from minimal seed.
Proxies only — not Socratic-Zero paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def socratic_teacher_craft(
    *,
    weakness: str,
    question: str,
) -> dict[str, Any]:
    """Teacher crafts a question targeting a Solver weakness."""
    w = weakness.strip()
    q = question.strip()
    if not w or not q:
        raise SchemaError("weakness and question required")
    qid = hashlib.sha256(
        canonical_dumps({"w": w, "q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "question_id": qid,
        "weakness": w[:80],
        "question": q[:200],
        "ok": True,
        "note": "socratic socratic_teacher_craft",
    }


def socratic_solver_preference(
    *,
    success: bool,
    failed: bool,
) -> dict[str, Any]:
    """Solver preference signal from successful vs failed trajectories."""
    if success and failed:
        raise SchemaError("success and failed cannot both be true")
    if not success and not failed:
        raise SchemaError("need success or failed")
    return {
        "prefer_success": success,
        "prefer_failure_for_critique": failed,
        "ok": True,
        "note": "socratic socratic_solver_preference",
    }


def socratic_generator_distill(
    *,
    teacher_strategy: str,
) -> dict[str, Any]:
    """Generator distills Teacher question-design strategy."""
    body = teacher_strategy.strip()
    if not body:
        raise SchemaError("teacher_strategy required")
    sid = hashlib.sha256(
        canonical_dumps({"s": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "strategy_id": sid,
        "strategy": body[:200],
        "ok": True,
        "note": "socratic socratic_generator_distill",
    }


def socratic_seed_bootstrap(
    *,
    seed_count: int,
    min_seeds: int = 100,
) -> dict[str, Any]:
    """Minimal seed gate (paper starts from ~100 seeds)."""
    if seed_count < 0 or min_seeds < 1:
        raise SchemaError("seed_count >= 0 and min_seeds >= 1")
    ready = seed_count >= min_seeds
    return {
        "ready": ready,
        "seed_count": seed_count,
        "min_seeds": min_seeds,
        "ok": True,
        "note": "socratic socratic_seed_bootstrap",
    }


def socratic_weakness_target(
    *,
    fail_rate: float,
    threshold: float = 0.4,
) -> dict[str, Any]:
    """Teacher targets weaknesses where fail_rate is above threshold."""
    if not (0.0 <= fail_rate <= 1.0):
        raise SchemaError("fail_rate must be in [0, 1]")
    if not (0.0 <= threshold <= 1.0):
        raise SchemaError("threshold must be in [0, 1]")
    return {
        "target": fail_rate >= threshold,
        "fail_rate": fail_rate,
        "ok": True,
        "note": "socratic socratic_weakness_target",
    }


def socratic_closed_loop(
    *,
    phase: str,
) -> dict[str, Any]:
    """Closed loop: teach → solve → prefer → distill."""
    order = ("teach", "solve", "prefer", "distill")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "teach"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "socratic socratic_closed_loop",
    }
