"""Memanto-shaped typed semantic memory (stdlib; no LLM).

Shaped by Memanto (arXiv:2604.22085): typed category schema, conflict
resolution, temporal versioning, single-query info-theoretic retrieve
(no index ingest delay). Proxies only — not Memanto paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

CATEGORIES = frozenset(
    {
        "preference",
        "fact",
        "event",
        "entity",
        "relation",
        "goal",
        "constraint",
        "skill",
        "decision",
        "feedback",
        "context",
        "meta",
        "other",
    }
)


def memanto_store_typed(
    *,
    category: str,
    content: str,
) -> dict[str, Any]:
    """Store into one of thirteen typed semantic categories."""
    if category not in CATEGORIES:
        raise SchemaError(f"category must be one of {sorted(CATEGORIES)}")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    mid = hashlib.sha256(
        canonical_dumps({"cat": category, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entry_id": mid,
        "category": category,
        "content": body[:200],
        "ok": True,
        "note": "memanto memanto_store_typed",
    }


def memanto_conflict_resolve(
    *,
    conflict: bool,
    newer_wins: bool,
) -> dict[str, Any]:
    """Automated conflict resolution plan (report-only)."""
    resolve = conflict
    winner = "newer" if (conflict and newer_wins) else (
        "older" if conflict else "none"
    )
    return {
        "resolve": resolve,
        "winner": winner,
        "apply": False,
        "ok": True,
        "note": "memanto memanto_conflict_resolve",
    }


def memanto_version(
    *,
    entry_id: str,
    version: int,
) -> dict[str, Any]:
    """Temporal versioning stamp."""
    eid = entry_id.strip()
    if not eid:
        raise SchemaError("entry_id required")
    if version < 1:
        raise SchemaError("version must be >= 1")
    return {
        "entry_id": eid[:64],
        "version": version,
        "ok": True,
        "note": "memanto memanto_version",
    }


def memanto_retrieve(
    *,
    query: str,
    single_query: bool = True,
) -> dict[str, Any]:
    """Single-query info-theoretic retrieve (no multi-query pipeline)."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    return {
        "query": q[:120],
        "queries_fired": 1 if single_query else 2,
        "ingestion_delay_ms": 0,
        "ok": True,
        "note": "memanto memanto_retrieve",
    }


def memanto_latency_gate(
    *,
    latency_ms: float,
    soft_cap_ms: float = 90.0,
) -> dict[str, Any]:
    """Sub-90ms soft latency gate."""
    if latency_ms < 0 or soft_cap_ms < 1:
        raise SchemaError("latency_ms >= 0 and soft_cap_ms >= 1")
    under = latency_ms <= soft_cap_ms
    return {
        "under_cap": under,
        "latency_ms": latency_ms,
        "ok": True,
        "note": "memanto memanto_latency_gate",
    }


def memanto_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → version → retrieve → conflict."""
    order = ("store", "version", "retrieve", "conflict")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memanto memanto_loop_plan",
    }
