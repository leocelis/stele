"""ACM-shaped anticipate + compaction verify (stdlib; no LLM).

Anticipation = prefetch plan from related neighborhood.
Compaction verify = check critical query tokens still present after compact.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def anticipate_prefetch(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    all_entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Prefetch ids likely needed next (ACM anticipate primitive).

    Seeds from current hits' LINK refs + shared conflict_key / cue_tags / tokens.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    hit_ids = {str(h.get("id")) for h in hits if h.get("id")}
    by_id = {str(e.get("id")): e for e in all_entries}
    qtok = set(tokenize(q))
    scored: dict[str, float] = {}

    for h in hits:
        eid = str(h.get("id") or "")
        entry = by_id.get(eid) or h
        for link in entry.get("links") or []:
            if not isinstance(link, Mapping):
                continue
            if str(link.get("kind") or "") != "entry":
                continue
            ref = str(link.get("ref") or "").strip()
            if ref and ref not in hit_ids and ref in by_id:
                if by_id[ref].get("state") == "promoted":
                    scored[ref] = scored.get(ref, 0) + 1.0
        ck = str(entry.get("conflict_key") or "")
        if ck:
            for other in all_entries:
                oid = str(other.get("id") or "")
                if oid in hit_ids or oid == eid:
                    continue
                if other.get("state") != "promoted":
                    continue
                if str(other.get("conflict_key") or "") == ck:
                    scored[oid] = scored.get(oid, 0) + 0.8

    for e in all_entries:
        eid = str(e.get("id") or "")
        if eid in hit_ids or e.get("state") != "promoted":
            continue
        etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        if not qtok or not etok:
            continue
        overlap = len(qtok & etok) / max(len(qtok), 1)
        if overlap >= 0.4:
            scored[eid] = max(scored.get(eid, 0), overlap)

    ranked = sorted(scored.items(), key=lambda kv: (-kv[1], kv[0]))[: max(1, int(limit))]
    prefetch = [
        {
            "id": i,
            "score": round(s, 4),
            "title": (by_id.get(i) or {}).get("title"),
        }
        for i, s in ranked
    ]
    return {
        "query": q,
        "prefetch": prefetch,
        "count": len(prefetch),
        "seed_hits": sorted(hit_ids),
        "ok": True,
        "note": "ACM anticipate prefetch — off critical path; caller may Select",
    }


def verify_compaction(
    query: str,
    original_hits: Sequence[Mapping[str, Any]],
    compacted_text: str,
) -> dict[str, Any]:
    """
    Verifiable compaction check (ACM compacting primitive).

    Ensures query tokens that appeared in original hits remain in compacted text.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    covered_before: set[str] = set()
    for h in original_hits:
        covered_before |= set(
            tokenize(f"{h.get('title') or ''}\n{h.get('body') or ''}")
        )
    critical = sorted(qtok & covered_before)
    after = set(tokenize(compacted_text or ""))
    missing = sorted(t for t in critical if t not in after)
    return {
        "query": q,
        "critical_tokens": critical,
        "missing": missing,
        "preserved": len(critical) - len(missing),
        "total_critical": len(critical),
        "ok": len(missing) == 0,
        "note": "ACM compaction verify — fail closed if critical tokens dropped",
    }
