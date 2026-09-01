"""AgeMem-shaped unified LTM/STM tool actions (stdlib; no LLM).

Shaped by AgeMem (arXiv:2601.01885): memory ops as tool actions for
store/retrieve/update/summarize/discard across LTM and STM. Proxies only
— not AgeMem RL scores. Discard plans are report-only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def agemem_ltm_store(*, content: str, tier: str = "ltm") -> dict[str, Any]:
    """Store into long-term (or STM buffer) via tool action."""
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    if tier not in ("ltm", "stm"):
        raise SchemaError("tier must be ltm or stm")
    mid = hashlib.sha256(
        canonical_dumps({"c": body, "t": tier}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "tier": tier,
        "ok": True,
        "note": "agemem agemem_ltm_store",
    }


def agemem_stm_manage(*, capacity: int, used: int) -> dict[str, Any]:
    """STM context capacity gate."""
    if capacity < 1 or used < 0:
        raise SchemaError("capacity >= 1 and used >= 0")
    full = used >= capacity
    return {
        "full": full,
        "ratio": round(used / capacity, 4),
        "ok": True,
        "note": "agemem agemem_stm_manage",
    }


def agemem_retrieve(*, query: str, hits: int) -> dict[str, Any]:
    """Unified retrieve across LTM/STM."""
    q = query.strip()
    if not q:
        raise SchemaError("query required")
    if hits < 0:
        raise SchemaError("hits must be >= 0")
    return {
        "query": q[:120],
        "hits": hits,
        "ok": True,
        "note": "agemem agemem_retrieve",
    }


def agemem_summarize(*, entries: int) -> dict[str, Any]:
    """Summarize plan for context efficiency (report-only)."""
    if entries < 0:
        raise SchemaError("entries must be >= 0")
    return {
        "entries": entries,
        "ready": entries >= 2,
        "apply": False,
        "ok": True,
        "note": "agemem agemem_summarize",
    }


def agemem_discard_plan(*, memory_id: str, reason: str) -> dict[str, Any]:
    """Discard plan — never auto-deletes on core."""
    mid = memory_id.strip()
    r = reason.strip()
    if not mid or not r:
        raise SchemaError("memory_id and reason required")
    return {
        "memory_id": mid[:64],
        "reason": r[:120],
        "apply": False,
        "ok": True,
        "note": "agemem agemem_discard_plan",
    }


def agemem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → stm → retrieve → summarize."""
    order = ("store", "stm", "retrieve", "summarize")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "agemem agemem_loop_plan",
    }
