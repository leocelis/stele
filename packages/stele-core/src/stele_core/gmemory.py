"""G-Memory-shaped MAS hierarchical memory (stdlib; no LLM).

Shaped by G-Memory (arXiv:2506.07398): insight / query / interaction
graphs + bi-directional traversal + hierarchy update plan.
Proxies only — not G-Memory paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

TIERS = frozenset({"insight", "query", "interaction"})
_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def classify_graph_tier(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Map entry → insight | query | interaction."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    text = f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()
    layer = str(entry.get("layer") or "")
    if any(w in text for w in ("insight:", "lesson:", "general rule", "always")):
        tier = "insight"
    elif any(w in text for w in ("query:", "task:", "user asked", "question:")) or layer == "goal":
        tier = "query"
    elif layer in {"failure_lesson", "workflow", "skill_artifact"} or any(
        w in text for w in ("agent said", "dialogue", "utterance", "collaborat")
    ):
        tier = "interaction"
    elif layer == "decision":
        tier = "insight"
    else:
        tier = "query"
    return {
        "id": entry.get("id"),
        "tier": tier,
        "ok": tier in TIERS,
        "note": "gmemory classify_graph_tier",
    }


def build_query_graph(entries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build query-graph nodes (query text + status + linked ids)."""
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence required")
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    by_tok: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        tier = classify_graph_tier(e)["tier"]
        if tier != "query" and "query" not in f"{e.get('title') or ''}".lower():
            # still allow decision/issue as query-like task nodes
            if tier == "interaction":
                continue
        eid = str(e.get("id"))
        title = str(e.get("title") or "")
        body = str(e.get("body") or "")
        status = "Failed" if any(
            w in body.lower() for w in ("failed", "error", "did not")
        ) else "Resolved"
        nodes.append(
            {
                "query_id": eid,
                "query": title or body[:80],
                "status": status,
                "tier": tier,
            }
        )
        for t in _tokens(title) | _tokens(body):
            if len(t) > 3:
                by_tok[t].append(eid)
    # edges: shared significant tokens
    seen: set[tuple[str, str]] = set()
    for ids in by_tok.values():
        uniq = sorted(set(ids))
        for i, a in enumerate(uniq):
            for b in uniq[i + 1 :]:
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                edges.append({"from": a, "to": b, "kind": "semantic"})
                if len(edges) >= 40:
                    break
            if len(edges) >= 40:
                break
        if len(edges) >= 40:
            break
    return {
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "ok": True,
        "note": "gmemory build_query_graph",
    }


def upward_insight_traverse(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Upward: query → insight nodes (lexical)."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    hits: list[tuple[int, dict[str, Any]]] = []
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        if classify_graph_tier(e)["tier"] != "insight":
            # also accept decision with lesson language
            blob = f"{e.get('title') or ''} {e.get('body') or ''}".lower()
            if "insight" not in blob and "lesson" not in blob and "always" not in blob:
                if str(e.get("layer")) != "decision":
                    continue
        blob = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        score = len(qtok & _tokens(blob))
        hits.append(
            (
                score,
                {
                    "id": e.get("id"),
                    "insight": str(e.get("title") or blob.split(".")[0])[:120],
                    "score": score,
                },
            )
        )
    hits.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    chosen = [h for sc, h in hits[:top_k] if sc >= 0]
    return {
        "query": query.strip(),
        "insights": chosen,
        "insight_count": len(chosen),
        "ok": True,
        "note": "gmemory upward_insight_traverse",
    }


def downward_interaction_traverse(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Downward: query → interaction / trajectory snippets."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    hits: list[tuple[int, dict[str, Any]]] = []
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        tier = classify_graph_tier(e)["tier"]
        layer = str(e.get("layer") or "")
        if tier != "interaction" and layer not in {
            "failure_lesson",
            "issue",
            "workflow",
        }:
            continue
        blob = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        score = len(qtok & _tokens(blob))
        hits.append(
            (
                score,
                {
                    "id": e.get("id"),
                    "snippet": blob.strip()[:160],
                    "score": score,
                },
            )
        )
    hits.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    chosen = [h for sc, h in hits[:top_k]]
    return {
        "query": query.strip(),
        "interactions": chosen,
        "interaction_count": len(chosen),
        "ok": True,
        "note": "gmemory downward_interaction_traverse",
    }


def bidirectional_retrieve(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Bi-directional retrieve: insights + interactions for a query."""
    up = upward_insight_traverse(entries, query=query, top_k=top_k)
    down = downward_interaction_traverse(entries, query=query, top_k=top_k)
    return {
        "query": query.strip(),
        "insights": up["insights"],
        "interactions": down["interactions"],
        "insight_count": up["insight_count"],
        "interaction_count": down["interaction_count"],
        "ok": True,
        "note": "gmemory bidirectional_retrieve",
    }


def hierarchy_update_plan(
    *,
    query: str,
    status: str,
    used_insight_ids: Sequence[str] | None = None,
    new_insight: str = "",
) -> dict[str, Any]:
    """Post-task hierarchy update plan (report-only)."""
    if status not in {"Failed", "Resolved"}:
        raise SchemaError("status must be Failed|Resolved")
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qid = hashlib.sha256(canonical_dumps({"q": query}).encode("utf-8")).hexdigest()[:10]
    insight = new_insight.strip() or (
        f"Insight from {'success' if status == 'Resolved' else 'failure'}: {query.strip()[:80]}"
    )
    return {
        "query_id": f"q:{qid}",
        "query": query.strip()[:160],
        "status": status,
        "link_insight_ids": [str(i) for i in (used_insight_ids or []) if i][:8],
        "new_insight": insight[:200],
        "apply": False,
        "ok": True,
        "note": "gmemory hierarchy_update_plan — no auto-write",
    }
