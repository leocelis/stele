"""DCPM-shaped dual-process cognitive memory (stdlib; no LLM).

Shaped by DCPM (arXiv:2606.09483): daytime System-1 belief supersedes chains,
nighttime System-2 schema/intention induction and cross-domain collision
abstraction. Proxies only — not DCPM paper scores. Distinct from D-Mem quality
gate in roles.py (arXiv:2603.18631).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

HIERARCHY = frozenset(
    {
        "raw",
        "fact",
        "belief",
        "identity",
        "schema",
        "intention",
        "core_schema",
    }
)


def dcpm_day_write(
    *,
    belief: str,
    superseded_id: str | None = None,
) -> dict[str, Any]:
    """System 1 daytime writer: record belief; optional supersedes link."""
    body = belief.strip()
    if not body:
        raise SchemaError("belief required")
    bid = hashlib.sha256(
        canonical_dumps({"b": body, "s": superseded_id or ""}).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return {
        "belief_id": bid,
        "supersedes": (superseded_id or "").strip()[:64] or None,
        "ok": True,
        "note": "dcpm dcpm_day_write",
    }


def dcpm_supersedes_chain(
    *,
    chain_len: int,
) -> dict[str, Any]:
    """Doubly linked supersedes chain length proxy."""
    if chain_len < 1:
        raise SchemaError("chain_len must be >= 1")
    return {
        "chain_len": chain_len,
        "bidirectional": True,
        "ok": True,
        "note": "dcpm dcpm_supersedes_chain",
    }


def dcpm_night_induce(
    *,
    fact_cluster_size: int,
    min_cluster: int = 3,
) -> dict[str, Any]:
    """System 2 nighttime: induce schema when cluster is large enough."""
    if fact_cluster_size < 0 or min_cluster < 1:
        raise SchemaError("fact_cluster_size >= 0 and min_cluster >= 1")
    induce = fact_cluster_size >= min_cluster
    return {
        "induce": induce,
        "fact_cluster_size": fact_cluster_size,
        "ok": True,
        "note": "dcpm dcpm_night_induce",
    }


def dcpm_cross_domain_collision(
    *,
    behavioral_similarity: float,
    semantic_similarity: float,
    behavior_threshold: float = 0.7,
    semantic_max: float = 0.3,
) -> dict[str, Any]:
    """Collision: high behavioral similarity, low semantic similarity."""
    for v in (
        behavioral_similarity,
        semantic_similarity,
        behavior_threshold,
        semantic_max,
    ):
        if not (0.0 <= v <= 1.0):
            raise SchemaError("similarities/thresholds must be in [0, 1]")
    collision = (
        behavioral_similarity >= behavior_threshold
        and semantic_similarity <= semantic_max
    )
    return {
        "collision": collision,
        "abstract_to_core": collision,
        "apply": False,
        "ok": True,
        "note": "dcpm dcpm_cross_domain_collision",
    }


def dcpm_hierarchy_level(*, level: str) -> dict[str, Any]:
    """Validate placement on the cognitive capability hierarchy."""
    if level not in HIERARCHY:
        raise SchemaError(f"level must be one of {sorted(HIERARCHY)}")
    return {
        "level": level,
        "ok": True,
        "note": "dcpm dcpm_hierarchy_level",
    }


def dcpm_loop_plan(*, phase: str) -> dict[str, Any]:
    """Day write → night induce → collision abstract."""
    order = ("day", "night", "collision")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "day"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dcpm dcpm_loop_plan",
    }
