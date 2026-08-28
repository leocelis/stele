"""REMem-shaped episodic memory graph (stdlib; no LLM).

Shaped by REMem (arXiv:2602.13530 / ICLR 2026): hybrid graph of
time-aware gists + temporal facts, situational binding, agentic
iterative retrieval plan. Proxies only — not REMem paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
_ISOish = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

SITUATIONAL_DIMS = frozenset(
    {"time", "location", "participants", "emotion", "action"}
)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def _blob(entry: Mapping[str, Any]) -> str:
    return f"{entry.get('title') or ''}\n{entry.get('body') or ''}"


def extract_episodic_gist(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Concise time-aware gist for one episode/entry."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    title = str(entry.get("title") or "").strip()
    body = str(entry.get("body") or "").strip()
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t = temporal.get("valid_from") or entry.get("created_at")
    # First sentence / title as gist proxy
    sentence = body.split(".")[0].strip() if body else title
    gist = sentence[:180] if sentence else title
    if t and gist and not str(t)[:10] in gist:
        gist = f"[{str(t)[:10]}] {gist}"
    digest = hashlib.sha256(gist.encode("utf-8")).hexdigest()[:12]
    return {
        "id": entry.get("id"),
        "gist": gist,
        "gist_digest": digest,
        "reference_time": t,
        "ok": True,
        "note": "remem extract_episodic_gist — gist proxy",
    }


def extract_temporal_facts(entry: Mapping[str, Any]) -> dict[str, Any]:
    """(subject, predicate, object) facts with optional time qualifiers."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    text = _blob(entry)
    toks = list(_TOKEN.findall(text))
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t = temporal.get("valid_from") or entry.get("created_at")
    dates = _ISOish.findall(text)
    facts: list[dict[str, Any]] = []
    # Lightweight SVO heuristic: first noun-ish as subject, verb cue, rest as object
    verbs = {"use", "uses", "retry", "retries", "prefer", "prefers", "fix", "fixed", "buy", "bought"}
    subj = str(entry.get("scope") or "").split(":")[-1] or (toks[0] if toks else "agent")
    pred = "relates_to"
    for v in verbs:
        if v in text.lower():
            pred = v.rstrip("s") if v.endswith("s") and v != "fix" else v
            break
    obj = title_obj = str(entry.get("title") or "event").strip() or "event"
    facts.append(
        {
            "s": subj,
            "p": pred,
            "o": title_obj,
            "point_in_time": str(t)[:10] if t else (dates[0] if dates else None),
            "entry_id": entry.get("id"),
        }
    )
    for d in dates[:2]:
        if d != (str(t)[:10] if t else None):
            facts.append(
                {
                    "s": subj,
                    "p": "mentioned_on",
                    "o": d,
                    "point_in_time": d,
                    "entry_id": entry.get("id"),
                }
            )
    return {
        "id": entry.get("id"),
        "facts": facts,
        "fact_count": len(facts),
        "ok": True,
        "note": "remem extract_temporal_facts — SPO proxy",
    }


