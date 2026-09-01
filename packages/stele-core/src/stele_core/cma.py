"""CMA-shaped Continuum Memory Architecture (stdlib; no LLM).

Shaped by Continuum Memory Architectures (arXiv:2601.09913): persistent
storage, selective retention, associative routing, temporal chaining,
consolidation into higher-order abstractions. Proxies only — not CMA paper
scores. Distinct from RAG-as-lookup.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cma_persist(
    *,
    content: str,
) -> dict[str, Any]:
    """Persistent storage write (mutable continuum, not read-only RAG)."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    mid = hashlib.sha256(
        canonical_dumps({"c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entry_id": mid,
        "content": body[:200],
        "mutable": True,
        "ok": True,
        "note": "cma cma_persist",
    }


def cma_selective_retain(
    *,
    utility: float,
    retain_threshold: float = 0.4,
) -> dict[str, Any]:
    """Selective retention: keep when utility >= threshold."""
    if not (0.0 <= utility <= 1.0) or not (0.0 <= retain_threshold <= 1.0):
        raise SchemaError("utility and retain_threshold must be in [0, 1]")
    retain = utility >= retain_threshold
    return {
        "retain": retain,
        "utility": utility,
        "apply": False,
        "ok": True,
        "note": "cma cma_selective_retain",
    }


def cma_associative_route(
    *,
    cue: str,
    hop_budget: int = 2,
) -> dict[str, Any]:
    """Associative routing from a cue with hop budget."""
    body = cue.strip()
    if not body:
        raise SchemaError("cue required")
    if hop_budget < 1:
        raise SchemaError("hop_budget must be >= 1")
    return {
        "cue": body[:80],
        "hop_budget": hop_budget,
        "ok": True,
        "note": "cma cma_associative_route",
    }


def cma_temporal_chain(
    *,
    event_a: str,
    event_b: str,
    order_ok: bool,
) -> dict[str, Any]:
    """Temporal chaining: link events when order is valid."""
    a = event_a.strip()
    b = event_b.strip()
    if not a or not b:
        raise SchemaError("event_a and event_b required")
    linked = order_ok
    return {
        "linked": linked,
        "event_a": a[:64],
        "event_b": b[:64],
        "ok": True,
        "note": "cma cma_temporal_chain",
    }


def cma_consolidate(
    *,
    episode_count: int,
    min_episodes: int = 2,
) -> dict[str, Any]:
    """Consolidate episodes into higher-order abstraction when enough exist."""
    if episode_count < 0 or min_episodes < 1:
        raise SchemaError("episode_count >= 0 and min_episodes >= 1")
    consolidate = episode_count >= min_episodes
    return {
        "consolidate": consolidate,
        "episode_count": episode_count,
        "apply": False,
        "ok": True,
        "note": "cma cma_consolidate",
    }


def cma_probe_gate(
    *,
    probe: str,
    supports_mutation: bool,
) -> dict[str, Any]:
    """Behavioral probe gate: CMA must support mutation (vs RAG)."""
    if probe not in (
        "knowledge_update",
        "temporal_association",
        "associative_recall",
        "contextual_disambiguation",
    ):
        raise SchemaError("unknown probe")
    pass_probe = supports_mutation
    return {
        "probe": probe,
        "pass": pass_probe,
        "ok": True,
        "note": "cma cma_probe_gate",
    }


def cma_loop_plan(*, phase: str) -> dict[str, Any]:
    """Persist → retain → route → chain → consolidate."""
    order = ("persist", "retain", "route", "chain", "consolidate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "persist"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cma cma_loop_plan",
    }
