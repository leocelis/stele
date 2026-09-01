"""Voyager-shaped skill library + curriculum (stdlib; no LLM).

Shaped by Voyager (arXiv:2305.16291): automatic curriculum, skill
library store/retrieve, iterative self-verify. Proxies only — no
Minecraft / real exec.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def voy_curriculum(*, level: int, task: str) -> dict[str, Any]:
    """Propose next curriculum task at a skill level."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if level < 0:
        raise SchemaError("level must be >= 0")
    cid = hashlib.sha256(
        canonical_dumps({"l": level, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "curriculum_id": cid,
        "level": level,
        "ok": True,
        "note": "voyager voy_curriculum",
    }


def voy_skill_store(*, name: str, code_ref: str) -> dict[str, Any]:
    """Store a skill in the ever-growing library (proxy id)."""
    n = name.strip()
    c = code_ref.strip()
    if not n or not c:
        raise SchemaError("name and code_ref required")
    sid = hashlib.sha256(
        canonical_dumps({"n": n, "c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "skill_id": sid,
        "ok": True,
        "note": "voyager voy_skill_store",
    }


def voy_skill_retrieve(*, query: str) -> dict[str, Any]:
    """Retrieve a skill from the library by query."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    rid = hashlib.sha256(
        canonical_dumps({"q": q}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "retrieve_id": rid,
        "ok": True,
        "note": "voyager voy_skill_retrieve",
    }


def voy_self_verify(*, skill_id: str, passed: bool) -> dict[str, Any]:
    """Self-verification of a skill (report-only)."""
    sid = skill_id.strip()
    if not sid:
        raise SchemaError("skill_id required")
    return {
        "skill_id": sid[:64],
        "passed": passed,
        "apply": False,
        "ok": True,
        "note": "voyager voy_self_verify",
    }


def voy_compose(*, skills: int) -> dict[str, Any]:
    """Flag compositional reuse of stored skills."""
    if skills < 0:
        raise SchemaError("skills must be >= 0")
    return {
        "skills": skills,
        "ok": True,
        "note": "voyager voy_compose",
    }


def voy_loop_plan(*, phase: str) -> dict[str, Any]:
    """Curriculum → store → retrieve → verify."""
    order = ("curriculum", "store", "retrieve", "verify")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "curriculum"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "voyager voy_loop_plan",
    }
