"""Graph / federation helpers — MELD + MAP-Graph shaped, deterministic (C5)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize

MERGE_OUTCOMES = frozenset({"insert", "merge", "relate", "conflict", "reject"})


def _title_sim(a: str, b: str) -> float:
    ta, tb = set(tokenize(a)), set(tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def _entry_links(entries: Mapping[str, dict[str, Any]]) -> dict[str, set[str]]:
    """Undirected entry↔entry adjacency from LINK kind=entry."""
    adj: dict[str, set[str]] = {eid: set() for eid in entries}
    for eid, e in entries.items():
        for lnk in e.get("links") or []:
            if lnk.get("kind") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref and ref in entries:
                adj[eid].add(ref)
                adj[ref].add(eid)
    return adj


def blast_radius(
    entries: Iterable[dict[str, Any]],
    entry_id: str,
    *,
    max_depth: int = 3,
) -> dict[str, Any]:
    """
    RippleMem/MAP-Graph-shaped neighborhood: who is within N hops via entry LINKs.

    Report-only — does not mutate SoT.
    """
    if max_depth < 1 or max_depth > 5:
        raise ValueError("max_depth must be 1..5")
    by_id = {e["id"]: e for e in entries}
    if entry_id not in by_id:
        raise KeyError(entry_id)
    adj = _entry_links(by_id)
    layers: list[list[dict[str, Any]]] = []
    seen: set[str] = {entry_id}
    frontier = {entry_id}
    for depth in range(1, max_depth + 1):
        nxt: set[str] = set()
        layer: list[dict[str, Any]] = []
        for cur in frontier:
            for nb in adj.get(cur, ()):
                if nb in seen:
                    continue
                seen.add(nb)
                nxt.add(nb)
                e = by_id[nb]
                layer.append(
                    {
                        "id": nb,
                        "title": e.get("title"),
                        "state": e.get("state"),
                        "depth": depth,
                        "via": cur,
                    }
                )
        layers.append(layer)
        frontier = nxt
        if not frontier:
            break
    flat = [n for layer in layers for n in layer]
    return {
        "id": entry_id,
        "max_depth": max_depth,
        "reachable_count": len(flat),
        "layers": layers,
        "ids": [n["id"] for n in flat],
        "note": "blast radius via LINK kind=entry — report only",
    }


def merge_classify(
    a: Mapping[str, Any],
    b: Mapping[str, Any],
    *,
    merge_threshold: float = 0.85,
    relate_threshold: float = 0.45,
) -> dict[str, Any]:
    """
    MELD-shaped five-outcome classifier — deterministic signals only (no NLI/LLM).

    Signals: scoped conflict_key identity, title Jaccard, contested/revoked state.
    Outcomes: insert | merge | relate | conflict | reject.
    Never auto-mutates — caller decides.
    """
    if merge_threshold < relate_threshold:
        raise ValueError("merge_threshold must be >= relate_threshold")
    reasons: list[str] = []
    sa, sb = str(a.get("state") or ""), str(b.get("state") or "")
    if sa == "revoked" or sb == "revoked":
        reasons.append("revoked_party")
        return {
            "outcome": "reject",
            "reasons": reasons,
            "title_sim": _title_sim(str(a.get("title") or ""), str(b.get("title") or "")),
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    if a.get("id") and b.get("id") and a.get("id") == b.get("id"):
        reasons.append("same_id")
        return {
            "outcome": "reject",
            "reasons": reasons,
            "title_sim": 1.0,
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    if str(a.get("scope") or "") != str(b.get("scope") or ""):
        reasons.append("scope_mismatch")
        return {
            "outcome": "reject",
            "reasons": reasons,
            "title_sim": _title_sim(str(a.get("title") or ""), str(b.get("title") or "")),
            "note": "MELD-shaped — no auto-merge (C7)",
        }

    ka, kb = a.get("conflict_key"), b.get("conflict_key")
    sim = _title_sim(str(a.get("title") or ""), str(b.get("title") or ""))
    contested = sa == "contested" or sb == "contested"
    if ka and kb and ka == kb:
        reasons.append("same_conflict_key")
        if contested:
            reasons.append("contested")
            outcome = "conflict"
        else:
            outcome = "merge"
        return {
            "outcome": outcome,
            "reasons": reasons,
            "title_sim": sim,
            "conflict_key": ka,
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    if contested or (
        ka
        and kb
        and ka != kb
        and sim >= relate_threshold
        and str(a.get("layer")) == str(b.get("layer"))
    ):
        if contested:
            reasons.append("contested")
        if ka and kb and ka != kb:
            reasons.append("distinct_conflict_keys")
        return {
            "outcome": "conflict",
            "reasons": reasons,
            "title_sim": sim,
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    if sim >= merge_threshold and str(a.get("layer")) == str(b.get("layer")):
        reasons.append(f"title_sim>={merge_threshold}")
        return {
            "outcome": "merge",
            "reasons": reasons,
            "title_sim": sim,
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    if sim >= relate_threshold:
        reasons.append(f"title_sim>={relate_threshold}")
        return {
            "outcome": "relate",
            "reasons": reasons,
            "title_sim": sim,
            "note": "MELD-shaped — no auto-merge (C7)",
        }
    reasons.append("insufficient_overlap")
    return {
        "outcome": "insert",
        "reasons": reasons,
        "title_sim": sim,
        "note": "MELD-shaped — treat as independent claim",
    }


def _source_trust(source: str, trusted: Sequence[str] | None) -> float:
    if not trusted:
        return 1.0
    allow = [s.strip() for s in trusted if s and str(s).strip()]
    if not allow:
        return 1.0
    src = str(source or "")
    for p in allow:
        if src == p or src.startswith(p):
            return 1.0
    return 0.25


def path_trust(
    entries: Iterable[dict[str, Any]],
    entry_id: str,
    *,
    trusted_sources: Sequence[str] | None = None,
    max_depth: int = 3,
) -> dict[str, Any]:
    """
    MAP-Graph-shaped multiplicative path trust along entry LINK ancestry.

    Trust starts at the entry's provenance.source, then multiplies neighbor
    source trusts for the best (highest) path within max_depth. No LLM.
    """
    if max_depth < 1 or max_depth > 5:
        raise ValueError("max_depth must be 1..5")
    by_id = {e["id"]: e for e in entries}
    if entry_id not in by_id:
        raise KeyError(entry_id)
    adj = _entry_links(by_id)
    root = by_id[entry_id]
    root_t = _source_trust(
        str((root.get("provenance") or {}).get("source") or ""), trusted_sources
    )
    best = root_t
    best_path = [entry_id]
    # BFS paths with running product
    queue: list[tuple[str, float, list[str]]] = [(entry_id, root_t, [entry_id])]
    seen_depth: dict[str, int] = {entry_id: 0}
    while queue:
        cur, trust, path = queue.pop(0)
        depth = len(path) - 1
        if depth >= max_depth:
            continue
        for nb in adj.get(cur, ()):
            if nb in path:
                continue
            nd = depth + 1
            if nb in seen_depth and seen_depth[nb] < nd:
                continue
            seen_depth[nb] = nd
            nb_e = by_id[nb]
            edge_t = _source_trust(
                str((nb_e.get("provenance") or {}).get("source") or ""),
                trusted_sources,
            )
            # State penalties (MAP-Graph: revoked/poisoned paths degrade)
            state = nb_e.get("state")
            if state == "revoked":
                edge_t *= 0.1
            elif state == "contested":
                edge_t *= 0.5
            elif state in {"superseded", "expired"}:
                edge_t *= 0.7
            nxt_trust = trust * edge_t
            nxt_path = path + [nb]
            if nxt_trust > best:
                best = nxt_trust
                best_path = nxt_path
            queue.append((nb, nxt_trust, nxt_path))
    return {
        "id": entry_id,
        "path_trust": round(best, 6),
        "root_trust": round(root_t, 6),
        "best_path": best_path,
        "trusted_sources": list(trusted_sources) if trusted_sources else None,
        "note": "MAP-Graph-shaped multiplicative path trust — not paper scores",
    }


UNTRUSTED_STATES = frozenset({"contested", "revoked", "quarantine"})


def lineage_trust(
    entries: Iterable[dict[str, Any]],
    entry_id: str,
    *,
    max_depth: int = 3,
) -> dict[str, Any]:
    """
    MemLineage-shaped trust label from entry LINK ancestry (deterministic).

    Labels: Trusted | Derived-Untrusted | Untrusted.
    No LLM / NLI — state walk only. Report-only unless Select refuses untrusted.
    """
    if max_depth < 1 or max_depth > 5:
        raise ValueError("max_depth must be 1..5")
    by_id = {e["id"]: e for e in entries}
    if entry_id not in by_id:
        raise KeyError(entry_id)
    self_state = str(by_id[entry_id].get("state") or "")
    if self_state in UNTRUSTED_STATES:
        return {
            "id": entry_id,
            "label": "Untrusted",
            "reason": f"self_state={self_state}",
            "untrusted_ancestors": [],
            "depth_checked": 0,
            "note": "MemLineage-shaped — fail-closed Select may refuse",
        }
    adj = _entry_links(by_id)
    untrusted: list[dict[str, Any]] = []
    seen: set[str] = {entry_id}
    frontier = {entry_id}
    for depth in range(1, max_depth + 1):
        nxt: set[str] = set()
        for cur in frontier:
            for nb in adj.get(cur, ()):
                if nb in seen:
                    continue
                seen.add(nb)
                nxt.add(nb)
                st = str(by_id[nb].get("state") or "")
                if st in UNTRUSTED_STATES:
                    untrusted.append({"id": nb, "state": st, "depth": depth, "via": cur})
        frontier = nxt
        if not frontier:
            break
    if untrusted:
        return {
            "id": entry_id,
            "label": "Derived-Untrusted",
            "reason": "untrusted_ancestor",
            "untrusted_ancestors": untrusted,
            "depth_checked": max_depth,
            "note": "MemLineage-shaped — fail-closed Select may refuse",
        }
    return {
        "id": entry_id,
        "label": "Trusted",
        "reason": "no_untrusted_ancestors",
        "untrusted_ancestors": [],
        "depth_checked": max_depth,
        "note": "MemLineage-shaped — fail-closed Select may refuse",
    }
