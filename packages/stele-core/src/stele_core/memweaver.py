"""MemWeaver-shaped hybrid memory weave (stdlib; no LLM).

Shaped by MemWeaver (arXiv:2601.18204 / ACL 2026 Findings): tri-layer
consolidation — temporally grounded graph memory, experience abstraction,
passage evidence — with dual-channel retrieval (structured + textual).
Lexical proxies only; not LoCoMo paper scores.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

WEAVE_LAYERS = frozenset({"graph", "experience", "passage"})

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)

_LAYER_TO_WEAVE: dict[str, str] = {
    "decision": "graph",
    "goal": "graph",
    "workflow": "experience",
    "skill_artifact": "experience",
    "failure_lesson": "experience",
    "issue": "passage",
}


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def weave_layer_assign(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Map a Stele entry onto MemWeaver GM / ExpM / PM."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    layer = str(entry.get("layer") or "").strip()
    weave = _LAYER_TO_WEAVE.get(layer, "passage")
    links = entry.get("links") or []
    if isinstance(links, list) and len(links) >= 2 and weave == "passage":
        weave = "graph"
    return {
        "id": entry.get("id"),
        "weave_layer": weave,
        "content_layer": layer or None,
        "ok": weave in WEAVE_LAYERS,
        "note": "memweaver weave_layer_assign — GM/ExpM/PM proxy",
    }


def build_hybrid_weave(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Build tri-layer index: graph triples from LINK edges, experience clusters
    by conflict_key, passages as raw evidence digests.
    """
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence is required")
    by_id = {
        str(e.get("id")): e for e in entries if isinstance(e, Mapping) and e.get("id")
    }
    graph_triples: list[dict[str, Any]] = []
    for eid, e in sorted(by_id.items()):
        for lnk in e.get("links") or []:
            if not isinstance(lnk, Mapping):
                continue
            ref = str(lnk.get("ref") or "")
            if not ref:
                continue
            graph_triples.append(
                {
                    "s": eid,
                    "p": str(lnk.get("kind") or "related"),
                    "o": ref,
                    "t": (e.get("temporal") or {}).get("valid_from")
                    or e.get("created_at"),
                }
            )

    experience_groups: dict[str, list[str]] = defaultdict(list)
    passages: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []
    for eid, e in sorted(by_id.items()):
        assign = weave_layer_assign(e)
        assignments.append(assign)
        ck = str(e.get("conflict_key") or "").strip() or f"id:{eid}"
        if assign["weave_layer"] == "experience":
            experience_groups[ck].append(eid)
        body = f"{e.get('title') or ''}\n{e.get('body') or ''}"
        digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
        passages.append(
            {
                "id": eid,
                "digest": digest,
                "tokens": sorted(_tokens(body))[:48],
                "weave_layer": assign["weave_layer"],
                "t": (e.get("temporal") or {}).get("valid_from")
                or e.get("created_at"),
            }
        )

    experience_items = [
        {
            "conflict_key": k,
            "entry_ids": ids,
            "support": len(ids),
            "abstractable": len(ids) >= 2,
        }
        for k, ids in sorted(experience_groups.items())
    ]
    weave_id = hashlib.sha256(
        canonical_dumps(
            {
                "triples": len(graph_triples),
                "experience": len(experience_items),
                "passages": len(passages),
            }
        ).encode("utf-8")
    ).hexdigest()[:16]

    return {
        "weave_id": weave_id,
        "graph": {"triples": graph_triples, "count": len(graph_triples)},
        "experience": {"items": experience_items, "count": len(experience_items)},
        "passage": {"items": passages, "count": len(passages)},
        "assignments": assignments,
        "ok": True,
        "note": "memweaver build_hybrid_weave — tri-layer proxy",
    }


