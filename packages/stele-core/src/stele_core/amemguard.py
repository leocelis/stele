"""A-MemGuard-shaped consensus retrieval admit (stdlib; no LLM).

Multi-channel agreement before a hit is admitted: lexical + LINK-neighbor +
optional second query tunnel. Anomalies that only one channel supports fail.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def consensus_admit(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]],
    *,
    min_channels: int = 2,
    min_overlap: float = 0.15,
) -> dict[str, Any]:
    """
    Admit hits supported by ≥ min_channels independent signals.

    Channels: lexical_overlap, link_neighbor_of_lexical, marker_clean.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    if min_channels < 1:
        raise SchemaError("min_channels must be >= 1")
    qtok = set(tokenize(q))
    by_id = {str(e.get("id")): e for e in entries}

    # Precompute lexical neighbors
    lexical_ids: set[str] = set()
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        et = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        if qtok and len(qtok & et) / max(len(qtok), 1) >= min_overlap:
            lexical_ids.add(str(e.get("id")))

    link_support: set[str] = set()
    for eid in lexical_ids:
        e = by_id.get(eid)
        if e is None:
            continue
        for link in e.get("links") or []:
            if not isinstance(link, Mapping):
                continue
            if str(link.get("kind") or "") != "entry":
                continue
            ref = str(link.get("ref") or "")
            if ref in by_id:
                link_support.add(ref)
                link_support.add(eid)

    admitted: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for h in hits:
        eid = str(h.get("id") or "")
        e = by_id.get(eid) or h
        text = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        channels: list[str] = []
        et = set(tokenize(text))
        overlap = len(qtok & et) / max(len(qtok), 1) if qtok else 0.0
        if overlap >= min_overlap:
            channels.append("lexical")
        if eid in link_support:
            channels.append("link_neighbor")
        # marker_clean: no ignore-prior style
        low = text.lower()
        if "ignore prior" not in low and "exfiltrate" not in low:
            channels.append("marker_clean")
        else:
            channels.append("marker_dirty")
        # Count only positive channels
        positive = [c for c in channels if c != "marker_dirty"]
        if "marker_dirty" in channels:
            blocked.append(
                {
                    "id": eid,
                    "reason": "marker_dirty",
                    "channels": channels,
                }
            )
            continue
        if len(positive) >= min_channels:
            admitted.append(
                {
                    "id": eid,
                    "title": e.get("title"),
                    "channels": positive,
                    "overlap": round(overlap, 4),
                }
            )
        else:
            blocked.append(
                {
                    "id": eid,
                    "reason": "insufficient_consensus",
                    "channels": positive,
                }
            )
    return {
        "query": q,
        "admitted": admitted,
        "blocked": blocked,
        "admit_count": len(admitted),
        "block_count": len(blocked),
        "min_channels": min_channels,
        "ok": True,
        "note": "A-MemGuard consensus_admit — multi-channel; not neural consensus",
    }
