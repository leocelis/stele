"""ReAct-shaped thought–act–observe (stdlib; no LLM / no live env).

Shaped by ReAct (arXiv:2210.03629): interleave Thought, Action, Observe,
Finish; record trajectory. Proxies only — not Wikipedia API / ALFWorld.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def react_thought(*, step: int, text: str) -> dict[str, Any]:
    """Record a reasoning Thought."""
    if step < 0:
        raise SchemaError("step must be >= 0")
    t = text.strip()
    if not t:
        raise SchemaError("text required")
    tid = hashlib.sha256(
        canonical_dumps({"s": step, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "thought_id": tid,
        "step": step,
        "ok": True,
        "note": "react react_thought",
    }


def react_action(*, action: str, arg: str) -> dict[str, Any]:
    """Emit an Action (e.g. Search[...]) — report-only apply."""
    a = action.strip()
    g = arg.strip()
    if not a:
        raise SchemaError("action required")
    return {
        "action": a[:64],
        "arg": g[:128],
        "apply": False,
        "ok": True,
        "note": "react react_action",
    }


def react_observe(*, observation: str) -> dict[str, Any]:
    """Record an Observation from the environment/API."""
    o = observation.strip()
    if not o:
        raise SchemaError("observation required")
    oid = hashlib.sha256(
        canonical_dumps({"o": o}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "obs_id": oid,
        "ok": True,
        "note": "react react_observe",
    }


def react_finish(*, answer: str) -> dict[str, Any]:
    """Finish with a final answer (report-only)."""
    a = answer.strip()
    if not a:
        raise SchemaError("answer required")
    return {
        "answer": a[:256],
        "apply": False,
        "ok": True,
        "note": "react react_finish",
    }


def react_trajectory(*, steps: int) -> dict[str, Any]:
    """Count Thought–Action–Observe triples in a trajectory."""
    if steps < 0:
        raise SchemaError("steps must be >= 0")
    return {
        "steps": steps,
        "ok": True,
        "note": "react react_trajectory",
    }


def react_loop_plan(*, phase: str) -> dict[str, Any]:
    """Thought → action → observe → finish."""
    order = ("thought", "action", "observe", "finish")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "thought"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "react react_loop_plan",
    }
