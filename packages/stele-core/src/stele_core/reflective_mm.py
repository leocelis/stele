"""RMM-shaped Reflective Memory Management for dialogue (stdlib; no LLM).

Shaped by Reflective Memory Management (arXiv:2503.08026 / ACL 2025):
Prospective Reflection (topic-based memory across utterance/turn/session),
Retrospective Reflection (cite feedback → refine retrieval), lightweight
rerank. Proxies only — not RMM paper scores. Distinct from RRM (rrm.py).
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
GRANULARITIES = frozenset({"utterance", "turn", "session"})


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def prospective_reflect(
    *,
    topic: str,
    segment: str,
    granularity: str = "turn",
) -> dict[str, Any]:
    """Prospective Reflection: (topic summary, dialogue segment) memory unit."""
    if granularity not in GRANULARITIES:
        raise SchemaError(f"granularity must be one of {sorted(GRANULARITIES)}")
    if not isinstance(topic, str) or not topic.strip():
        raise SchemaError("topic required")
    if not isinstance(segment, str) or not segment.strip():
        raise SchemaError("segment required")
    mid = hashlib.sha256(
        canonical_dumps(
            {"t": topic, "g": granularity, "s": segment[:160]}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "topic": topic.strip()[:80],
        "segment": segment.strip()[:240],
        "granularity": granularity,
        "cite_count": 0,
        "retrieval_weight": 1.0,
        "ok": True,
        "note": "rmm_dialogue prospective_reflect",
    }


def topic_memory_bank(
    memories: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Index topic bank: group by topic key."""
    by_topic: dict[str, list[dict[str, Any]]] = {}
    for m in memories:
        if not isinstance(m, Mapping):
            continue
        key = str(m.get("topic") or "").strip().lower() or "_untagged"
        by_topic.setdefault(key, []).append(dict(m))
    return {
        "topics": sorted(by_topic.keys()),
        "by_topic": by_topic,
        "memory_count": sum(len(v) for v in by_topic.values()),
        "ok": True,
        "note": "rmm_dialogue topic_memory_bank",
    }


def retrieve_topic_memories(
    memories: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Initial retrieve by topic/segment overlap × retrieval_weight."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for m in memories:
        if not isinstance(m, Mapping):
            continue
        blob = f"{m.get('topic') or ''} {m.get('segment') or ''}"
        overlap = len(qtok & _tokens(blob))
        weight = float(m.get("retrieval_weight") or 1.0)
        scored.append((overlap * weight, dict(m)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("memory_id") or "")))
    hits = [m for sc, m in scored[:top_k] if sc >= 0]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "rmm_dialogue retrieve_topic_memories",
    }


def retrospective_cite_feedback(
    *,
    cited_ids: Sequence[str],
    all_retrieved_ids: Sequence[str],
) -> dict[str, Any]:
    """
    Retrospective Reflection signal: which retrieved memories the LLM cited.
    Cited → positive; retrieved-but-uncited → soft negative.
    """
    cited = {str(i) for i in cited_ids if i}
    retrieved = {str(i) for i in all_retrieved_ids if i}
    unused = sorted(retrieved - cited)
    return {
        "cited_ids": sorted(cited),
        "unused_ids": unused,
        "cite_count": len(cited),
        "unused_count": len(unused),
        "ok": True,
        "note": "rmm_dialogue retrospective_cite_feedback",
    }


def rerank_memories(
    candidates: Sequence[Mapping[str, Any]],
    *,
    query: str,
    cite_boosts: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Lightweight rerank: overlap + retrieval_weight + cite boosts."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    boosts = dict(cite_boosts or {})
    qtok = _tokens(query)
    ranked: list[tuple[float, dict[str, Any]]] = []
    for m in candidates:
        if not isinstance(m, Mapping):
            continue
        mid = str(m.get("memory_id") or "")
        overlap = len(qtok & _tokens(f"{m.get('topic') or ''} {m.get('segment') or ''}"))
        weight = float(m.get("retrieval_weight") or 1.0)
        boost = float(boosts.get(mid) or 0.0)
        score = overlap * weight + boost + 0.1 * int(m.get("cite_count") or 0)
        ranked.append((score, dict(m)))
    ranked.sort(key=lambda x: (-x[0], str(x[1].get("memory_id") or "")))
    return {
        "query": query.strip(),
        "ranked": [m for _, m in ranked],
        "scores": [round(s, 4) for s, _ in ranked],
        "ok": True,
        "note": "rmm_dialogue rerank_memories",
    }


def retrieval_refine_plan(
    memories: Sequence[Mapping[str, Any]],
    *,
    cited_ids: Sequence[str],
    unused_ids: Sequence[str],
    cite_delta: float = 0.15,
    unused_delta: float = 0.05,
) -> dict[str, Any]:
    """Update retrieval_weight from cite feedback (report-only)."""
    cited = {str(i) for i in cited_ids if i}
    unused = {str(i) for i in unused_ids if i}
    updates: list[dict[str, Any]] = []
    for m in memories:
        if not isinstance(m, Mapping):
            continue
        mid = str(m.get("memory_id") or "")
        w = float(m.get("retrieval_weight") or 1.0)
        cites = int(m.get("cite_count") or 0)
        if mid in cited:
            nw = min(3.0, w + cite_delta)
            updates.append(
                {
                    "memory_id": mid,
                    "retrieval_weight": round(nw, 4),
                    "cite_count": cites + 1,
                    "reason": "cited",
                }
            )
        elif mid in unused:
            nw = max(0.1, w - unused_delta)
            updates.append(
                {
                    "memory_id": mid,
                    "retrieval_weight": round(nw, 4),
                    "cite_count": cites,
                    "reason": "unused",
                }
            )
    return {
        "updates": updates,
        "update_count": len(updates),
        "apply": False,
        "ok": True,
        "note": "rmm_dialogue retrieval_refine_plan",
    }
