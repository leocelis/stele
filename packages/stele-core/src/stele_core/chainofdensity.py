"""Chain of Density proxies (stdlib; no LLM).

Shaped by Chain of Density (arXiv:2309.04269): sparse summary →
identify missing entities → fuse without growing length. Proxies only.

Prefix ``cod_*`` — Chain of Density, not code / CoVe.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cod_sparse(*, source: str) -> dict[str, Any]:
    """Generate an initial entity-sparse summary."""
    s = source.strip()
    if not s:
        raise SchemaError("source required")
    sid = hashlib.sha256(
        canonical_dumps({"s": s}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sparse_id": sid,
        "ok": True,
        "note": "cod dens cod_sparse",
    }


def cod_entities(*, sparse_id: str, count: int) -> dict[str, Any]:
    """Identify missing salient entities to fuse."""
    sid = sparse_id.strip()
    if not sid:
        raise SchemaError("sparse_id required")
    if count < 1:
        raise SchemaError("count must be >= 1")
    eid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entity_id": eid,
        "count": count,
        "ok": True,
        "note": "cod dens cod_entities",
    }


def cod_fuse(*, entity_id: str) -> dict[str, Any]:
    """Fuse entities into the summary without increasing length."""
    eid = entity_id.strip()
    if not eid:
        raise SchemaError("entity_id required")
    fid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dense_id": fid,
        "ok": True,
        "note": "cod dens cod_fuse",
    }


def cod_length(*, fixed: bool) -> dict[str, Any]:
    """Flag fixed-length constraint across densification turns."""
    return {
        "fixed": fixed,
        "ok": True,
        "note": "cod dens cod_length",
    }


def cod_tradeoff(*, prefer_dense: bool) -> dict[str, Any]:
    """Flag informativeness vs readability tradeoff (report-only)."""
    return {
        "prefer_dense": prefer_dense,
        "apply": False,
        "ok": True,
        "note": "cod dens cod_tradeoff",
    }


def cod_loop_plan(*, phase: str) -> dict[str, Any]:
    """Sparse → entities → fuse → length."""
    order = ("sparse", "entities", "fuse", "length")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "sparse"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cod dens cod_loop_plan",
    }
