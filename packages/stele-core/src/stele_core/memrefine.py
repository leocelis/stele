"""MemRefine-shaped storage-budget compression plans (stdlib; no LLM judge).

Similarity only proposes pairs; delete/merge/preserve is deterministic heuristic.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _jaccard(a: Mapping[str, Any], b: Mapping[str, Any]) -> float:
    ta = set(tokenize(f"{a.get('title')}\n{a.get('body')}"))
    tb = set(tokenize(f"{b.get('title')}\n{b.get('body')}"))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def compress_candidates(
    entries: Sequence[Mapping[str, Any]],
    *,
    min_similarity: float = 0.45,
    limit: int = 40,
) -> dict[str, Any]:
    """Surface near-duplicate pairs (similarity propose only)."""
    if not (0 <= min_similarity <= 1):
        raise SchemaError("min_similarity must be in [0, 1]")
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested", "quarantined"}
    ]
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(pool):
        for b in pool[i + 1 :]:
            # Same scope preferred
            if a.get("scope") and b.get("scope") and a.get("scope") != b.get("scope"):
                continue
            sim = _jaccard(a, b)
            if sim < min_similarity:
                continue
            pairs.append(
                {
                    "a": a.get("id"),
                    "b": b.get("id"),
                    "similarity": round(sim, 4),
                    "title_a": a.get("title"),
                    "title_b": b.get("title"),
                }
            )
            if len(pairs) >= limit:
                break
        if len(pairs) >= limit:
            break
    pairs.sort(key=lambda p: (-float(p["similarity"]), str(p["a"]), str(p["b"])))
    return {
        "pairs": pairs,
        "count": len(pairs),
        "min_similarity": min_similarity,
        "ok": True,
        "note": "MemRefine compress_candidates — similarity propose only",
    }


def refine_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    target_count: int,
    min_similarity: float = 0.45,
) -> dict[str, Any]:
    """
    Iterate pair decisions until store ≤ target_count (report-only).

    Heuristic: sim≥0.75 → merge (keep higher helpful); 0.45–0.75 → preserve both
    unless over budget then delete lower-worth; never LLM judge.
    """
    if target_count < 1:
        raise SchemaError("target_count must be >= 1")
    pool = [
        dict(e)
        for e in entries
        if e.get("state") in {"promoted", "contested", "quarantined"}
    ]
    by_id = {str(e.get("id")): e for e in pool}
    alive = set(by_id.keys())
    actions: list[dict[str, Any]] = []

    def worth(eid: str) -> tuple[int, int, str]:
        e = by_id[eid]
        u = e.get("usage") or {}
        return (
            int(bool(u.get("pinned"))),
            int(u.get("helpful") or 0) - int(u.get("harmful") or 0),
            eid,
        )

    # Propose pairs from current alive set
    while len(alive) > target_count:
        cand = compress_candidates(
            [by_id[i] for i in alive],
            min_similarity=min_similarity,
            limit=20,
        )
        pairs = [
            p
            for p in cand.get("pairs") or []
            if p["a"] in alive and p["b"] in alive
        ]
        if not pairs:
            # Force-delete lowest worth
            worst = sorted(alive, key=worth)[0]
            actions.append(
                {
                    "action": "delete",
                    "id": worst,
                    "reason": "budget_force",
                }
            )
            alive.discard(worst)
            continue
        p = pairs[0]
        sim = float(p["similarity"])
        a, b = str(p["a"]), str(p["b"])
        if sim >= 0.75:
            keep, drop = (a, b) if worth(a) >= worth(b) else (b, a)
            actions.append(
                {
                    "action": "merge",
                    "keep": keep,
                    "drop": drop,
                    "similarity": sim,
                    "reason": "near_duplicate",
                }
            )
            alive.discard(drop)
        else:
            # Prefer delete lower worth when over budget
            drop = a if worth(a) < worth(b) else b
            actions.append(
                {
                    "action": "delete",
                    "id": drop,
                    "pair": [a, b],
                    "similarity": sim,
                    "reason": "budget_trim",
                }
            )
            alive.discard(drop)

    return {
        "target_count": target_count,
        "final_count": len(alive),
        "kept_ids": sorted(alive),
        "actions": actions,
        "action_count": len(actions),
        "ok": len(alive) <= target_count,
        "note": "MemRefine refine_plan — deterministic; not LLM pairwise judge",
    }
