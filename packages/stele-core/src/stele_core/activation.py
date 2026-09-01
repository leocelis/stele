"""Spreading activation + density + retention — SYNAPSE/SodaMem/Oblivion shaped (C5)."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import Any

from stele_core.graph import _entry_links
from stele_core.lifecycle import age_days


def retention_score(
    entry: dict[str, Any],
    *,
    now: str,
    half_life_days: float = 30.0,
) -> float:
    """
    Oblivion-shaped retention in [0, 1] from freshness + usage reinforcement.

    score ≈ 2^(-age/half_life) * (1 + helpful boost), capped at 1.
    """
    if half_life_days <= 0:
        raise ValueError("half_life_days must be > 0")
    last = str((entry.get("temporal") or {}).get("last_verified") or "")
    if not last:
        base = 0.1
    else:
        age = max(0.0, age_days(last, now))
        base = 2.0 ** (-(age / half_life_days))
    usage = entry.get("usage") or {}
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    boost = min(0.35, 0.05 * max(0, helpful - harmful))
    if usage.get("pinned"):
        boost = max(boost, 0.25)
    return round(min(1.0, base + boost), 6)


def connection_density(
    entries: Iterable[dict[str, Any]],
    entry_id: str,
) -> dict[str, Any]:
    """SodaMem-shaped connection density: degree + contested/revoked penalties."""
    by_id = {e["id"]: e for e in entries}
    if entry_id not in by_id:
        raise KeyError(entry_id)
    adj = _entry_links(by_id)
    neighbors = adj.get(entry_id, set())
    degree = len(neighbors)
    # Normalize softly: 1 - 1/(1+degree)
    density = 1.0 - (1.0 / (1.0 + degree))
    state = by_id[entry_id].get("state")
    if state == "revoked":
        density *= 0.1
    elif state == "contested":
        density *= 0.5
    return {
        "id": entry_id,
        "degree": degree,
        "density": round(density, 6),
        "neighbors": sorted(neighbors),
        "note": "SodaMem-shaped connection density — not paper scores",
    }


def spread_activate(
    entries: Iterable[dict[str, Any]],
    *,
    seed_ids: Sequence[str],
    max_hops: int = 2,
    decay: float = 0.5,
    lateral_inhibit: float = 0.15,
) -> dict[str, Any]:
    """
    SYNAPSE-shaped spreading activation from seed entry ids along LINK edges.

    activation[v] = seed_mass for seeds; neighbors get decay^hop * mass.
    Lateral inhibition: subtract fraction of max neighbor activation (soft).
    """
    if max_hops < 1 or max_hops > 5:
        raise ValueError("max_hops must be 1..5")
    if not (0 < decay <= 1):
        raise ValueError("decay must be in (0, 1]")
    by_id = {e["id"]: e for e in entries}
    seeds = [s for s in seed_ids if s in by_id]
    if not seeds:
        return {
            "seeds": list(seed_ids),
            "activations": [],
            "note": "no valid seeds in store",
        }
    adj = _entry_links(by_id)
    act: dict[str, float] = {s: 1.0 for s in seeds}
    frontier = set(seeds)
    for hop in range(1, max_hops + 1):
        nxt: set[str] = set()
        mass = decay**hop
        for cur in frontier:
            for nb in adj.get(cur, ()):
                if nb in act and act[nb] >= mass:
                    continue
                # Skip non-live states for activation spread (still report if seeded)
                st = by_id[nb].get("state")
                if st in {"quarantined", "revoked"}:
                    continue
                act[nb] = max(act.get(nb, 0.0), mass)
                nxt.add(nb)
        frontier = nxt
        if not frontier:
            break
    # Lateral inhibition: damp nodes that are weaker than their strongest neighbor
    if lateral_inhibit > 0 and act:
        dampened = dict(act)
        for eid, val in act.items():
            nb_vals = [act[n] for n in adj.get(eid, ()) if n in act]
            if not nb_vals:
                continue
            peak = max(nb_vals)
            if peak > val:
                dampened[eid] = max(0.0, val - lateral_inhibit * (peak - val))
        act = dampened
    ranked = sorted(act.items(), key=lambda x: (-x[1], x[0]))
    return {
        "seeds": seeds,
        "max_hops": max_hops,
        "decay": decay,
        "activations": [
            {
                "id": eid,
                "activation": round(score, 6),
                "title": by_id[eid].get("title"),
                "state": by_id[eid].get("state"),
            }
            for eid, score in ranked
        ],
        "note": "SYNAPSE-shaped spreading activation — not LoCoMo claims",
    }
