"""Dependency-guided rollback repair (stdlib; no LLM).

Shaped by arXiv:2608.10502 — typed memory dependency graph, preserve
candidates with independent trusted support, quarantine unsupported
derived state, selective replay plan. Report-only — never auto-writes.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError


def _children(entries: Sequence[Mapping[str, Any]]) -> dict[str, set[str]]:
    """ref → entries that LINK to ref (depends-on / derived-from)."""
    by_id = {str(e.get("id")): e for e in entries}
    kids: dict[str, set[str]] = {eid: set() for eid in by_id}
    for eid, e in by_id.items():
        for lnk in e.get("links") or []:
            if not isinstance(lnk, Mapping):
                continue
            if str(lnk.get("kind") or "") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in by_id:
                kids.setdefault(ref, set()).add(eid)
    return kids


def build_mem_action_graph(
    entries: Sequence[Mapping[str, Any]],
    *,
    actions: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Typed dependency graph: memory→memory via LINK; optional action nodes.

    Each action: {id, step?, memory_ids: [...]} — edges action→memory.
    """
    by_id = {str(e.get("id")): e for e in entries}
    kids = _children(entries)
    mem_edges: list[dict[str, str]] = []
    for parent, ch in kids.items():
        for child in sorted(ch):
            mem_edges.append({"from": child, "to": parent, "kind": "depends_on"})

    action_nodes: list[dict[str, Any]] = []
    action_edges: list[dict[str, str]] = []
    for a in actions or ():
        if not isinstance(a, Mapping):
            continue
        aid = str(a.get("id") or "").strip()
        if not aid:
            continue
        mids = [str(m) for m in (a.get("memory_ids") or []) if m]
        action_nodes.append(
            {
                "id": aid,
                "step": a.get("step"),
                "memory_ids": mids,
            }
        )
        for mid in mids:
            if mid in by_id:
                action_edges.append(
                    {"from": aid, "to": mid, "kind": "uses_memory"}
                )

    return {
        "memory_count": len(by_id),
        "action_count": len(action_nodes),
        "depends_on_edges": mem_edges,
        "uses_memory_edges": action_edges,
        "actions": action_nodes,
        "ok": True,
        "note": "deprepair build_mem_action_graph — LINK + optional actions",
    }


