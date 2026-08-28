"""AgentIR-shaped cascade routing + multi-channel RRF fusion (stdlib; no LLM).

Channels: lexical · ppr · residual. Cascade may skip expensive channels when
lexical margin is decisive.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.hipporag import multi_hop_retrieve
from stele_core.index.lexical import tokenize
from stele_core.prograph import extract_residuals
from stele_core.retrieval import rrf_fuse
from stele_core.schema import SchemaError


def cascade_route(
    query: str,
    lexical_hits: Sequence[Mapping[str, Any]],
    *,
    margin_threshold: float = 0.25,
) -> dict[str, Any]:
    """
    Decide whether to run PPR channel from lexical top-k margin.

    High margin → lexical_only; else full_rrf.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    if not (0 <= margin_threshold <= 1):
        raise SchemaError("margin_threshold must be in [0, 1]")
    qtok = set(tokenize(q))
    scores: list[float] = []
    for h in lexical_hits[:5]:
        etok = set(tokenize(f"{h.get('title') or ''}\n{h.get('body') or ''}"))
        scores.append(len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0)
    top = scores[0] if scores else 0.0
    second = scores[1] if len(scores) > 1 else 0.0
    margin = round(top - second, 6)
    mode = "lexical_only" if margin >= margin_threshold and top > 0 else "full_rrf"
    return {
        "query": q,
        "mode": mode,
        "margin": margin,
        "threshold": margin_threshold,
        "top_score": round(top, 6),
        "skip_ppr": mode == "lexical_only",
        "ok": True,
        "note": "AgentIR cascade route — margin-triggered channel skip",
    }


def multi_channel_fuse(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    lexical_hits: Sequence[Mapping[str, Any]],
    *,
    k: int = 60,
    result_limit: int = 10,
    force_full: bool = False,
) -> dict[str, Any]:
    """
    Fuse lexical + optional PPR + residual channels via RRF.
    """
    route = cascade_route(query, lexical_hits)
    lex_rank = [
        (str(h.get("id")), float(i))
        for i, h in enumerate(lexical_hits)
        if h.get("id")
    ]
    rankings: list[list[tuple[str, float]]] = [lex_rank]
    channels = ["lexical"]
    ppr_hits: list[dict[str, Any]] = []
    if force_full or not route.get("skip_ppr"):
        mh = multi_hop_retrieve(query, entries, result_limit=result_limit)
        ppr_hits = list(mh.get("hits") or [])
        rankings.append(
            [
                (str(h.get("id")), float(h.get("score") or 0))
                for h in ppr_hits
                if h.get("id")
            ]
        )
        channels.append("ppr")

    # residual channel: rank by residual hit count vs query
    qtok = set(tokenize(query))
    res_scored: list[tuple[str, float]] = []
    by_id = {str(e.get("id")): e for e in entries}
    cand_ids = {eid for ranking in rankings for eid, _ in ranking}
    for eid in cand_ids:
        e = by_id.get(eid)
        if e is None:
            continue
        res = extract_residuals(e)
        hit = 0
        for r in res.get("residuals") or []:
            val = str(r.get("value") or "").lower()
            if any(t in val for t in qtok if len(t) > 2):
                hit += 1
        if hit:
            res_scored.append((eid, float(hit)))
    res_scored.sort(key=lambda x: (-x[1], x[0]))
    if res_scored:
        rankings.append(res_scored)
        channels.append("residual")

    fused_ids = rrf_fuse(rankings, k=k)[: max(1, int(result_limit))]
    hits = []
    for eid in fused_ids:
        e = by_id.get(eid) or {}
        hits.append(
            {
                "id": eid,
                "title": e.get("title"),
                "state": e.get("state"),
            }
        )
    return {
        "query": query,
        "route": route,
        "channels": channels,
        "hits": hits,
        "count": len(hits),
        "rrf_k": k,
        "ok": True,
        "note": "AgentIR multi-channel RRF — lexical±ppr±residual; not AgentIR paper latency",
    }
