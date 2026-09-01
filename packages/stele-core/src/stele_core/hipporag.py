"""HippoRAG-shaped Personalized PageRank over entry LINKs (stdlib; no LLM).

Multi-hop retrieval via graph walk seeded by lexical hits — not neural PPR.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.graph import _entry_links
from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def ppr_scores(
    entries: Iterable[Mapping[str, Any]],
    seed_ids: Sequence[str],
    *,
    damping: float = 0.85,
    iterations: int = 20,
    states: set[str] | None = None,
) -> dict[str, Any]:
    """
    Personalized PageRank over undirected entry LINK graph.

    Seeds restart uniformly. Returns scores for promoted/contested nodes.
    """
    if not (0 < damping < 1):
        raise SchemaError("damping must be in (0, 1)")
    if iterations < 1 or iterations > 200:
        raise SchemaError("iterations must be 1..200")
    allow = states or {"promoted", "contested"}
    by_id = {
        str(e.get("id")): dict(e)
        for e in entries
        if e.get("id") and str(e.get("state") or "") in allow
    }
    if not by_id:
        return {"scores": {}, "seeds": [], "ok": True, "note": "empty graph"}
    seeds = [str(s) for s in seed_ids if str(s) in by_id]
    if not seeds:
        return {
            "scores": {},
            "seeds": [],
            "ok": False,
            "note": "no seed ids in graph",
        }
    adj = _entry_links(by_id)
    nodes = list(by_id.keys())
    score = {nid: 0.0 for nid in nodes}
    seed_mass = 1.0 / len(seeds)
    for s in seeds:
        score[s] = seed_mass
    for _ in range(iterations):
        nxt = {nid: 0.0 for nid in nodes}
        teleport = (1.0 - damping) / len(seeds)
        for s in seeds:
            nxt[s] += teleport
        for u in nodes:
            nbrs = [v for v in (adj.get(u) or ()) if v in nxt]
            mass = damping * score[u]
            if not nbrs:
                for s in seeds:
                    nxt[s] += mass / len(seeds)
                continue
            share = mass / len(nbrs)
            for v in nbrs:
                nxt[v] += share
        score = nxt
    ranked = sorted(score.items(), key=lambda kv: (-kv[1], kv[0]))
    return {
        "seeds": seeds,
        "scores": {k: round(v, 8) for k, v in ranked if v > 1e-12},
        "top": [
            {
                "id": k,
                "score": round(v, 8),
                "title": by_id[k].get("title"),
                "state": by_id[k].get("state"),
            }
            for k, v in ranked[:25]
            if v > 1e-12
        ],
        "nodes": len(nodes),
        "damping": damping,
        "iterations": iterations,
        "ok": True,
        "note": "HippoRAG-shaped PPR — lexical seeds + LINK graph; not neural HippoRAG",
    }


def multi_hop_retrieve(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    seed_limit: int = 5,
    result_limit: int = 10,
    damping: float = 0.85,
) -> dict[str, Any]:
    """
    Lexical seed → PPR expand for multi-hop association (MemHop/HippoRAG proxy).
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    scored: list[tuple[float, str]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        if not qtok or not etok:
            continue
        overlap = len(qtok & etok) / max(len(qtok), 1)
        if overlap > 0:
            scored.append((overlap, str(e.get("id"))))
    scored.sort(key=lambda x: (-x[0], x[1]))
    seeds = [eid for _, eid in scored[: max(1, int(seed_limit))]]
    ppr = ppr_scores(entries, seeds, damping=damping)
    top = (ppr.get("top") or [])[: max(1, int(result_limit))]
    return {
        "query": q,
        "seeds": seeds,
        "hits": top,
        "count": len(top),
        "ppr": {"damping": damping, "nodes": ppr.get("nodes")},
        "ok": True,
        "note": "HippoRAG multi-hop retrieve proxy — not MemHop paper scores",
    }
