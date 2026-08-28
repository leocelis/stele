"""GAM-shaped episodic buffer + semantic boundary + consolidate plan (stdlib).

Decouples fast buffering of recent quarantine from stable promoted memory.
Consolidation is a plan — never auto-promotes (C7).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def jaccard(a: str, b: str) -> float:
    ta = set(tokenize(a))
    tb = set(tokenize(b))
    if not ta and not tb:
        return 1.0
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / max(len(ta | tb), 1)


def semantic_boundary(
    previous: str,
    current: str,
    *,
    threshold: float = 0.35,
) -> dict[str, Any]:
    """
    Detect a topic shift between two text blobs (GAM semantic indicator proxy).

    Low Jaccard → shift / consolidate trigger.
    """
    if not (0 < threshold <= 1):
        raise SchemaError("threshold must be in (0, 1]")
    score = round(jaccard(previous or "", current or ""), 6)
    shift = score < threshold
    return {
        "overlap": score,
        "threshold": threshold,
        "shift": shift,
        "action": "consolidate" if shift else "keep_buffering",
        "note": "GAM semantic-boundary proxy — not LLM topic shift",
    }


def episodic_buffer(
    entries: Iterable[Mapping[str, Any]],
    *,
    limit: int = 20,
) -> dict[str, Any]:
    """Recent quarantined entries as the episodic buffer surface."""
    rows = [
        {
            "id": e.get("id"),
            "title": e.get("title"),
            "layer": e.get("layer"),
            "scope": e.get("scope"),
            "written_at": (e.get("provenance") or {}).get("written_at"),
        }
        for e in entries
        if e.get("state") == "quarantined"
    ]
    rows.sort(key=lambda r: str(r.get("written_at") or ""), reverse=True)
    rows = rows[: max(1, int(limit))]
    return {
        "buffer": rows,
        "count": len(rows),
        "ok": True,
        "note": "GAM episodic buffer — quarantined only; promote still needs oracle",
    }


def consolidate_candidates(
    buffer_entries: Sequence[Mapping[str, Any]],
    promoted_entries: Sequence[Mapping[str, Any]],
    *,
    min_overlap: float = 0.25,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Plan merges of buffer items into topic neighborhood (report only).

    Suggests LINK or supersede review — never writes.
    """
    if not (0 < min_overlap <= 1):
        raise SchemaError("min_overlap must be in (0, 1]")
    pairs: list[dict[str, Any]] = []
    for b in buffer_entries:
        b_tok = set(tokenize(f"{b.get('title')}\n{b.get('body') or ''}"))
        best = None
        best_score = 0.0
        for p in promoted_entries:
            if p.get("state") != "promoted":
                continue
            if b.get("scope") and p.get("scope") and b.get("scope") != p.get("scope"):
                continue
            p_tok = set(tokenize(f"{p.get('title')}\n{p.get('body')}"))
            if not b_tok or not p_tok:
                continue
            score = len(b_tok & p_tok) / max(len(b_tok | p_tok), 1)
            if score > best_score:
                best_score = score
                best = p
        if best is not None and best_score >= min_overlap:
            pairs.append(
                {
                    "buffer_id": b.get("id"),
                    "topic_id": best.get("id"),
                    "overlap": round(best_score, 4),
                    "action": "link_or_review",
                    "titles": [b.get("title"), best.get("title")],
                }
            )
        else:
            pairs.append(
                {
                    "buffer_id": b.get("id"),
                    "topic_id": None,
                    "overlap": round(best_score, 4),
                    "action": "new_topic_candidate",
                    "titles": [b.get("title"), None],
                }
            )
    pairs.sort(key=lambda r: (-float(r.get("overlap") or 0), str(r.get("buffer_id"))))
    pairs = pairs[: max(1, int(limit))]
    return {
        "candidates": pairs,
        "count": len(pairs),
        "ok": True,
        "note": "GAM consolidate plan — never auto-promotes (C7)",
    }
