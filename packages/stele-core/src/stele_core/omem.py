"""O-Mem-shaped active user profiling memory (stdlib; no LLM).

Shaped by O-Mem (arXiv:2511.13593): active persona/event extraction, hierarchical
persona vs topic retrieve, memory-time scaling. Proxies only — not O-Mem
paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def omem_extract_persona(*, trait: str, confidence: float) -> dict[str, Any]:
    """Extract a persona attribute from interaction."""
    body = trait.strip()
    if not body:
        raise SchemaError("trait required")
    if not (0.0 <= confidence <= 1.0):
        raise SchemaError("confidence must be in [0, 1]")
    pid = hashlib.sha256(
        canonical_dumps({"t": body, "c": confidence}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "persona_id": pid,
        "trait": body[:80],
        "confidence": confidence,
        "ok": True,
        "note": "omem omem_extract_persona",
    }


def omem_update_event(*, event: str, timestamp: str) -> dict[str, Any]:
    """Record an event in the user event stream."""
    body = event.strip()
    ts = timestamp.strip()
    if not body or not ts:
        raise SchemaError("event and timestamp required")
    eid = hashlib.sha256(
        canonical_dumps({"e": body, "ts": ts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "event_id": eid,
        "event": body[:120],
        "timestamp": ts[:40],
        "ok": True,
        "note": "omem omem_update_event",
    }


def omem_hierarchy_retrieve(*, channel: str, hits: int) -> dict[str, Any]:
    """Hierarchical retrieve: persona attributes or topic context."""
    if channel not in ("persona", "topic"):
        raise SchemaError("channel must be persona or topic")
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "channel": channel,
        "hits": hits,
        "ok": True,
        "note": "omem omem_hierarchy_retrieve",
    }


def omem_profile_gate(*, confidence: float, min_confidence: float = 0.5) -> dict[str, Any]:
    """Admit profile updates only above confidence floor."""
    if not (0.0 <= confidence <= 1.0) or not (0.0 <= min_confidence <= 1.0):
        raise SchemaError("confidence values must be in [0, 1]")
    admit = confidence >= min_confidence
    return {
        "admit": admit,
        "apply": False,
        "ok": True,
        "note": "omem omem_profile_gate",
    }


def omem_scale_memory_time(*, interactions: int, memory_units: int) -> dict[str, Any]:
    """Memory-time scaling: units per interaction density."""
    if interactions < 1 or memory_units < 0:
        raise SchemaError("interactions >= 1 and memory_units >= 0")
    density = round(memory_units / interactions, 4)
    return {
        "density": density,
        "interactions": interactions,
        "memory_units": memory_units,
        "ok": True,
        "note": "omem omem_scale_memory_time",
    }


def omem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Extract → event → retrieve → gate."""
    order = ("extract", "event", "retrieve", "gate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "extract"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "omem omem_loop_plan",
    }
