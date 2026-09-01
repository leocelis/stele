"""RecMem-shaped recurrence consolidation (stdlib; no LLM).

Shaped by RecMem (arXiv:2605.16045): subconscious buffer, recurrence
trigger, episodic consolidate, semantic refine, merged retrieve.
Proxies only — not RecMem paper scores. No LLM on core write path.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def recmem_buffer_subconscious(*, content: str) -> dict[str, Any]:
    """Buffer raw interaction in subconscious layer (no LLM)."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    bid = hashlib.sha256(
        canonical_dumps({"c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "buffer_id": bid,
        "content": body[:200],
        "ok": True,
        "note": "recmem recmem_buffer_subconscious",
    }


def recmem_recurrence_gate(
    *,
    similar_count: int,
    threshold: int = 5,
) -> dict[str, Any]:
    """Trigger consolidation only when recurrence reaches threshold."""
    if similar_count < 0 or threshold < 1:
        raise SchemaError("similar_count >= 0 and threshold >= 1")
    trigger = similar_count >= threshold
    return {
        "trigger": trigger,
        "similar_count": similar_count,
        "threshold": threshold,
        "ok": True,
        "note": "recmem recmem_recurrence_gate",
    }


def recmem_consolidate_episodic(*, cluster_size: int) -> dict[str, Any]:
    """Episodic abstraction over a recurrent cluster (plan/report only)."""
    if cluster_size < 0:
        raise SchemaError("cluster_size must be >= 0")
    return {
        "cluster_size": cluster_size,
        "ready": cluster_size >= 2,
        "apply": False,
        "ok": True,
        "note": "recmem recmem_consolidate_episodic",
    }


def recmem_semantic_refine(*, omitted_facts: int) -> dict[str, Any]:
    """Recover fine-grained facts omitted by episodic extraction."""
    if omitted_facts < 0:
        raise SchemaError("omitted_facts must be >= 0")
    return {
        "recovered": omitted_facts,
        "ok": True,
        "note": "recmem recmem_semantic_refine",
    }


def recmem_merge_retrieve(
    *,
    subconscious: int,
    episodic: int,
    semantic: int,
) -> dict[str, Any]:
    """Merge retrieve across three tiers."""
    if subconscious < 0 or episodic < 0 or semantic < 0:
        raise SchemaError("counts must be >= 0")
    total = subconscious + episodic + semantic
    return {
        "total": total,
        "ok": True,
        "note": "recmem recmem_merge_retrieve",
    }


def recmem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Buffer → gate → consolidate → refine."""
    order = ("buffer", "gate", "consolidate", "refine")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "buffer"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "recmem recmem_loop_plan",
    }
