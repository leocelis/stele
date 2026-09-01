"""ExpeL-shaped experiential insight memory (stdlib; no LLM).

Shaped by ExpeL (arXiv:2308.10144 / AAAI 2024): pool success+failure
trajectories; extract insights via ADD/EDIT/UPVOTE/DOWNVOTE with
importance counts; retrieve insights + similar successes at test time.
Proxies only — not ExpeL paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
INSIGHT_OPS = frozenset({"ADD", "EDIT", "UPVOTE", "DOWNVOTE"})


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def experience_pool_add(
    *,
    task: str,
    outcome: str,
    trajectory_summary: str = "",
) -> dict[str, Any]:
    """Add a success or failure experience to the pool (structured, not raw dump)."""
    if outcome not in {"success", "failure"}:
        raise SchemaError("outcome must be success|failure")
    if not isinstance(task, str) or not task.strip():
        raise SchemaError("task required")
    eid = hashlib.sha256(
        canonical_dumps(
            {"t": task, "o": outcome, "s": trajectory_summary[:200]}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experience_id": eid,
        "task": task.strip()[:120],
        "outcome": outcome,
        "summary": (trajectory_summary or "").strip()[:240],
        "ok": True,
        "note": "expel experience_pool_add",
    }


def insight_op(
    insights: Sequence[Mapping[str, Any]],
    *,
    op: str,
    text: str = "",
    insight_id: str | None = None,
) -> dict[str, Any]:
    """
    Apply ADD / EDIT / UPVOTE / DOWNVOTE on the insight list.
    ADD starts importance=2; UPVOTE/EDIT +1; DOWNVOTE -1; drop at 0.
    Report-only — returns next_insights plan.
    """
    if op not in INSIGHT_OPS:
        raise SchemaError(f"op must be one of {sorted(INSIGHT_OPS)}")
    bank = [dict(i) for i in insights if isinstance(i, Mapping)]
    by_id = {str(i.get("insight_id")): i for i in bank if i.get("insight_id")}

    if op == "ADD":
        if not text.strip():
            raise SchemaError("text required for ADD")
        iid = hashlib.sha256(
            canonical_dumps({"t": text.strip()}).encode("utf-8")
        ).hexdigest()[:12]
        if iid in by_id:
            by_id[iid]["importance"] = int(by_id[iid].get("importance") or 0) + 1
            by_id[iid]["text"] = text.strip()[:240]
        else:
            by_id[iid] = {
                "insight_id": iid,
                "text": text.strip()[:240],
                "importance": 2,
            }
        action = "ADD"
    else:
        if not insight_id or insight_id not in by_id:
            return {
                "action": op,
                "ok": False,
                "reason": "insight_id_missing",
                "next_insights": list(by_id.values()),
                "apply": False,
                "note": "expel insight_op",
            }
        item = by_id[insight_id]
        imp = int(item.get("importance") or 0)
        if op == "UPVOTE":
            item["importance"] = imp + 1
        elif op == "EDIT":
            if not text.strip():
                raise SchemaError("text required for EDIT")
            item["text"] = text.strip()[:240]
            item["importance"] = imp + 1
        elif op == "DOWNVOTE":
            item["importance"] = imp - 1
            if item["importance"] <= 0:
                del by_id[insight_id]
        action = op

    next_list = sorted(
        by_id.values(),
        key=lambda x: (-int(x.get("importance") or 0), str(x.get("insight_id"))),
    )
    return {
        "action": action,
        "ok": True,
        "next_insights": next_list,
        "apply": False,
        "note": "expel insight_op",
    }


def insight_importance_gate(insights: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Drop insights with importance <= 0 (ExpeL robustify)."""
    keep: list[dict[str, Any]] = []
    drop: list[dict[str, Any]] = []
    for i in insights:
        if not isinstance(i, Mapping):
            continue
        imp = int(i.get("importance") or 0)
        if imp <= 0:
            drop.append(dict(i))
        else:
            keep.append(dict(i))
    return {
        "keep": keep,
        "drop": drop,
        "drop_count": len(drop),
        "apply": False,
        "ok": True,
        "note": "expel insight_importance_gate",
    }


def retrieve_insights(
    insights: Sequence[Mapping[str, Any]],
    *,
    query: str,
    top_k: int = 5,
) -> dict[str, Any]:
    """Retrieve insights by lexical overlap, prefer higher importance."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    scored: list[tuple[int, int, dict[str, Any]]] = []
    for i in insights:
        if not isinstance(i, Mapping):
            continue
        score = len(qtok & _tokens(str(i.get("text") or "")))
        imp = int(i.get("importance") or 0)
        scored.append((score, imp, dict(i)))
    scored.sort(key=lambda x: (-x[0], -x[1], str(x[2].get("insight_id"))))
    hits = [e for sc, imp, e in scored[:top_k]]
    return {
        "query": query.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "expel retrieve_insights",
    }


def retrieve_similar_successes(
    pool: Sequence[Mapping[str, Any]],
    *,
    task: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Recall similar successful trajectories for test-time guidance."""
    if not isinstance(task, str) or not task.strip():
        raise SchemaError("task required")
    qtok = _tokens(task)
    scored: list[tuple[int, dict[str, Any]]] = []
    for e in pool:
        if not isinstance(e, Mapping):
            continue
        if e.get("outcome") != "success":
            continue
        blob = f"{e.get('task') or ''} {e.get('summary') or ''}"
        score = len(qtok & _tokens(blob))
        scored.append((score, dict(e)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("experience_id") or "")))
    hits = [e for sc, e in scored[:top_k]]
    return {
        "task": task.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "expel retrieve_similar_successes",
    }
