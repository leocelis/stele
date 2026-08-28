"""LIVE-EVO-shaped online memory evolution (stdlib; no LLM).

Shaped by LIVE-EVO (arXiv:2602.02369): Experience Bank + Meta-Guideline Bank,
contrastive weight updates, decay of stale experiences, online stream loop.
Proxies only — not LIVE-EVO paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def experience_bank_record(
    *,
    experience: str,
    weight: float = 1.0,
) -> dict[str, Any]:
    """Store a structured experience with an initial retrieval weight."""
    body = experience.strip()
    if not body:
        raise SchemaError("experience required")
    if weight < 0:
        raise SchemaError("weight must be >= 0")
    eid = hashlib.sha256(
        canonical_dumps({"e": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experience_id": eid,
        "weight": weight,
        "content": body[:200],
        "ok": True,
        "note": "liveevo experience_bank_record",
    }


def meta_guideline_record(
    *,
    guideline: str,
) -> dict[str, Any]:
    """Store a higher-level meta-guideline for composing experiences."""
    body = guideline.strip()
    if not body:
        raise SchemaError("guideline required")
    gid = hashlib.sha256(
        canonical_dumps({"g": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "guideline_id": gid,
        "guideline": body[:200],
        "ok": True,
        "note": "liveevo meta_guideline_record",
    }


def compile_task_guideline(
    *,
    task: str,
    experience_count: int,
    has_meta: bool,
) -> dict[str, Any]:
    """Compile task-adaptive guideline from retrieved experiences + meta."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if experience_count < 0:
        raise SchemaError("experience_count must be >= 0")
    ready = experience_count > 0 and has_meta
    return {
        "compiled": ready,
        "task": t[:120],
        "ok": True,
        "note": "liveevo compile_task_guideline",
    }


def update_experience_weight(
    *,
    weight: float,
    delta_on_minus_off: float,
    lr: float = 0.1,
) -> dict[str, Any]:
    """Reinforce when memory-on beats memory-off; else down-weight."""
    if weight < 0 or lr < 0:
        raise SchemaError("weight and lr must be >= 0")
    new_w = max(0.0, weight + lr * delta_on_minus_off)
    return {
        "weight": round(new_w, 4),
        "reinforced": delta_on_minus_off > 0,
        "ok": True,
        "note": "liveevo update_experience_weight",
    }


def forget_stale_experience(
    *,
    weight: float,
    min_weight: float = 0.05,
) -> dict[str, Any]:
    """Gradually forget when weight falls below floor."""
    if weight < 0 or min_weight < 0:
        raise SchemaError("weight and min_weight must be >= 0")
    forget = weight < min_weight
    return {
        "forget": forget,
        "weight": weight,
        "min_weight": min_weight,
        "apply": False,
        "ok": True,
        "note": "liveevo forget_stale_experience",
    }


def liveevo_online_round(
    *,
    phase: str,
) -> dict[str, Any]:
    """Online loop: retrieve → compile → act → update."""
    order = ("retrieve", "compile", "act", "update")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "retrieve"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "liveevo liveevo_online_round",
    }
