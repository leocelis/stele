"""Maieutic Prompting proxies (stdlib; no LLM).

Shaped by Maieutic Prompting (arXiv:2205.11822): abductive explanation
tree, recurse, satisfiability over relations. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mai_abduce(*, claim: str, because: str) -> dict[str, Any]:
    """Abductive explanation node (X is true, because…)."""
    c = claim.strip()
    b = because.strip()
    if not c or not b:
        raise SchemaError("claim and because required")
    nid = hashlib.sha256(
        canonical_dumps({"c": c, "b": b}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "node_id": nid,
        "ok": True,
        "note": "maieutic mai_abduce",
    }


def mai_recurse(*, node_id: str, depth: int) -> dict[str, Any]:
    """Recursively expand the explanation tree."""
    nid = node_id.strip()
    if not nid:
        raise SchemaError("node_id required")
    if depth < 0:
        raise SchemaError("depth must be >= 0")
    rid = hashlib.sha256(
        canonical_dumps({"n": nid, "d": depth}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tree_id": rid,
        "depth": depth,
        "ok": True,
        "note": "maieutic mai_recurse",
    }


def mai_sat(*, relations: int) -> dict[str, Any]:
    """Frame inference as satisfiability over explanation relations."""
    if relations < 0:
        raise SchemaError("relations must be >= 0")
    return {
        "relations": relations,
        "ok": True,
        "note": "maieutic mai_sat",
    }


def mai_consistent(*, consistent: bool) -> dict[str, Any]:
    """Flag logically consistent answer from noisy explanations."""
    return {
        "consistent": consistent,
        "ok": True,
        "note": "maieutic mai_consistent",
    }


def mai_unreliable(*, tolerate: bool) -> dict[str, Any]:
    """Flag tolerance of unreliable LM explanations (report-only)."""
    return {
        "tolerate": tolerate,
        "apply": False,
        "ok": True,
        "note": "maieutic mai_unreliable",
    }


def mai_loop_plan(*, phase: str) -> dict[str, Any]:
    """Abduce → recurse → sat → consistent."""
    order = ("abduce", "recurse", "sat", "consistent")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "abduce"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "maieutic mai_loop_plan",
    }
