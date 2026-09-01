"""MemStrata-shaped deterministic supersession (stdlib; no LLM on read path)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from stele_core.schema import SchemaError


def supersession_winners(
    entries: Iterable[Mapping[str, Any]],
) -> dict[str, str]:
    """
    Map conflict_key → current winning promoted entry id.

    Prefers tip of superseded_by chain; else newest last_verified among promoted
    sharing the key. Deterministic — MemStrata-shaped (no similarity threshold).
    """
    by_id = {str(e.get("id")): e for e in entries}
    by_key: dict[str, list[str]] = {}
    for eid, e in by_id.items():
        key = e.get("conflict_key")
        if not key:
            continue
        by_key.setdefault(str(key), []).append(eid)

    winners: dict[str, str] = {}
    for key, ids in by_key.items():
        # Follow superseded_by to tip when present
        tips: list[str] = []
        for eid in ids:
            cur = eid
            seen: set[str] = set()
            while cur and cur not in seen:
                seen.add(cur)
                e = by_id.get(cur)
                if e is None:
                    break
                nxt = (e.get("temporal") or {}).get("superseded_by")
                if not nxt:
                    tips.append(cur)
                    break
                cur = str(nxt)
        # Among tips that are promoted, pick newest last_verified
        promoted_tips = [
            t
            for t in tips
            if by_id.get(t) and by_id[t].get("state") == "promoted"
        ]
        if not promoted_tips:
            # fallback: newest promoted with this key
            promoted = [
                i
                for i in ids
                if by_id.get(i) and by_id[i].get("state") == "promoted"
            ]
            if not promoted:
                continue
            promoted.sort(
                key=lambda i: str(
                    (by_id[i].get("temporal") or {}).get("last_verified") or ""
                ),
                reverse=True,
            )
            winners[key] = promoted[0]
            continue
        promoted_tips.sort(
            key=lambda i: str(
                (by_id[i].get("temporal") or {}).get("last_verified") or ""
            ),
            reverse=True,
        )
        winners[key] = promoted_tips[0]
    return winners


def stale_fact_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Report promoted entries that are superseded (state or not current winner).

    MemStrata stale-fact-error class — RAG would still retrieve these.
    """
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    entries_list = list(entries)
    winners = supersession_winners(entries_list)
    stale: list[dict[str, Any]] = []
    for e in entries_list:
        if len(stale) >= limit:
            break
        state = str(e.get("state") or "")
        if state not in {"promoted", "superseded"}:
            continue
        eid = str(e.get("id") or "")
        key = e.get("conflict_key")
        reasons: list[str] = []
        if state == "superseded":
            reasons.append("state_superseded")
        if key and winners.get(str(key)) and winners[str(key)] != eid:
            reasons.append("not_current_winner")
        sb = (e.get("temporal") or {}).get("superseded_by")
        if sb:
            reasons.append(f"superseded_by:{sb}")
        if reasons:
            stale.append(
                {
                    "id": eid,
                    "conflict_key": key,
                    "state": state,
                    "winner": winners.get(str(key)) if key else None,
                    "reasons": reasons,
                    "title": e.get("title"),
                }
            )
    return {
        "stale": stale,
        "count": len(stale),
        "winner_count": len(winners),
        "note": "MemStrata-shaped stale-fact scan — exclude via exclude_superseded Select",
    }


def is_current_fact(
    entry: Mapping[str, Any],
    winners: Mapping[str, str],
) -> bool:
    """True if entry should appear under exclude_superseded Select."""
    state = str(entry.get("state") or "")
    if state == "superseded":
        return False
    if state != "promoted":
        return True  # contested etc. handled elsewhere
    key = entry.get("conflict_key")
    if not key:
        return True
    winner = winners.get(str(key))
    if winner is None:
        return True
    return str(entry.get("id")) == winner
