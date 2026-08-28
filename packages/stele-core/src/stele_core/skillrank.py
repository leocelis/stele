"""Skill-library hybrid ranker (stdlib; no dense embeddings).

Comparative skill-retrieval finding (arXiv:2608.06196): hybrid lexical ranker
is the workhorse; typed graphs rarely extend reach. We ship lexical skill_rank
+ LINK-based prereq expand — not an LLM edge layer.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def skill_rank(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 5,
) -> dict[str, Any]:
    """Rank skill_artifact (+ crystallized workflow) entries for a query."""
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    scored: list[tuple[float, dict[str, Any]]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        layer = str(e.get("layer") or "")
        if layer not in {"skill_artifact", "workflow"}:
            continue
        blob = f"{e.get('title')}\n{e.get('body')}"
        etok = set(tokenize(blob))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        pin = 0.1 if (e.get("usage") or {}).get("pinned") else 0.0
        helpful = int((e.get("usage") or {}).get("helpful") or 0)
        score = round(overlap + pin + min(0.2, helpful * 0.02), 6)
        if score <= 0:
            continue
        scored.append(
            (
                score,
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "layer": layer,
                    "score": score,
                },
            )
        )
    scored.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    hits = [row for _, row in scored[: max(1, int(limit))]]
    return {
        "query": q,
        "hits": hits,
        "count": len(hits),
        "ok": True,
        "note": "skill_rank — lexical hybrid proxy; not dense+LLM graph edges",
    }


def skill_prereq_expand(
    skill_id: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    depth: int = 2,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Expand prerequisites via entry LINKs (workflow relations proxy).
    Does not invent edges the ranker could not already see.
    """
    sid = str(skill_id or "").strip()
    if not sid:
        raise SchemaError("skill_id is required")
    if depth < 1:
        raise SchemaError("depth must be >= 1")
    by_id = {str(e.get("id")): e for e in entries}
    root = by_id.get(sid)
    if root is None:
        raise SchemaError(f"unknown skill: {sid}")
    seen = {sid}
    frontier = [sid]
    edges: list[dict[str, Any]] = []
    for _ in range(int(depth)):
        nxt: list[str] = []
        for cur in frontier:
            e = by_id.get(cur)
            if e is None:
                continue
            for link in e.get("links") or []:
                if not isinstance(link, Mapping):
                    continue
                if str(link.get("kind") or "") != "entry":
                    continue
                ref = str(link.get("ref") or "")
                if not ref or ref in seen:
                    continue
                other = by_id.get(ref)
                if other is None:
                    continue
                if other.get("layer") not in {
                    "skill_artifact",
                    "workflow",
                    "decision",
                }:
                    continue
                seen.add(ref)
                nxt.append(ref)
                edges.append(
                    {
                        "from": cur,
                        "to": ref,
                        "title": other.get("title"),
                        "layer": other.get("layer"),
                        "relation": "prereq_or_dep",
                    }
                )
                if len(edges) >= limit:
                    break
            if len(edges) >= limit:
                break
        frontier = nxt
        if not frontier or len(edges) >= limit:
            break
    return {
        "skill_id": sid,
        "root_title": root.get("title"),
        "edges": edges,
        "count": len(edges),
        "reachable_ids": sorted(seen - {sid}),
        "ok": True,
        "note": "skill_prereq_expand — LINK walk only; graph cannot extend ranker reach",
    }
