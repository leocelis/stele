"""MemCon-shaped memory control suggestions (stdlib; no LLM / no bandit train).

Heuristic policy proxy over store features — not MemCon UCB learning.
Actions: NO_OP · RETRIEVE · RE_RETRIEVE · CONSOLIDATE · FORGET · PLAN_INJECT.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.archive import archive_plan
from stele_core.fademem import fusion_candidates
from stele_core.memr3 import evidence_gap, suggest_probes
from stele_core.schema import SchemaError

CONTROL_ACTIONS = frozenset(
    {
        "NO_OP",
        "RETRIEVE",
        "RE_RETRIEVE",
        "CONSOLIDATE",
        "FORGET",
        "PLAN_INJECT",
    }
)


def control_suggest(
    *,
    query: str,
    hits: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]],
    now: str,
    coverage_target: float = 0.85,
) -> dict[str, Any]:
    """
    One-shot MemCon-shaped action suggestion from local features.

    No learned Q-table — deterministic heuristics only.
    """
    q = str(query or "").strip()
    if coverage_target <= 0 or coverage_target > 1:
        raise SchemaError("coverage_target must be in (0, 1]")
    promoted = [e for e in entries if e.get("state") == "promoted"]
    store_n = len(promoted)
    hit_n = len(hits)
    gap = evidence_gap(q or " ", hits) if q else {
        "gaps": [{"kind": "empty_hits", "value": "*"}] if not hits else [],
        "coverage": 1.0 if hits else 0.0,
        "closed": bool(hits),
        "gap_count": 0 if hits else 1,
    }
    if not q:
        # Empty query → still allow forget/consolidate maintenance
        action = "NO_OP"
        rationale = "empty_query"
        probes: list[str] = []
    elif store_n == 0:
        action = "NO_OP"
        rationale = "empty_store"
        probes = []
    elif hit_n == 0:
        action = "RETRIEVE"
        rationale = "zero_hits"
        probes = [q]
    elif not gap.get("closed") and float(gap.get("coverage") or 0) < coverage_target:
        action = "RE_RETRIEVE"
        rationale = "evidence_gap"
        probes = suggest_probes(q, gap.get("gaps") or [])
    else:
        fuse = fusion_candidates(promoted, min_overlap=0.45, limit=5)
        arch = archive_plan(promoted, now=now, limit=5)
        skillish = [
            e
            for e in promoted
            if e.get("layer") in {"workflow", "skill_artifact", "failure_lesson"}
            and int((e.get("usage") or {}).get("helpful") or 0) >= 2
        ]
        if fuse.get("count", 0) >= 1:
            action = "CONSOLIDATE"
            rationale = "fusion_candidates"
            probes = []
        elif arch.get("count", 0) >= 1:
            action = "FORGET"
            rationale = "archive_candidates"
            probes = []
        elif skillish and "plan" in q.lower():
            action = "PLAN_INJECT"
            rationale = "reusable_plan_available"
            probes = []
        else:
            action = "RETRIEVE"
            rationale = "sufficient_coverage"
            probes = []

    assert action in CONTROL_ACTIONS
    return {
        "action": action,
        "rationale": rationale,
        "features": {
            "store_promoted": store_n,
            "hit_count": hit_n,
            "gap_count": gap.get("gap_count"),
            "coverage": gap.get("coverage"),
        },
        "next_probes": probes,
        "gap": gap if q else None,
        "ok": True,
        "note": "MemCon control suggest — heuristic proxy, not UCB bandit",
    }
