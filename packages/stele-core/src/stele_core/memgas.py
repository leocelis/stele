"""MemGAS-shaped multi-granularity association (stdlib; no LLM).

Shaped by MemGAS (arXiv:2505.19549): multi-granularity units, cluster
association, entropy-based granularity router, LLM-filter plan proxy.
Proxies only — not MemGAS paper scores. No GMM/LLM on core.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

GRANULARITIES = frozenset({"turn", "session", "topic", "summary"})


def memgas_unit(*, content: str, granularity: str) -> dict[str, Any]:
    """Create a multi-granularity memory unit."""
    body = content.strip()
    g = granularity.strip().lower()
    if not body:
        raise SchemaError("content required")
    if g not in GRANULARITIES:
        raise SchemaError(f"granularity must be one of {sorted(GRANULARITIES)}")
    uid = hashlib.sha256(
        canonical_dumps({"c": body, "g": g}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "unit_id": uid,
        "granularity": g,
        "ok": True,
        "note": "memgas memgas_unit",
    }


def memgas_associate(*, new_id: str, cluster_size: int) -> dict[str, Any]:
    """Associate a new unit with a historical cluster (GMM proxy)."""
    nid = new_id.strip()
    if not nid:
        raise SchemaError("new_id required")
    if cluster_size < 0:
        raise SchemaError("cluster_size must be >= 0")
    return {
        "new_id": nid[:64],
        "cluster_size": cluster_size,
        "associated": cluster_size >= 1,
        "ok": True,
        "note": "memgas memgas_associate",
    }


def memgas_entropy_route(*, entropy: float, low: float = 1.0) -> dict[str, Any]:
    """Entropy-based router signal for granularity selection."""
    if entropy < 0.0 or low < 0.0:
        raise SchemaError("entropy and low must be >= 0")
    focused = entropy <= low
    return {
        "focused": focused,
        "entropy": round(entropy, 4),
        "ok": True,
        "note": "memgas memgas_entropy_route",
    }


def memgas_select_granularity(*, preferred: str, entropy: float) -> dict[str, Any]:
    """Select optimal granularity balancing completeness vs noise."""
    p = preferred.strip().lower()
    if p not in GRANULARITIES:
        raise SchemaError(f"preferred must be one of {sorted(GRANULARITIES)}")
    if entropy < 0.0:
        raise SchemaError("entropy must be >= 0")
    # High entropy → coarser (summary); low → finer (turn)
    if entropy > 2.0:
        chosen = "summary"
    elif entropy > 1.0:
        chosen = "topic" if p not in ("summary",) else p
    else:
        chosen = p
    return {
        "chosen": chosen,
        "ok": True,
        "note": "memgas memgas_select_granularity",
    }


def memgas_filter_plan(*, candidates: int, keep: int) -> dict[str, Any]:
    """Post-retrieve filter plan (LLM-filter proxy; report-only)."""
    if candidates < 0 or keep < 0:
        raise SchemaError("candidates and keep must be >= 0")
    return {
        "candidates": candidates,
        "keep": min(keep, candidates),
        "apply": False,
        "ok": True,
        "note": "memgas memgas_filter_plan",
    }


def memgas_loop_plan(*, phase: str) -> dict[str, Any]:
    """Unit → associate → route → select."""
    order = ("unit", "associate", "route", "select")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "unit"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memgas memgas_loop_plan",
    }
