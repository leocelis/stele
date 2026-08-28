"""Reflexion-shaped verbal reinforcement (stdlib; no LLM / no live RL).

Shaped by Reflexion (arXiv:2303.11366): trial, evaluate, verbal reflect,
episodic memory, next trial. Proxies only — not Shinn Reflexion agents.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rx_trial_run(*, task: str, trial: int = 0) -> dict[str, Any]:
    """Record a trial attempt."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if trial < 0:
        raise SchemaError("trial must be >= 0")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "n": trial}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "trial_id": tid,
        "trial": trial,
        "ok": True,
        "note": "reflexion rx_trial_run",
    }


def rx_evaluate(*, trial_id: str, success: bool) -> dict[str, Any]:
    """Evaluate trial outcome (report-only apply)."""
    tid = trial_id.strip()
    if not tid:
        raise SchemaError("trial_id required")
    return {
        "trial_id": tid[:64],
        "success": success,
        "apply": False,
        "ok": True,
        "note": "reflexion rx_evaluate",
    }


def rx_verbal_reflect(*, trial_id: str, feedback: str) -> dict[str, Any]:
    """Produce a verbal reflection from feedback."""
    tid = trial_id.strip()
    f = feedback.strip()
    if not tid:
        raise SchemaError("trial_id required")
    if not f:
        raise SchemaError("feedback required")
    rid = hashlib.sha256(
        canonical_dumps({"t": tid, "f": f}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflection_id": rid,
        "trial_id": tid[:64],
        "ok": True,
        "note": "reflexion rx_verbal_reflect",
    }


def rx_memory_store(*, reflection_id: str) -> dict[str, Any]:
    """Store reflection in episodic buffer (report-only)."""
    rid = reflection_id.strip()
    if not rid:
        raise SchemaError("reflection_id required")
    return {
        "reflection_id": rid[:64],
        "stored": True,
        "apply": False,
        "ok": True,
        "note": "reflexion rx_memory_store",
    }


def rx_next_trial(*, reflections: int) -> dict[str, Any]:
    """Plan next trial conditioned on reflection count."""
    if reflections < 0:
        raise SchemaError("reflections must be >= 0")
    return {
        "reflections": reflections,
        "ready": True,
        "ok": True,
        "note": "reflexion rx_next_trial",
    }


def rx_loop_plan(*, phase: str) -> dict[str, Any]:
    """Trial → evaluate → reflect → store."""
    order = ("trial", "evaluate", "reflect", "store")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "trial"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "reflexion rx_loop_plan",
    }