def situational_bind(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Bind situational dimensions: time, location, participants, emotion, action."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    text = _blob(entry).lower()
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    dims: dict[str, Any] = {
        "time": temporal.get("valid_from") or entry.get("created_at"),
        "location": None,
        "participants": [],
        "emotion": None,
        "action": None,
    }
    for loc in ("office", "home", "lab", "clinic", "warehouse", "store"):
        if loc in text:
            dims["location"] = loc
            break
    for emo in ("happy", "frustrated", "anxious", "calm", "angry"):
        if emo in text:
            dims["emotion"] = emo
            break
    for act in ("retry", "fix", "buy", "ship", "deploy", "review", "pay"):
        if act in text:
            dims["action"] = act
            break
    # Participants: capitalized tokens in title (proxy)
    title = str(entry.get("title") or "")
    parts = [w for w in title.split() if w[:1].isupper() and len(w) > 2]
    dims["participants"] = parts[:4]
    bound = sum(1 for k, v in dims.items() if v not in (None, []))
    return {
        "id": entry.get("id"),
        "situational": dims,
        "bound_count": bound,
        "ok": True,
        "note": "remem situational_bind — situation-model proxy",
    }


def build_hybrid_episodic_graph(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Hybrid graph: gist nodes + fact triples + situational edges."""
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence is required")
    gists: list[dict[str, Any]] = []
    facts: list[dict[str, Any]] = []
    situational: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        g = extract_episodic_gist(e)
        f = extract_temporal_facts(e)
        s = situational_bind(e)
        gists.append(
            {
                "entry_id": e.get("id"),
                "gist": g["gist"],
                "gist_digest": g["gist_digest"],
                "reference_time": g["reference_time"],
            }
        )
        facts.extend(f["facts"])
        situational.append({"entry_id": e.get("id"), **s["situational"]})
    graph_id = hashlib.sha256(
        canonical_dumps(
            {"g": len(gists), "f": len(facts), "s": len(situational)}
        ).encode("utf-8")
    ).hexdigest()[:16]
    return {
        "graph_id": graph_id,
        "gists": gists,
        "facts": facts,
        "situational": situational,
        "gist_count": len(gists),
        "fact_count": len(facts),
        "ok": True,
        "note": "remem build_hybrid_episodic_graph",
    }


def agentic_retrieve_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    max_steps: int = 3,
) -> dict[str, Any]:
    """
    REMem-I shaped plan: lexical retrieve → graph explore → output answer.
    Report-only tool sequence — no LLM agent loop.
    """
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string is required")
    if max_steps < 1:
        raise SchemaError("max_steps must be >= 1")
    graph = build_hybrid_episodic_graph(entries)
    qtok = _tokens(query)
    scored_gists: list[tuple[int, dict[str, Any]]] = []
    for g in graph["gists"]:
        score = len(qtok & _tokens(g.get("gist") or ""))
        if score:
            scored_gists.append((score, g))
    scored_gists.sort(key=lambda x: (-x[0], str(x[1].get("entry_id"))))
    seeds = [g for _, g in scored_gists[:5]]

    steps: list[dict[str, Any]] = [
        {
            "step": 1,
            "tool": "lexical_retrieve",
            "seeds": [s.get("entry_id") for s in seeds],
            "gist_hits": len(seeds),
        }
    ]
    if max_steps >= 2:
        # Graph explore: pull facts for seed entry ids
        seed_ids = {str(s.get("entry_id")) for s in seeds}
        related_facts = [
            f for f in graph["facts"] if str(f.get("entry_id")) in seed_ids
        ]
        steps.append(
            {
                "step": 2,
                "tool": "find_gist_contexts",
                "fact_hits": len(related_facts),
                "facts": related_facts[:8],
            }
        )
    if max_steps >= 3:
        # Temporal filter if query has time cues
        ql = query.lower()
        temporal = any(
            w in ql for w in ("when", "before", "after", "date", "timeline")
        )
        steps.append(
            {
                "step": 3,
                "tool": "output_answer" if not temporal else "temporal_filter_then_answer",
                "temporal_focus": temporal,
                "confidence": "high" if seeds else "low",
            }
        )
    return {
        "query": query.strip(),
        "graph_id": graph["graph_id"],
        "steps": steps[:max_steps],
        "seed_count": len(seeds),
        "ok": True,
        "note": "remem agentic_retrieve_plan — ReAct tool proxy; no LLM loop",
    }


def ordinal_event_query(
    entries: Sequence[Mapping[str, Any]],
    *,
    order: str = "first",
) -> dict[str, Any]:
    """Episodic reasoning helper: first/last event by valid_from."""
    order_l = str(order or "first").lower()
    if order_l not in {"first", "last"}:
        raise SchemaError("order must be first or last")
    dated: list[tuple[str, str, str]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        temporal = e.get("temporal") if isinstance(e.get("temporal"), Mapping) else {}
        t = str(temporal.get("valid_from") or e.get("created_at") or "")
        if not t:
            continue
        dated.append((t, str(e.get("id")), str(e.get("title") or "")))
    dated.sort(key=lambda x: x[0])
    if not dated:
        return {"match": None, "ok": True, "note": "remem ordinal_event_query — empty"}
    pick = dated[0] if order_l == "first" else dated[-1]
    return {
        "order": order_l,
        "match": {"time": pick[0], "id": pick[1], "title": pick[2]},
        "candidate_count": len(dated),
        "ok": True,
        "note": "remem ordinal_event_query — timeline proxy",
    }
