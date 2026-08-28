"""H-MEM abstraction-level hierarchy (stdlib; no LLM).

Shaped by H-MEM (arXiv:2507.22925): four semantic abstraction levels
(section → subsection → subsubsection → content) with index-based routing.
Proxies only — not H-MEM paper scores. Distinct from hybrid H-Mem (2605.15701).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

LEVELS = frozenset(
    {"section", "subsection", "subsubsection", "content"}
)


def hmeml_store_level(
    *,
    level: str,
    content: str,
) -> dict[str, Any]:
    """Store memory at a semantic abstraction level."""
    if level not in LEVELS:
        raise SchemaError(f"level must be one of {sorted(LEVELS)}")
    body = content.strip()
    if not body:
        raise SchemaError("content required")
    mid = hashlib.sha256(
        canonical_dumps({"l": level, "c": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entry_id": mid,
        "level": level,
        "content": body[:200],
        "ok": True,
        "note": "hmeml hmeml_store_level",
    }


def hmeml_route_query(
    *,
    start_level: str,
) -> dict[str, Any]:
    """Index-based routing starts at a level and may descend."""
    if start_level not in LEVELS:
        raise SchemaError(f"start_level must be one of {sorted(LEVELS)}")
    order = ["section", "subsection", "subsubsection", "content"]
    idx = order.index(start_level)
    path = order[idx:]
    return {
        "path": path,
        "start_level": start_level,
        "ok": True,
        "note": "hmeml hmeml_route_query",
    }


def hmeml_descend(
    *,
    current_level: str,
    hit: bool,
) -> dict[str, Any]:
    """Descend one level when current index miss; stop on hit."""
    if current_level not in LEVELS:
        raise SchemaError(f"current_level must be one of {sorted(LEVELS)}")
    order = ["section", "subsection", "subsubsection", "content"]
    idx = order.index(current_level)
    if hit:
        return {
            "action": "stop",
            "level": current_level,
            "ok": True,
            "note": "hmeml hmeml_descend",
        }
    if idx + 1 >= len(order):
        return {
            "action": "exhausted",
            "level": current_level,
            "ok": True,
            "note": "hmeml hmeml_descend",
        }
    return {
        "action": "descend",
        "level": order[idx + 1],
        "ok": True,
        "note": "hmeml hmeml_descend",
    }


def hmeml_parent_link(
    *,
    parent_level: str,
    child_level: str,
) -> dict[str, Any]:
    """Validate parent→child adjacency in the hierarchy."""
    order = ["section", "subsection", "subsubsection", "content"]
    if parent_level not in LEVELS or child_level not in LEVELS:
        raise SchemaError("levels must be valid hierarchy levels")
    pi, ci = order.index(parent_level), order.index(child_level)
    adjacent = ci == pi + 1
    return {
        "adjacent": adjacent,
        "parent_level": parent_level,
        "child_level": child_level,
        "ok": True,
        "note": "hmeml hmeml_parent_link",
    }


def hmeml_efficiency_score(
    *,
    levels_scanned: int,
    max_levels: int = 4,
) -> dict[str, Any]:
    """Efficiency proxy: fewer levels scanned is better (1 − scanned/max)."""
    if levels_scanned < 0 or max_levels < 1:
        raise SchemaError("levels_scanned >= 0 and max_levels >= 1")
    score = max(0.0, 1.0 - (levels_scanned / max_levels))
    return {
        "score": round(score, 4),
        "levels_scanned": levels_scanned,
        "ok": True,
        "note": "hmeml hmeml_efficiency_score",
    }


def hmeml_loop_plan(*, phase: str) -> dict[str, Any]:
    """Store → route → descend → score."""
    order = ("store", "route", "descend", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "store"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hmeml hmeml_loop_plan",
    }
