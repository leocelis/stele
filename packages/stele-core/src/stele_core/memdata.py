"""MemoryData-shaped localized maintenance plans (stdlib; no LLM).

O7 finding: localize maintenance to a bounded subset — never global reorganize
on every write. Plans are report-only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def localized_maintenance_plan(
    seed_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    radius: int = 1,
    max_touch: int = 20,
) -> dict[str, Any]:
    """
    Bound maintenance to seed neighborhood (conflict_key + LINK hops ≤ radius).

    Returns touch set + actions (reverify / compress_candidate / leave).
    """
    seeds = [str(s) for s in seed_ids if s]
    if not seeds:
        raise SchemaError("seed_ids is required")
    if radius < 0:
        raise SchemaError("radius must be >= 0")
    if max_touch < 1:
        raise SchemaError("max_touch must be >= 1")

    by_id = {str(e.get("id")): e for e in entries}
    missing = [s for s in seeds if s not in by_id]
    # Adjacency via entry links
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

    # conflict_key cohorts
    by_ck: dict[str, set[str]] = {}
    for e in entries:
        ck = str(e.get("conflict_key") or "").strip()
        if ck:
            by_ck.setdefault(ck, set()).add(str(e.get("id")))

    touch: set[str] = set()
    frontier = {s for s in seeds if s in by_id}
    touch |= frontier
    for _ in range(radius):
        nxt: set[str] = set()
        for cur in frontier:
            nxt |= adj.get(cur) or set()
            ck = str((by_id.get(cur) or {}).get("conflict_key") or "").strip()
            if ck:
                nxt |= by_ck.get(ck) or set()
        nxt -= touch
        touch |= nxt
        frontier = nxt
        if len(touch) >= max_touch:
            break

    ordered = sorted(touch)[:max_touch]
    actions: list[dict[str, Any]] = []
    for eid in ordered:
        e = by_id[eid]
        state = e.get("state")
        if state == "contested":
            actions.append({"id": eid, "action": "reverify", "reason": "contested"})
        elif state == "quarantined":
            actions.append({"id": eid, "action": "leave", "reason": "await_oracle"})
        else:
            # Near-dup signal vs other touch members
            et = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
            twin = None
            for other in ordered:
                if other == eid:
                    continue
                o = by_id[other]
                if e.get("scope") and o.get("scope") and e.get("scope") != o.get("scope"):
                    continue
                ot = set(tokenize(f"{o.get('title')}\n{o.get('body')}"))
                if not et or not ot:
                    continue
                sim = len(et & ot) / len(et | ot)
                if sim >= 0.75:
                    twin = other
                    break
            if twin:
                actions.append(
                    {
                        "id": eid,
                        "action": "compress_candidate",
                        "pair": twin,
                        "reason": "near_duplicate_in_neighborhood",
                    }
                )
            else:
                actions.append(
                    {"id": eid, "action": "leave", "reason": "in_bound_stable"}
                )

    return {
        "seeds": seeds,
        "missing": missing,
        "radius": radius,
        "touch_ids": ordered,
        "touch_count": len(ordered),
        "max_touch": max_touch,
        "actions": actions,
        "global_reorganize": False,
        "ok": True,
        "note": "MemoryData localized_maintenance — O7 bound subset; not global reorganize",
    }


def maintenance_cost_compare(
    local_touch: int,
    *,
    store_size: int,
    local_unit: float = 1.0,
    global_unit: float = 1.0,
) -> dict[str, Any]:
    """
    Cost proxy: local maintenance vs full-store reorganize.
    """
    if local_touch < 0 or store_size < 0:
        raise SchemaError("sizes must be >= 0")
    local_cost = local_touch * local_unit
    global_cost = store_size * global_unit
    savings = global_cost - local_cost
    return {
        "local_cost": round(local_cost, 4),
        "global_cost": round(global_cost, 4),
        "savings": round(savings, 4),
        "prefer_local": local_cost <= global_cost,
        "ok": True,
        "note": "MemoryData cost compare — localized vs global reorganize proxy",
    }
