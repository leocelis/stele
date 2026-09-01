"""AriadneMem-shaped merge/link/add + bridge discovery (stdlib; no LLM).

Offline coarsening: merge near-duplicates, link state transitions, else add.
Online: bridge discovery between retrieved facts via LINK paths.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _tok(e: Mapping[str, Any]) -> set[str]:
    return set(tokenize(f"{e.get('title') or ''}\n{e.get('body') or ''}"))


def merge_link_add(
    new_entry: Mapping[str, Any],
    existing: Sequence[Mapping[str, Any]],
    *,
    merge_threshold: float = 0.75,
    link_threshold: float = 0.45,
) -> dict[str, Any]:
    """
    Decide merge | link | add against existing promoted/contested tips.
    """
    if not (0 <= link_threshold <= merge_threshold <= 1):
        raise SchemaError("need 0 ≤ link_threshold ≤ merge_threshold ≤ 1")
    ntok = _tok(new_entry)
    if not ntok:
        raise SchemaError("new_entry must have tokenizable title/body")
    best = None
    best_sim = -1.0
    for e in existing:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        if new_entry.get("scope") and e.get("scope") and new_entry.get("scope") != e.get("scope"):
            continue
        et = _tok(e)
        if not et:
            continue
        sim = len(ntok & et) / len(ntok | et)
        if sim > best_sim:
            best_sim = sim
            best = e
    if best is None or best_sim < link_threshold:
        return {
            "decision": "add",
            "similarity": round(max(0.0, best_sim), 4),
            "against_id": None,
            "ok": True,
            "note": "AriadneMem merge_link_add — distinct content",
        }
    if best_sim >= merge_threshold:
        return {
            "decision": "merge",
            "similarity": round(best_sim, 4),
            "against_id": best.get("id"),
            "against_title": best.get("title"),
            "edge": None,
            "ok": True,
            "note": "AriadneMem merge — update timestamp of existing; no new node",
        }
    # Mid band: state transition → link
    edge = "UPDATES"
    ck_n = str(new_entry.get("conflict_key") or "")
    ck_e = str(best.get("conflict_key") or "")
    if ck_n and ck_e and ck_n == ck_e:
        edge = "SUPERSEDES"
    elif best_sim < 0.55:
        edge = "RELATED"
    return {
        "decision": "link",
        "similarity": round(best_sim, 4),
        "against_id": best.get("id"),
        "against_title": best.get("title"),
        "edge": edge,
        "ok": True,
        "note": "AriadneMem link — retain both; temporal/state edge",
    }


def bridge_discover(
    seed_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    max_depth: int = 3,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Reconstruct LINK paths between seed facts (algorithmic bridge discovery).
    """
    seeds = [str(s) for s in seed_ids if s]
    if len(seeds) < 2:
        raise SchemaError("seed_ids needs at least 2 ids")
    if max_depth < 1:
        raise SchemaError("max_depth must be >= 1")
    by_id = {str(e.get("id")): e for e in entries}
    # adjacency via links both ways
    adj: dict[str, set[str]] = {i: set() for i in by_id}
    for e in entries:
        eid = str(e.get("id") or "")
        for link in e.get("links") or []:
            if not isinstance(link, Mapping):
                continue
            if str(link.get("kind") or "") != "entry":
                continue
            ref = str(link.get("ref") or "")
            if ref in by_id and eid in by_id:
                adj[eid].add(ref)
                adj[ref].add(eid)

    bridges: list[dict[str, Any]] = []
    # BFS from first seed to each other seed
    start = seeds[0]
    for target in seeds[1:]:
        if start not in by_id or target not in by_id:
            bridges.append(
                {
                    "from": start,
                    "to": target,
                    "path": None,
                    "found": False,
                    "reason": "missing_node",
                }
            )
            continue
        prev: dict[str, str | None] = {start: None}
        depth_of: dict[str, int] = {start: 0}
        queue = [start]
        found = False
        while queue:
            cur = queue.pop(0)
            if cur == target:
                found = True
                break
            if depth_of[cur] >= max_depth:
                continue
            for nxt in sorted(adj.get(cur) or []):
                if nxt not in prev:
                    prev[nxt] = cur
                    depth_of[nxt] = depth_of[cur] + 1
                    queue.append(nxt)
        if not found:
            bridges.append(
                {
                    "from": start,
                    "to": target,
                    "path": None,
                    "found": False,
                }
            )
            continue
        path = [target]
        while path[-1] != start:
            parent = prev[path[-1]]
            if parent is None:
                break
            path.append(parent)
            if len(path) > max_depth + 1:
                break
        path.reverse()
        bridges.append(
            {
                "from": start,
                "to": target,
                "path": path,
                "hops": len(path) - 1,
                "found": True,
                "titles": [(by_id.get(p) or {}).get("title") for p in path],
            }
        )
        if len(bridges) >= limit:
            break
    return {
        "seeds": seeds,
        "bridges": bridges,
        "found_count": sum(1 for b in bridges if b.get("found")),
        "ok": True,
        "note": "AriadneMem bridge_discover — LINK BFS; not iterative LLM planning",
    }


def fuse_cluster(
    entry_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    label: str | None = None,
) -> dict[str, Any]:
    """MemFuse-shaped cluster summary over atomic evidence ids (report-only)."""
    by_id = {str(e.get("id")): e for e in entries}
    members = []
    sources = set()
    for eid in entry_ids:
        e = by_id.get(str(eid))
        if e is None:
            continue
        members.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "source": (e.get("provenance") or {}).get("source"),
                "subject_id": (e.get("provenance") or {}).get("subject_id"),
            }
        )
        src = (e.get("provenance") or {}).get("source")
        if src:
            sources.add(str(src))
    titles = [str(m.get("title") or "") for m in members]
    summary = " | ".join(t for t in titles if t)[:240]
    return {
        "label": label or "cluster",
        "members": members,
        "member_count": len(members),
        "sources": sorted(sources),
        "summary": summary,
        "ok": len(members) > 0,
        "note": "MemFuse fuse_cluster — event-layer ids preserved under cluster",
    }