def dependency_trace(
    entries: Sequence[Mapping[str, Any]],
    fault_ids: Sequence[str],
    *,
    max_depth: int = 8,
) -> dict[str, Any]:
    """Downstream descendants of diagnosed faulty memories."""
    faults = {str(f) for f in fault_ids if f}
    if not faults:
        raise SchemaError("fault_ids is required")
    by_id = {str(e.get("id")): e for e in entries}
    missing = sorted(f for f in faults if f not in by_id)
    kids = _children(entries)
    seen: set[str] = set()
    layers: list[list[dict[str, Any]]] = []
    frontier = set(faults) & set(by_id)
    for depth in range(1, max_depth + 1):
        nxt: set[str] = set()
        layer: list[dict[str, Any]] = []
        for cur in sorted(frontier):
            for child in sorted(kids.get(cur, ())):
                if child in seen or child in faults:
                    continue
                seen.add(child)
                nxt.add(child)
                e = by_id[child]
                layer.append(
                    {
                        "id": child,
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
    affected = [n["id"] for layer in layers for n in layer]
    return {
        "fault_ids": sorted(faults),
        "missing_faults": missing,
        "affected_ids": affected,
        "affected_count": len(affected),
        "layers": layers,
        "ok": True,
        "note": "deprepair dependency_trace — downstream LINK reachability",
    }


def _source(entry: Mapping[str, Any]) -> str:
    prov = entry.get("provenance") or {}
    if isinstance(prov, Mapping):
        return str(prov.get("source") or "").strip()
    return ""


def preserve_independent(
    entries: Sequence[Mapping[str, Any]],
    fault_ids: Sequence[str],
    *,
    trusted_sources: Sequence[str] | None = None,
    max_depth: int = 8,
) -> dict[str, Any]:
    """
    Among cascade-affected entries, keep those with independent trusted support.

    Independent = provenance.source in trusted_sources AND not itself a fault.
    """
    faults = {str(f) for f in fault_ids if f}
    if not faults:
        raise SchemaError("fault_ids is required")
    trusted = {str(s) for s in (trusted_sources or []) if s}
    trace = dependency_trace(entries, sorted(faults), max_depth=max_depth)
    by_id = {str(e.get("id")): e for e in entries}
    preserve: list[dict[str, Any]] = []
    quarantine: list[dict[str, Any]] = []
    for eid in trace["affected_ids"]:
        e = by_id.get(eid)
        if e is None:
            continue
        src = _source(e)
        if trusted and src in trusted:
            preserve.append({"id": eid, "source": src, "reason": "trusted_source"})
        else:
            quarantine.append(
                {
                    "id": eid,
                    "source": src,
                    "reason": "no_independent_trusted_support",
                }
            )
    return {
        "fault_ids": sorted(faults),
        "preserve": preserve,
        "quarantine": quarantine,
        "preserve_count": len(preserve),
        "quarantine_count": len(quarantine),
        "ok": True,
        "note": "deprepair preserve_independent — trusted source ≠ fault path",
    }


def selective_replay_plan(
    entries: Sequence[Mapping[str, Any]],
    fault_ids: Sequence[str],
    *,
    trusted_sources: Sequence[str] | None = None,
    actions: Sequence[Mapping[str, Any]] | None = None,
    max_depth: int = 8,
) -> dict[str, Any]:
    """
    Report-only repair: deactivate faults, quarantine unsupported descendants,
    preserve independent support, list actions needing selective replay.
    """
    faults = {str(f) for f in fault_ids if f}
    if not faults:
        raise SchemaError("fault_ids is required")
    by_id = {str(e.get("id")): e for e in entries}
    graph = build_mem_action_graph(entries, actions=actions)
    trace = dependency_trace(entries, sorted(faults), max_depth=max_depth)
    ind = preserve_independent(
        entries,
        sorted(faults),
        trusted_sources=trusted_sources,
        max_depth=max_depth,
    )
    preserve_ids = {p["id"] for p in ind["preserve"]}
    quarantine_ids = {q["id"] for q in ind["quarantine"]}
    deactivate = sorted(f for f in faults if f in by_id)
    # Benign memories never in the cascade must not be collateral damage
    untouched = {
        str(e.get("id"))
        for e in entries
        if str(e.get("id")) not in faults
        and str(e.get("id")) not in set(trace["affected_ids"])
    }
    collateral = (set(deactivate) | quarantine_ids) & untouched
    benign_ok = len(collateral) == 0

    dirty = set(deactivate) | quarantine_ids
    replay: list[dict[str, Any]] = []
    for a in graph.get("actions") or []:
        mids = set(a.get("memory_ids") or [])
        hit = sorted(mids & dirty)
        if hit:
            replay.append(
                {
                    "action_id": a.get("id"),
                    "step": a.get("step"),
                    "dirty_memory_ids": hit,
                    "decision": "replay",
                }
            )

    return {
        "ok": True,
        "deactivate_ids": deactivate,
        "quarantine_ids": sorted(quarantine_ids),
        "preserve_ids": sorted(preserve_ids),
        "replay_actions": replay,
        "replay_count": len(replay),
        "benign_untouched": benign_ok,
        "collateral_ids": sorted(collateral),
        "selective_ok": len(deactivate) >= 1 and benign_ok,
        "graph": {
            "memory_count": graph["memory_count"],
            "action_count": graph["action_count"],
            "depends_on_edges": len(graph["depends_on_edges"]),
        },
        "note": "deprepair selective_replay_plan — report-only; actor applies",
    }
