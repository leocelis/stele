"""EvoPrompt proxies (stdlib; no LLM).

Shaped by EvoPrompt (arXiv:2309.08532): connect LLMs with evolutionary
operators (crossover/mutation) over a prompt population. Proxies only.

Prefix ``evp_*`` — not ``evo_*`` (evomemory/evolver) / Promptbreeder (``pbr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def evp_init(*, task: str) -> dict[str, Any]:
    """Initialize a prompt population for EvoPrompt."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    iid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pop_id": iid,
        "ok": True,
        "note": "evp evp_init",
    }


def evp_cross(*, pop_id: str) -> dict[str, Any]:
    """LLM-mediated crossover over parent prompts."""
    pid = pop_id.strip()
    if not pid:
        raise SchemaError("pop_id required")
    cid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cross_id": cid,
        "ok": True,
        "note": "evp evp_cross",
    }


def evp_mutate(*, cross_id: str) -> dict[str, Any]:
    """LLM-mediated mutation of offspring prompts."""
    cid = cross_id.strip()
    if not cid:
        raise SchemaError("cross_id required")
    mid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mut_id": mid,
        "ok": True,
        "note": "evp evp_mutate",
    }


def evp_select(*, mut_id: str, score: int) -> dict[str, Any]:
    """Select into next generation by development-set score (0–100)."""
    mid = mut_id.strip()
    if not mid:
        raise SchemaError("mut_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sel_id": sid,
        "score": score,
        "ok": True,
        "note": "evp evp_select",
    }


def evp_ea(*, connect_ea: bool) -> dict[str, Any]:
    """Flag LLM↔EA connection (report-only)."""
    return {
        "connect_ea": connect_ea,
        "apply": False,
        "ok": True,
        "note": "evp evp_ea",
    }


def evp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → cross → mutate → select."""
    order = ("init", "cross", "mutate", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "evp evp_loop_plan",
    }
