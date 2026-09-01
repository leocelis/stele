"""SkillCraft-shaped Skill Mode (stdlib; no LLM).

Shaped by SkillCraft (arXiv:2603.00718): save/get/list/execute skill library,
coding verifier gate, token-efficiency proxy. Proxies only — not SkillCraft
paper scores. No live sandbox execution on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def skillcraft_save_skill(
    *,
    name: str,
    steps: int,
    verified: bool,
) -> dict[str, Any]:
    """Persist a composed skill only when verified."""
    body = name.strip()
    if not body:
        raise SchemaError("name required")
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    admitted = verified
    sid = hashlib.sha256(
        canonical_dumps({"n": body, "s": steps}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "skill_id": sid if admitted else None,
        "name": body[:80],
        "steps": steps,
        "admitted": admitted,
        "ok": True,
        "note": "skillcraft skillcraft_save_skill",
    }


def skillcraft_get_skill(*, skill_id: str) -> dict[str, Any]:
    """Retrieve skill metadata by id."""
    sid = skill_id.strip()
    if not sid:
        raise SchemaError("skill_id required")
    return {
        "skill_id": sid[:64],
        "found": True,
        "ok": True,
        "note": "skillcraft skillcraft_get_skill",
    }


def skillcraft_list_skills(*, library_size: int) -> dict[str, Any]:
    """Enumerate skill library size."""
    if library_size < 0:
        raise SchemaError("library_size must be >= 0")
    return {
        "count": library_size,
        "ok": True,
        "note": "skillcraft skillcraft_list_skills",
    }


def skillcraft_execute_skill(
    *,
    skill_exists: bool,
    params_ok: bool,
) -> dict[str, Any]:
    """Invoke cached skill when present and params valid."""
    executed = skill_exists and params_ok
    return {
        "executed": executed,
        "ok": True,
        "note": "skillcraft skillcraft_execute_skill",
    }


def skillcraft_verify_skill(
    *,
    syntax_ok: bool,
    runtime_ok: bool,
    nonempty_output: bool,
) -> dict[str, Any]:
    """Coding verifier: syntax + runtime + nonempty output."""
    verified = syntax_ok and runtime_ok and nonempty_output
    return {
        "verified": verified,
        "ok": True,
        "note": "skillcraft skillcraft_verify_skill",
    }


def skillcraft_token_efficiency(
    *,
    tokens_baseline: int,
    tokens_skill_mode: int,
) -> dict[str, Any]:
    """Token reduction ratio vs baseline (report-only)."""
    if tokens_baseline < 1 or tokens_skill_mode < 0:
        raise SchemaError("tokens_baseline >= 1 and tokens_skill_mode >= 0")
    if tokens_skill_mode > tokens_baseline:
        raise SchemaError("tokens_skill_mode must be <= baseline")
    reduction = round(1.0 - (tokens_skill_mode / tokens_baseline), 4)
    return {
        "reduction": reduction,
        "tokens_baseline": tokens_baseline,
        "tokens_skill_mode": tokens_skill_mode,
        "ok": True,
        "note": "skillcraft skillcraft_token_efficiency",
    }


def skillcraft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Explore → verify → save → execute."""
    order = ("explore", "verify", "save", "execute")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "explore"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "skillcraft skillcraft_loop_plan",
    }