def dual_channel_retrieve(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    k_r: int = 6,
    k_p: int = 6,
    k_e: int = 6,
) -> dict[str, Any]:
    """Dual-channel retrieve: structured triples + textual passages/experience."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string is required")
    weave = build_hybrid_weave(entries)
    qtok = _tokens(query)
    by_id = {
        str(e.get("id")): e for e in entries if isinstance(e, Mapping) and e.get("id")
    }

    scored_triples: list[tuple[int, dict[str, Any]]] = []
    for tri in weave["graph"]["triples"]:
        blob = f"{tri['s']} {tri['p']} {tri['o']}"
        subj = by_id.get(tri["s"]) or {}
        obj = by_id.get(tri["o"]) or {}
        blob += f" {subj.get('title') or ''} {obj.get('title') or ''}"
        score = len(qtok & _tokens(blob))
        if score:
            scored_triples.append((score, tri))
    scored_triples.sort(key=lambda x: (-x[0], x[1]["s"], x[1]["o"]))
    c_kg = [t for _, t in scored_triples[: max(0, k_r)]]

    scored_passages: list[tuple[int, dict[str, Any]]] = []
    for p in weave["passage"]["items"]:
        score = len(qtok & set(p.get("tokens") or []))
        if score:
            scored_passages.append((score, p))
    scored_passages.sort(key=lambda x: (-x[0], x[1]["id"]))
    c_pass = [p for _, p in scored_passages[: max(0, k_p)]]

    scored_exp: list[tuple[int, dict[str, Any]]] = []
    for item in weave["experience"]["items"]:
        blob_parts: list[str] = [item["conflict_key"]]
        for eid in item["entry_ids"]:
            e = by_id.get(eid) or {}
            blob_parts.append(str(e.get("title") or ""))
            blob_parts.append(str(e.get("body") or ""))
        score = len(qtok & _tokens(" ".join(blob_parts)))
        if score or item.get("abstractable"):
            scored_exp.append((score + (1 if item.get("abstractable") else 0), item))
    scored_exp.sort(key=lambda x: (-x[0], x[1]["conflict_key"]))
    c_exp = [e for _, e in scored_exp[: max(0, k_e)]]

    return {
        "query": query.strip(),
        "budgets": {"k_r": k_r, "k_p": k_p, "k_e": k_e},
        "c_kg": c_kg,
        "c_txt": {"passages": c_pass, "experience": c_exp},
        "structured_count": len(c_kg),
        "textual_count": len(c_pass) + len(c_exp),
        "weave_id": weave["weave_id"],
        "ok": True,
        "note": "memweaver dual_channel_retrieve — fused context proxy",
    }


def experience_abstract_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    min_support: int = 2,
) -> dict[str, Any]:
    """Plan experience abstractions only when support ≥ min_support (report-only)."""
    weave = build_hybrid_weave(entries)
    candidates = [
        i
        for i in weave["experience"]["items"]
        if int(i.get("support") or 0) >= min_support
    ]
    return {
        "min_support": min_support,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "apply": False,
        "ok": True,
        "note": "memweaver experience_abstract_plan — report-only; no auto-write",
    }


def temporal_session_conflict_scan(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Session-level temporal conflict scan: same conflict_key with divergent
    promoted bodies / valid_from ordering — reconcile plan only.
    """
    by_ck: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        ck = str(e.get("conflict_key") or "").strip()
        if not ck:
            continue
        by_ck[ck].append(e)

    conflicts: list[dict[str, Any]] = []
    for ck, group in sorted(by_ck.items()):
        if len(group) < 2:
            continue
        bodies = {str(g.get("body") or "").strip() for g in group}
        states = {str(g.get("state") or "") for g in group}
        if len(bodies) <= 1 and "contested" not in states:
            continue
        times = sorted(
            str(
                (g.get("temporal") or {}).get("valid_from")
                or g.get("created_at")
                or ""
            )
            for g in group
        )
        conflicts.append(
            {
                "conflict_key": ck,
                "entry_ids": [str(g.get("id")) for g in group],
                "body_variants": len(bodies),
                "states": sorted(states),
                "time_span": [times[0], times[-1]] if times else [],
                "action": "reconcile",
            }
        )
    return {
        "conflict_count": len(conflicts),
        "conflicts": conflicts,
        "apply": False,
        "ok": True,
        "note": "memweaver temporal_session_conflict_scan — reconcile plan only",
    }


def multi_hop_depth_score(
    path_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """MemHop-shaped hop depth over an explicit entry path (1–5)."""
    if not isinstance(path_ids, Sequence) or isinstance(path_ids, (str, bytes)):
        raise SchemaError("path_ids sequence is required")
    ids = [str(i) for i in path_ids if i]
    hops = max(0, len(ids) - 1)
    by_id = {
        str(e.get("id")): e for e in entries if isinstance(e, Mapping) and e.get("id")
    }
    linked = True
    for a, b in zip(ids, ids[1:]):
        ea = by_id.get(a) or {}
        refs = {
            str(lnk.get("ref"))
            for lnk in (ea.get("links") or [])
            if isinstance(lnk, Mapping)
        }
        eb = by_id.get(b) or {}
        refs_b = {
            str(lnk.get("ref"))
            for lnk in (eb.get("links") or [])
            if isinstance(lnk, Mapping)
        }
        if b not in refs and a not in refs_b:
            linked = False
            break
    return {
        "path": ids,
        "hop_depth": hops,
        "within_memhop_range": 1 <= hops <= 5,
        "edges_linked": linked,
        "ok": True,
        "note": "memhop multi_hop_depth_score — path proxy, not MemHop scores",
    }
