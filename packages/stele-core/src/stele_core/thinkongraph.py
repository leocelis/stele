"""Think-on-Graph-shaped KG beam explore (stdlib; no LLM / no live KG).

Shaped by Think-on-Graph (arXiv:2307.07697): explore neighbors, beam prune,
score paths, answer from paths. Proxies only — not Freebase / Wikidata.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tog_init_entity(*, entity: str) -> dict[str, Any]:
    """Seed exploration at an entity."""
    e = entity.strip()
    if not e:
        raise SchemaError("entity required")
    eid = hashlib.sha256(
        canonical_dumps({"e": e}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "entity_id": eid,
        "ok": True,
        "note": "tog tog_init_entity",
    }


def tog_explore_neighbors(*, entity_id: str, width: int = 3) -> dict[str, Any]:
    """Expand beam width over neighbor triples (proxy count)."""
    eid = entity_id.strip()
    if not eid:
        raise SchemaError("entity_id required")
    if width < 1:
        raise SchemaError("width must be >= 1")
    return {
        "neighbors": width,
        "entity_id": eid[:64],
        "ok": True,
        "note": "tog tog_explore_neighbors",
    }


def tog_beam_prune(*, paths: int, keep: int) -> dict[str, Any]:
    """Prune beam to top-k paths (report-only)."""
    if paths < 0 or keep < 0:
        raise SchemaError("paths and keep must be >= 0")
    if keep > paths:
        raise SchemaError("keep must be <= paths")
    return {
        "kept": keep,
        "pruned": paths - keep,
        "apply": False,
        "ok": True,
        "note": "tog tog_beam_prune",
    }


def tog_path_score(*, path_id: str, score: float) -> dict[str, Any]:
    """Score a reasoning path (0..1 proxy)."""
    pid = path_id.strip()
    if not pid:
        raise SchemaError("path_id required")
    if score < 0.0 or score > 1.0:
        raise SchemaError("score must be in [0, 1]")
    return {
        "path_id": pid[:64],
        "score": score,
        "ok": True,
        "note": "tog tog_path_score",
    }


def tog_answer_from_paths(*, path_count: int) -> dict[str, Any]:
    """Compose answer from retained reasoning paths."""
    if path_count < 0:
        raise SchemaError("path_count must be >= 0")
    return {
        "path_count": path_count,
        "answered": path_count > 0,
        "ok": True,
        "note": "tog tog_answer_from_paths",
    }


def tog_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → explore → prune → answer."""
    order = ("init", "explore", "prune", "answer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tog tog_loop_plan",
    }
