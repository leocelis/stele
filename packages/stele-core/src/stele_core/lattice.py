"""LatticeMind-shaped symbolic conflict + budgeted compact render (stdlib)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

CONFLICT_KINDS = frozenset({"credibility", "coordination", "none"})


def _adj_entry_links(entries: Mapping[str, Mapping[str, Any]]) -> dict[str, set[str]]:
    adj: dict[str, set[str]] = {eid: set() for eid in entries}
    for eid, e in entries.items():
        for lnk in e.get("links") or []:
            if lnk.get("kind") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in entries:
                adj[eid].add(ref)
                adj[ref].add(eid)
    return adj


def link_cycles(entries: Iterable[Mapping[str, Any]]) -> list[list[str]]:
    """Detect triangles/simple cycles in undirected entry LINK graph (mechanical)."""
    by_id = {str(e.get("id")): e for e in entries if e.get("id")}
    adj = _adj_entry_links(by_id)
    found: list[list[str]] = []
    seen_sets: set[frozenset[str]] = set()
    nodes = sorted(by_id)
    for i, a in enumerate(nodes):
        for b in sorted(adj.get(a, ())):
            if b <= a:
                continue
            for c in sorted(adj.get(b, ())):
                if c <= b:
                    continue
                if a in adj.get(c, ()):
                    key = frozenset({a, b, c})
                    if key not in seen_sets:
                        seen_sets.add(key)
                        found.append([a, b, c, a])
                        if len(found) >= 20:
                            return found
    # Also flag self-loops / 2-cycles (mutual only already undirected)
    for a in nodes:
        if a in adj.get(a, ()):
            key = frozenset({a})
            if key not in seen_sets:
                seen_sets.add(key)
                found.append([a, a])
    return found


def symbolic_conflict_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """
    LatticeMind-shaped cheap symbolic checks (no LLM).

    Mechanical: duplicate promoted conflict_keys; LINK cycles.
    """
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    entries_list = list(entries)
    by_key: dict[str, list[str]] = {}
    for e in entries_list:
        if e.get("state") != "promoted":
            continue
        key = e.get("conflict_key")
        if not key:
            continue
        by_key.setdefault(str(key), []).append(str(e.get("id")))
    key_conflicts = [
        {"conflict_key": k, "ids": ids, "kind": "credibility"}
        for k, ids in sorted(by_key.items())
        if len(ids) > 1
    ][:limit]
    cycles = link_cycles(entries_list)
    return {
        "key_conflicts": key_conflicts,
        "link_cycles": cycles,
        "count_key_conflicts": len(key_conflicts),
        "count_cycles": len(cycles),
        "ok": len(key_conflicts) == 0 and len(cycles) == 0,
        "note": "LatticeMind-shaped symbolic scan — no LLM reconciler",
    }


def classify_conflict(
    a: Mapping[str, Any],
    b: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Credibility vs coordination (LatticeMind).

    Same conflict_key + divergent body → credibility.
    Different keys, overlapping scope + high title overlap → coordination.
    Else none.
    """
    ka, kb = a.get("conflict_key"), b.get("conflict_key")
    if ka and kb and str(ka) == str(kb):
        ta = set(tokenize(f"{a.get('title') or ''} {a.get('body') or ''}"))
        tb = set(tokenize(f"{b.get('title') or ''} {b.get('body') or ''}"))
        same_body = ta == tb and bool(ta)
        if same_body:
            return {
                "kind": "none",
                "reason": "same_key_identical_tokens",
                "a": a.get("id"),
                "b": b.get("id"),
            }
        return {
            "kind": "credibility",
            "reason": "same_conflict_key_divergent",
            "a": a.get("id"),
            "b": b.get("id"),
            "note": "one claim should defeat the other — use supersede/TARL revise",
        }
    sa, sb = str(a.get("scope") or ""), str(b.get("scope") or "")
    if sa and sa == sb:
        ta = set(tokenize(str(a.get("title") or "")))
        tb = set(tokenize(str(b.get("title") or "")))
        if ta and tb:
            j = len(ta & tb) / len(ta | tb)
            if j >= 0.4:
                return {
                    "kind": "coordination",
                    "reason": "same_scope_title_overlap",
                    "jaccard": round(j, 4),
                    "a": a.get("id"),
                    "b": b.get("id"),
                    "note": "proposals may coexist — do not silent-merge",
                }
    return {
        "kind": "none",
        "reason": "no_symbolic_conflict",
        "a": a.get("id"),
        "b": b.get("id"),
    }


def compact_render(
    slices: Sequence[Mapping[str, Any]],
    *,
    reader_budget: int = 1400,
    include_fields: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    LatticeMind budgeted-track compact renderer (character budget).

    Packs id/title/body (clipped) until reader_budget; reports overflow.
    """
    if reader_budget < 1:
        raise SchemaError("reader_budget must be >= 1")
    fields = list(include_fields or ("id", "title", "body", "conflict_key", "state"))
    rendered: list[dict[str, Any]] = []
    used = 0
    overflow: list[str] = []
    for s in slices:
        row: dict[str, Any] = {}
        for f in fields:
            if f in s:
                row[f] = s[f]
        # Prefer short form
        body = str(row.get("body") or "")
        title = str(row.get("title") or "")
        # Estimate cost
        cost = len(title) + min(len(body), 200) + 32
        if used + cost > reader_budget and rendered:
            overflow.append(str(s.get("id") or ""))
            continue
        # If still over budget alone, hard clip to remaining
        remaining = reader_budget - used
        blob = " ".join(str(row.get(f) or "") for f in fields)
        if len(blob) > remaining:
            keep = max(20, remaining - len(title) - 16)
            row["body"] = body[:keep].rstrip() + "…"
            row["body_truncated"] = True
            cost = min(remaining, len(title) + keep + 16)
        if used + cost > reader_budget and rendered:
            overflow.append(str(s.get("id") or ""))
            continue
        if used + cost > reader_budget and not rendered:
            cost = remaining
        used += cost
        rendered.append(row)
    return {
        "reader_budget": reader_budget,
        "used": min(used, reader_budget),
        "items": rendered,
        "count": len(rendered),
        "overflow_ids": overflow,
        "overflow": len(overflow),
        "note": "LatticeMind-shaped compact render — external memory budget",
    }
