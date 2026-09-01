"""CAMEL-shaped role-playing communicative agents (stdlib; no LLM).

Shaped by CAMEL (arXiv:2303.17760): assign roles, inception prompt,
message turn, task complete. Proxies only — ≠ Multiagent Debate.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def camel_roles(*, user_role: str, assistant_role: str) -> dict[str, Any]:
    """Assign user and assistant roles for role-playing."""
    u = user_role.strip()
    a = assistant_role.strip()
    if not u or not a:
        raise SchemaError("user_role and assistant_role required")
    rid = hashlib.sha256(
        canonical_dumps({"u": u, "a": a}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "role_id": rid,
        "ok": True,
        "note": "camel camel_roles",
    }


def camel_inception(*, role_id: str, task: str) -> dict[str, Any]:
    """Inception prompt to steer agents toward the task."""
    rid = role_id.strip()
    t = task.strip()
    if not rid or not t:
        raise SchemaError("role_id and task required")
    iid = hashlib.sha256(
        canonical_dumps({"r": rid, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "inception_id": iid,
        "ok": True,
        "note": "camel camel_inception",
    }


def camel_turn(*, inception_id: str, speaker: str) -> dict[str, Any]:
    """One communicative turn between agents."""
    iid = inception_id.strip()
    s = speaker.strip()
    if not iid or not s:
        raise SchemaError("inception_id and speaker required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid, "s": s}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "turn_id": tid,
        "ok": True,
        "note": "camel camel_turn",
    }


def camel_complete(*, done: bool) -> dict[str, Any]:
    """Flag autonomous task completion (report-only)."""
    return {
        "done": done,
        "apply": False,
        "ok": True,
        "note": "camel camel_complete",
    }


def camel_society(*, agents: int) -> dict[str, Any]:
    """Count agents in the communicative society."""
    if agents < 2:
        raise SchemaError("agents must be >= 2")
    return {
        "agents": agents,
        "ok": True,
        "note": "camel camel_society",
    }


def camel_loop_plan(*, phase: str) -> dict[str, Any]:
    """Roles → inception → turn → complete."""
    order = ("roles", "inception", "turn", "complete")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "roles"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "camel camel_loop_plan",
    }
