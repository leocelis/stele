"""SMITH-shaped cognitive memory + tool hub (stdlib; no LLM / no sandbox).

Shaped by SMITH (arXiv:2512.11303): procedural/semantic/episodic hierarchy,
dynamic tool creation in sandbox, cross-task episodic reuse, curriculum.
Proxies only — not SMITH paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

TIERS = frozenset({"procedural", "semantic", "episodic"})


def smith_store_memory(
    *,
    tier: str,
    content: str,
) -> dict[str, Any]:
    """Store memory in procedural | semantic | episodic tier."""
    if tier not in TIERS:
        raise SchemaError(f"tier must be one of {sorted(TIERS)}")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    mid = hashlib.sha256(
        canonical_dumps({"t": tier, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "tier": tier,
        "content": body[:200],
        "ok": True,
        "note": "smith smith_store_memory",
    }


def smith_create_tool(
    *,
    tool_name: str,
    sandbox_pass: bool,
) -> dict[str, Any]:
    """Admit a tool only after sandbox exec succeeds."""
    name = tool_name.strip()
    if not name:
        raise SchemaError("tool_name required")
    if not sandbox_pass:
        return {
            "admitted": False,
            "tool_name": name[:80],
            "apply": False,
            "ok": True,
            "note": "smith smith_create_tool",
        }
    tid = hashlib.sha256(
        canonical_dumps({"n": name}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "admitted": True,
        "tool_id": tid,
        "tool_name": name[:80],
        "apply": False,
        "ok": True,
        "note": "smith smith_create_tool",
    }


def smith_retrieve_episode(
    *,
    similarity: float,
    threshold: float = 0.5,
) -> dict[str, Any]:
    """Cross-task episodic retrieve when semantic similarity > θ."""
    if not (0.0 <= similarity <= 1.0):
        raise SchemaError("similarity must be in [0, 1]")
    if not (0.0 <= threshold <= 1.0):
        raise SchemaError("threshold must be in [0, 1]")
    return {
        "hit": similarity > threshold,
        "similarity": similarity,
        "ok": True,
        "note": "smith smith_retrieve_episode",
    }


def smith_curriculum_difficulty(
    *,
    ensemble_fail_rate: float,
) -> dict[str, Any]:
    """Agent-ensemble difficulty re-estimation for curriculum."""
    if not (0.0 <= ensemble_fail_rate <= 1.0):
        raise SchemaError("ensemble_fail_rate must be in [0, 1]")
    if ensemble_fail_rate >= 0.7:
        band = "hard"
    elif ensemble_fail_rate >= 0.3:
        band = "medium"
    else:
        band = "easy"
    return {
        "band": band,
        "ensemble_fail_rate": ensemble_fail_rate,
        "ok": True,
        "note": "smith smith_curriculum_difficulty",
    }


def smith_tool_reuse_gate(
    *,
    tool_exists: bool,
    task_similar: bool,
) -> dict[str, Any]:
    """Prefer reusing existing tools over creating from scratch."""
    return {
        "reuse": tool_exists and task_similar,
        "create_new": not tool_exists,
        "apply": False,
        "ok": True,
        "note": "smith smith_tool_reuse_gate",
    }


def smith_loop_plan(*, phase: str) -> dict[str, Any]:
    """Unified loop: store → tool → retrieve → act."""
    order = ("store", "tool", "retrieve", "act")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "smith smith_loop_plan",
    }
