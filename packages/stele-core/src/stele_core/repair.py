"""MemoRepair-shaped cascade impact, barrier withdraw, repair plan (stdlib)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError


def cascade_descendants(
    entries: Iterable[dict[str, Any]],
    fault_id: str,
    *,
    max_depth: int = 5,
) -> dict[str, Any]:
    """
    Descendants that LINK (kind=entry) toward a fault source — cascade exposure set.

    Uses undirected LINK neighborhood (blast_radius) then filters nodes that
    transitively reach the fault via directed out-links (depends-on semantics).
    """
    by_id = {e["id"]: e for e in entries}
    if fault_id not in by_id:
        raise KeyError(fault_id)
    # Directed: entry → ref means depends-on / derived-from
    children: dict[str, set[str]] = {eid: set() for eid in by_id}
    for eid, e in by_id.items():
        for lnk in e.get("links") or []:
            if lnk.get("kind") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in by_id:
                # eid depends on ref → eid is descendant of ref
                children.setdefault(ref, set()).add(eid)
    seen: set[str] = set()
    layers: list[list[dict[str, Any]]] = []
    frontier = {fault_id}
    for depth in range(1, max_depth + 1):
        nxt: set[str] = set()
        layer: list[dict[str, Any]] = []
        for cur in frontier:
            for child in children.get(cur, ()):
                if child in seen or child == fault_id:
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
    flat = [n for layer in layers for n in layer]
    promoted_exposed = [
        n for n in flat if n.get("state") == "promoted"
    ]
    return {
        "fault_id": fault_id,
        "descendant_count": len(flat),
        "promoted_exposed": len(promoted_exposed),
        "layers": layers,
        "ids": [n["id"] for n in flat],
        "promoted_ids": [n["id"] for n in promoted_exposed],
        "note": "MemoRepair-shaped cascade — directed depends-on LINKs",
    }


def cascade_exposure(
    entries: Iterable[dict[str, Any]],
    fault_id: str,
    *,
    max_depth: int = 5,
) -> dict[str, Any]:
    """Metric: promoted descendants still in service after fault (invalidated exposure)."""
    impact = cascade_descendants(entries, fault_id, max_depth=max_depth)
    fault = next((e for e in entries if e.get("id") == fault_id), None)
    fault_state = str((fault or {}).get("state") or "")
    return {
        "fault_id": fault_id,
        "fault_state": fault_state,
        "promoted_exposed": impact["promoted_exposed"],
        "descendant_count": impact["descendant_count"],
        "exposure_ratio": (
            round(impact["promoted_exposed"] / impact["descendant_count"], 4)
            if impact["descendant_count"]
            else 0.0
        ),
        "promoted_ids": impact["promoted_ids"],
        "note": "0 promoted_exposed after barrier withdraw is the MemoRepair goal proxy",
    }


def repair_plan(
    entries: Iterable[dict[str, Any]],
    fault_id: str,
    *,
    lambda_cost: float = 0.5,
    max_depth: int = 5,
    budget: int | None = None,
) -> dict[str, Any]:
    """
    Predecessor-closed repair selection proxy (MemoRepair-shaped).

    Score per candidate: value − λ·cost with value from usage.helpful + pin,
    cost=1. Greedy topo over depends-on DAG — prefer `repair_select_mincut` for
    exact maximum-weight predecessor closure.
    """
    if lambda_cost < 0:
        raise SchemaError("lambda_cost must be >= 0")
    if budget is not None and budget < 0:
        raise SchemaError("budget must be >= 0")
    by_id = {e["id"]: e for e in entries}
    impact = cascade_descendants(entries, fault_id, max_depth=max_depth)
    candidates = list(impact["ids"])
    if not candidates:
        return {
            "fault_id": fault_id,
            "selected": [],
            "skipped": [],
            "lambda_cost": lambda_cost,
            "realized_cost": 0,
            "method": "greedy",
            "note": "no descendants — nothing to repair",
        }

    # Parents: required predecessors within candidate set (link refs that are also candidates or fault)
    cand_set = set(candidates) | {fault_id}
    parents: dict[str, set[str]] = {c: set() for c in candidates}
    for cid in candidates:
        e = by_id[cid]
        for lnk in e.get("links") or []:
            if lnk.get("kind") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in cand_set and ref != cid:
                parents[cid].add(ref)

    def value_of(eid: str) -> float:
        e = by_id[eid]
        usage = e.get("usage") or {}
        helpful = float(usage.get("helpful") or 0)
        pin = 1.0 if usage.get("pinned") else 0.0
        return 1.0 + helpful + pin

    scored: list[tuple[str, float, float, int]] = []
    depth_of = {n["id"]: int(n["depth"]) for layer in impact["layers"] for n in layer}
    for cid in candidates:
        v = value_of(cid)
        cost = 1.0
        score = v - lambda_cost * cost
        scored.append((cid, score, v, depth_of.get(cid, 99)))
    # Depth-first then score — improves predecessor-closure success vs pure score sort
    scored.sort(key=lambda x: (x[3], -x[1], x[0]))

    selected: list[str] = []
    selected_set: set[str] = set()
    skipped: list[dict[str, Any]] = []
    realized = 0
    for cid, score, v, _depth in scored:
        if score < 0:
            skipped.append({"id": cid, "reason": "negative_score", "score": round(score, 4)})
            continue
        preds = {p for p in parents[cid] if p != fault_id}
        if not preds.issubset(selected_set):
            missing = sorted(preds - selected_set)
            skipped.append(
                {"id": cid, "reason": "predecessor_not_selected", "missing": missing}
            )
            continue
        if budget is not None and realized + 1 > budget:
            skipped.append({"id": cid, "reason": "budget", "score": round(score, 4)})
            continue
        selected.append(cid)
        selected_set.add(cid)
        realized += 1

    return {
        "fault_id": fault_id,
        "selected": selected,
        "skipped": skipped,
        "lambda_cost": lambda_cost,
        "budget": budget,
        "realized_cost": realized,
        "candidate_count": len(candidates),
        "method": "greedy",
        "note": "greedy predecessor-closure proxy — use repair_select_mincut for exact",
    }


_INF = 10**12


def _edmonds_karp(
    capacity: dict[str, dict[str, float]], source: str, sink: str
) -> tuple[float, dict[str, dict[str, float]]]:
    """Max-flow / min-cut via Edmonds–Karp. Returns (flow, residual)."""
    residual: dict[str, dict[str, float]] = {
        u: dict(vs) for u, vs in capacity.items()
    }
    for u in list(capacity):
        for v in capacity[u]:
            residual.setdefault(v, {})
            residual[v].setdefault(u, 0.0)

    def bfs() -> list[str] | None:
        parent: dict[str, str | None] = {source: None}
        q = [source]
        while q:
            u = q.pop(0)
            for v, cap in residual.get(u, {}).items():
                if v not in parent and cap > 1e-12:
                    parent[v] = u
                    if v == sink:
                        path = [sink]
                        cur = sink
                        while cur != source:
                            cur = parent[cur]  # type: ignore[assignment]
                            path.append(cur)
                        path.reverse()
                        return path
                    q.append(v)
        return None

    flow = 0.0
    while True:
        path = bfs()
        if not path:
            break
        bott = min(residual[path[i]][path[i + 1]] for i in range(len(path) - 1))
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            residual[u][v] -= bott
            residual[v][u] = residual[v].get(u, 0.0) + bott
        flow += bott
    return flow, residual


def repair_select_mincut(
    entries: Iterable[dict[str, Any]],
    fault_id: str,
    *,
    lambda_cost: float = 0.5,
    max_depth: int = 5,
) -> dict[str, Any]:
    """
    Exact maximum-weight predecessor-closed repair selection via s–t min-cut.

    MemoRepair Theorem 1 shaped (Picard closure reduction). Stdlib Edmonds–Karp.
    Budget truncation is not applied — exact closure for the full candidate family.
    """
    if lambda_cost < 0:
        raise SchemaError("lambda_cost must be >= 0")
    entries_list = list(entries)
    by_id = {e["id"]: e for e in entries_list}
    if fault_id not in by_id:
        raise KeyError(fault_id)
    impact = cascade_descendants(entries_list, fault_id, max_depth=max_depth)
    candidates = list(impact["ids"])
    if not candidates:
        return {
            "fault_id": fault_id,
            "selected": [],
            "skipped": [],
            "lambda_cost": lambda_cost,
            "realized_cost": 0,
            "method": "mincut",
            "max_flow": 0.0,
            "objective": 0.0,
            "note": "no descendants — nothing to repair (exact min-cut)",
        }

    cand_set = set(candidates) | {fault_id}
    parents: dict[str, set[str]] = {c: set() for c in candidates}
    for cid in candidates:
        e = by_id[cid]
        for lnk in e.get("links") or []:
            if lnk.get("kind") != "entry":
                continue
            ref = str(lnk.get("ref") or "")
            if ref in cand_set and ref != cid and ref != fault_id:
                parents[cid].add(ref)

    def value_of(eid: str) -> float:
        e = by_id[eid]
        usage = e.get("usage") or {}
        helpful = float(usage.get("helpful") or 0)
        pin = 1.0 if usage.get("pinned") else 0.0
        return 1.0 + helpful + pin

    weights: dict[str, float] = {}
    for cid in candidates:
        weights[cid] = value_of(cid) - lambda_cost * 1.0

    source, sink = "__s__", "__t__"
    capacity: dict[str, dict[str, float]] = {source: {}, sink: {}}
    for cid in candidates:
        capacity.setdefault(cid, {})
        w = weights[cid]
        if w > 0:
            capacity[source][cid] = w
        elif w < 0:
            capacity[cid][sink] = -w
        # precedence: selecting j requires parent i → edge j→i capacity INF
        for p in parents[cid]:
            if p in cand_set and p != fault_id:
                capacity.setdefault(cid, {})
                capacity[cid][p] = float(_INF)

    flow, residual = _edmonds_karp(capacity, source, sink)

    # Source-side nodes in residual = selected closed set
    reachable: set[str] = set()
    stack = [source]
    while stack:
        u = stack.pop()
        if u in reachable:
            continue
        reachable.add(u)
        for v, cap in residual.get(u, {}).items():
            if cap > 1e-12 and v not in reachable:
                stack.append(v)
    selected = sorted(n for n in candidates if n in reachable)
    skipped = [
        {
            "id": cid,
            "reason": "not_in_mincut_closure",
            "weight": round(weights[cid], 4),
        }
        for cid in candidates
        if cid not in reachable
    ]
    objective = sum(weights[cid] for cid in selected)
    return {
        "fault_id": fault_id,
        "selected": selected,
        "skipped": skipped,
        "lambda_cost": lambda_cost,
        "realized_cost": len(selected),
        "candidate_count": len(candidates),
        "method": "mincut",
        "max_flow": round(flow, 6),
        "objective": round(objective, 6),
        "weights": {k: round(v, 4) for k, v in weights.items()},
        "note": "exact MemoRepair-shaped s–t min-cut closure — not ToolBench scores",
    }


def non_revival_probe(
    entries: Iterable[Mapping[str, Any]],
    search_hits: Sequence[Mapping[str, Any]],
    *,
    forbidden_ids: Sequence[str],
) -> dict[str, Any]:
    """
    GPM non-revival: revoked/deleted IDs must not appear in Select hits.
    """
    hit_ids = {str(h.get("id") or "") for h in search_hits}
    leaks = [i for i in forbidden_ids if i in hit_ids]
    by_id = {str(e.get("id")): e for e in entries}
    states = {i: str((by_id.get(i) or {}).get("state") or "missing") for i in forbidden_ids}
    return {
        "ok": len(leaks) == 0,
        "leaks": leaks,
        "forbidden_states": states,
        "note": "non-revival probe — revoked/withdrawn must not surface in SEARCH",
    }
