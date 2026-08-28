"""MemoryBank-shaped long-term companion memory (stdlib; no LLM).

Shaped by MemoryBank (arXiv:2305.10250): summon relevant memories,
personality synthesis, Ebbinghaus-inspired forget/reinforce updates.
Proxies only — not MemoryBank paper scores.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mbank_store_memory(*, content: str, significance: float) -> dict[str, Any]:
    """Store a long-term memory with relative significance."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    if not (0.0 <= significance <= 1.0):
        raise SchemaError("significance must be in [0, 1]")
    mid = hashlib.sha256(
        canonical_dumps({"c": body, "s": significance}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "significance": round(significance, 4),
        "ok": True,
        "note": "memorybank mbank_store_memory",
    }


def mbank_summon(*, query: str, hits: int) -> dict[str, Any]:
    """Summon relevant memories for the current turn."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "query": q[:120],
        "hits": hits,
        "ok": True,
        "note": "memorybank mbank_summon",
    }


def mbank_personality_synth(*, traits: int) -> dict[str, Any]:
    """Synthesize user personality from accumulated interactions."""
    if traits < 0:
        raise SchemaError("traits must be >= 0")
    return {
        "traits": traits,
        "ready": traits >= 1,
        "ok": True,
        "note": "memorybank mbank_personality_synth",
    }


def mbank_forget_curve(
    *,
    days_elapsed: float,
    strength: float = 1.0,
) -> dict[str, Any]:
    """Ebbinghaus-shaped retention: R = e^(-t/S). Report-only fade plan."""
    if days_elapsed < 0.0 or strength <= 0.0:
        raise SchemaError("days_elapsed >= 0 and strength > 0")
    retention = math.exp(-days_elapsed / strength)
    fade = retention < 0.37
    return {
        "retention": round(retention, 4),
        "fade": fade,
        "apply": False,
        "ok": True,
        "note": "memorybank mbank_forget_curve",
    }


def mbank_reinforce(*, memory_id: str, boost: float) -> dict[str, Any]:
    """Reinforce a memory after successful recall (no auto-delete)."""
    mid = memory_id.strip()
    if not mid:
        raise SchemaError("memory_id required")
    if boost < 0.0:
        raise SchemaError("boost must be >= 0")
    return {
        "memory_id": mid[:64],
        "boost": round(boost, 4),
        "ok": True,
        "note": "memorybank mbank_reinforce",
    }


def mbank_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → summon → personality → forget."""
    order = ("store", "summon", "personality", "forget")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memorybank mbank_loop_plan",
    }
