"""Promptbreeder proxies (stdlib; no LLM).

Shaped by Promptbreeder (arXiv:2309.16797): self-referential
evolutionary prompt mutation with diversity maintenance. Proxies only.

Prefix ``pbr_*`` — not Progressive-Hint (``php_*``) / APE (``ape_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def pbr_init(*, task: str) -> dict[str, Any]:
    """Initialize a prompt population for a task domain."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    iid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pop_id": iid,
        "ok": True,
        "note": "pbr pbr_init",
    }


def pbr_mutate(*, pop_id: str) -> dict[str, Any]:
    """Mutate prompts (and mutation-prompts) self-referentially."""
    pid = pop_id.strip()
    if not pid:
        raise SchemaError("pop_id required")
    mid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mut_id": mid,
        "ok": True,
        "note": "pbr pbr_mutate",
    }


def pbr_fitness(*, mut_id: str, score: int) -> dict[str, Any]:
    """Fitness score for an evolved prompt (0–100)."""
    mid = mut_id.strip()
    if not mid:
        raise SchemaError("mut_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    fid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fit_id": fid,
        "score": score,
        "ok": True,
        "note": "pbr pbr_fitness",
    }


def pbr_diversity(*, maintain: bool) -> dict[str, Any]:
    """Flag diversity-maintaining selection (vs APE diminishing returns)."""
    return {
        "maintain": maintain,
        "ok": True,
        "note": "pbr pbr_diversity",
    }


def pbr_selfref(*, self_improve: bool) -> dict[str, Any]:
    """Flag self-referential self-improvement (report-only)."""
    return {
        "self_improve": self_improve,
        "apply": False,
        "ok": True,
        "note": "pbr pbr_selfref",
    }


def pbr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → mutate → fitness → diversity."""
    order = ("init", "mutate", "fitness", "diversity")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "pbr pbr_loop_plan",
    }
