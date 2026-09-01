"""MemForest/MemTree-shaped hierarchical temporal index (stdlib; no LLM).

Time-ordered trees per scope: leaves = evidence, internals = interval digests,
root = coarse forest entry. Localized dirty-path updates — not full-state rewrite.
Coarse-to-fine retrieval navigates root → interval → leaf.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _ts(e: Mapping[str, Any]) -> str:
    t = e.get("temporal") if isinstance(e.get("temporal"), Mapping) else {}
    return str(
        t.get("valid_from")
        or (e.get("provenance") or {}).get("written_at")
        or ""
    )


def build_memtree(
    entries: Sequence[Mapping[str, Any]],
    *,
    scope: str | None = None,
    bucket_hours: int = 24,
) -> dict[str, Any]:
    """
    Build a MemTree over promoted/contested tips (report-only structure).

    Leaves sorted by time; internal nodes summarize contiguous buckets;
    one root per scope.
    """
    if bucket_hours < 1:
        raise SchemaError("bucket_hours must be >= 1")
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested"}
        and (scope is None or e.get("scope") == scope)
    ]
    pool.sort(key=lambda e: (_ts(e), str(e.get("id"))))
    leaves: list[dict[str, Any]] = []
    for e in pool:
        leaves.append(
            {
                "id": e.get("id"),
                "level": "leaf",
                "title": e.get("title"),
                "ts": _ts(e),
                "scope": e.get("scope"),
            }
        )

    # Bucket by day prefix of ISO ts (YYYY-MM-DD) as cheap temporal interval
    buckets: dict[str, list[dict[str, Any]]] = {}
    for leaf in leaves:
        day = (leaf.get("ts") or "unknown")[:10]
        buckets.setdefault(day, []).append(leaf)

    internals: list[dict[str, Any]] = []
    for day, kids in sorted(buckets.items()):
        titles = [str(k.get("title") or "") for k in kids]
        internals.append(
            {
                "id": f"interval:{day}",
                "level": "interval",
                "valid_from": day,
                "valid_to": day,
                "child_ids": [k["id"] for k in kids],
                "summary": " | ".join(t for t in titles if t)[:200],
                "leaf_count": len(kids),
            }
        )

    root = {
        "id": f"root:{(scope or 'all')}",
        "level": "root",
        "scope": scope,
        "child_ids": [n["id"] for n in internals],
        "interval_count": len(internals),
        "leaf_count": len(leaves),
        "summary": f"{len(leaves)} leaves / {len(internals)} intervals",
    }
    return {
        "root": root,
        "intervals": internals,
        "leaves": leaves,
        "ok": True,
        "note": "MemTree build_memtree — hierarchical temporal index; files remain SoT",
    }


def dirty_path_plan(
    tree: Mapping[str, Any],
    new_entry: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Localized maintenance path for a new tip (affected nodes only).

    Not a global profile rewrite — dirty = matching day interval + root.
    """
    if not tree.get("root"):
        raise SchemaError("tree.root required")
    day = (_ts(new_entry) or "unknown")[:10]
    intervals = tree.get("intervals") or []
    hit = next(
        (i for i in intervals if str(i.get("valid_from")) == day),
        None,
    )
    path = [tree["root"]["id"]]
    if hit:
        path.append(hit["id"])
        action = "update_interval"
    else:
        action = "create_interval"
        path.append(f"interval:{day}")
    path.append(f"leaf:{new_entry.get('id') or 'new'}")
    return {
        "action": action,
        "dirty_path": path,
        "day": day,
        "global_rewrite": False,
        "nodes_touched": len(path),
        "ok": True,
        "note": "MemForest dirty_path_plan — cost ∝ path, not store size",
    }


def coarse_to_fine(
    query: str,
    tree: Mapping[str, Any],
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 8,
) -> dict[str, Any]:
    """
    Coarse→fine retrieval: score intervals by summary overlap, then leaves.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    by_id = {str(e.get("id")): e for e in entries}
    scored_intervals: list[dict[str, Any]] = []
    for node in tree.get("intervals") or []:
        stok = set(tokenize(str(node.get("summary") or "")))
        overlap = len(qtok & stok) / max(len(qtok), 1) if qtok else 0.0
        if overlap <= 0:
            continue
        scored_intervals.append(
            {
                "id": node.get("id"),
                "score": round(overlap, 4),
                "summary": node.get("summary"),
                "child_ids": node.get("child_ids") or [],
            }
        )
    scored_intervals.sort(key=lambda x: (-x["score"], str(x["id"])))

    leaves_out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for iv in scored_intervals:
        for cid in iv.get("child_ids") or []:
            if cid in seen:
                continue
            e = by_id.get(str(cid))
            if e is None:
                continue
            etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
            score = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
            if score <= 0:
                continue
            seen.add(str(cid))
            leaves_out.append(
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "score": round(score, 4),
                    "via_interval": iv.get("id"),
                    "level": "leaf",
                }
            )
            if len(leaves_out) >= limit:
                break
        if len(leaves_out) >= limit:
            break
    leaves_out.sort(key=lambda x: (-x["score"], str(x["id"])))
    return {
        "query": q,
        "intervals": scored_intervals[: max(1, limit // 2)],
        "leaves": leaves_out[:limit],
        "count": len(leaves_out[:limit]),
        "ok": True,
        "note": "MemForest coarse_to_fine — interval then leaf; not flat top-k only",
    }
