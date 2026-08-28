"""MemPoison + Salami-shaped compositional / dormant threat scan (stdlib; no LLM).

Shaped by MemPoison (arXiv:2607.14651) L1/L2/L3 ladder and Salami / MemCollusion
(arXiv:2608.01637): write-time L1 filters miss coalitions whose harm appears only
when fragments co-retrieve or a trigger context wakes a dormant payload.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from itertools import combinations
from typing import Any

from stele_core.schema import SchemaError

# Semantic slots that salami fragments may split across
_SLOTS: dict[str, tuple[str, ...]] = {
    "directive": (
        "ignore prior",
        "ignore previous",
        "disregard previous",
        "override safety",
        "developer mode",
        "system note:",
    ),
    "exfil": (
        "exfiltrate",
        "send all data",
        "bcc ",
        "blind carbon",
        "forward a copy",
        "redirect payment",
        "unauthorized recipient",
    ),
    "destination": (
        "@evil.",
        "@attacker",
        "adversary@",
        "deploy.attacker",
        "http://evil",
        "https://evil",
        "mailto:adversary",
    ),
    "trigger": (
        "when generating",
        "when asked",
        "if the user asks",
        "end-of-month",
        "only when",
        "when preparing the report",
        "dormant until",
    ),
    "authority": (
        "official policy",
        "approved by security",
        "compliance requires",
        "mandatory workflow",
    ),
}

_CRITICAL_COMBO = frozenset({"exfil", "destination"})
_L1_STRONG = frozenset({"directive", "exfil"})


def _text(entry: Mapping[str, Any]) -> str:
    return f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()


def slot_coverage(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Which salami/MemPoison semantic slots fire on one entry."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    blob = _text(entry)
    hits: dict[str, list[str]] = {}
    for slot, markers in _SLOTS.items():
        found = [m for m in markers if m in blob]
        if found:
            hits[slot] = found
    return {
        "id": entry.get("id"),
        "slots": sorted(hits),
        "markers": hits,
        "slot_count": len(hits),
        "ok": True,
        "note": "mempoison slot_coverage — fragment taxonomy",
    }


def threat_tier_classify(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    MemPoison ladder for one record.

    L1 = strong single-record harm (directive+exfil or exfil+destination).
    L3 = trigger-conditioned dormant (trigger slot present).
    L2 = partial slots only (compositional candidate).
    clean = no slots.
    """
    cov = slot_coverage(entry)
    slots = set(cov["slots"])
    tier = "clean"
    reason = "no_slots"
    if slots & _L1_STRONG == _L1_STRONG or slots >= _CRITICAL_COMBO:
        tier = "L1"
        reason = "single_record_explicit"
    elif "trigger" in slots:
        tier = "L3"
        reason = "context_triggered_dormant"
    elif slots:
        tier = "L2"
        reason = "partial_slots_compositional_candidate"
    return {
        "id": entry.get("id"),
        "tier": tier,
        "reason": reason,
        "slots": cov["slots"],
        "ok": True,
        "note": "MemPoison threat_tier_classify — L1/L2/L3 ladder proxy",
    }


def dormant_trigger_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """List L3-shaped dormant / trigger-conditioned entries."""
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    rows: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        t = threat_tier_classify(e)
        if t["tier"] != "L3":
            continue
        rows.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "state": e.get("state"),
                "slots": t["slots"],
            }
        )
        if len(rows) >= limit:
            break
    return {
        "dormant": rows,
        "count": len(rows),
        "ok": True,
        "note": "MemPoison dormant_trigger_scan — L3 sleeper proxy",
    }


def compositional_coalition_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    min_slots: int = 3,
    max_coalition: int = 4,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Find small sets of entries whose union covers ≥ min_slots while no
    member alone is L1 — Salami / MemCollusion compositional risk.
    """
    if min_slots < 2:
        raise SchemaError("min_slots must be >= 2")
    if max_coalition < 2 or max_coalition > 6:
        raise SchemaError("max_coalition must be in [2, 6]")
    candidates: list[tuple[str, frozenset[str], Mapping[str, Any]]] = []
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        if e.get("state") not in {None, "promoted", "contested", "quarantined"}:
            # still include quarantined — they may co-retrieve with include_contested
            pass
        t = threat_tier_classify(e)
        if t["tier"] == "clean":
            continue
        if t["tier"] == "L1":
            continue  # L1 is single-record; not a salami fragment
        slots = frozenset(t["slots"])
        if not slots:
            continue
        eid = str(e.get("id") or "")
        if eid:
            candidates.append((eid, slots, e))

    coalitions: list[dict[str, Any]] = []
    seen: set[frozenset[str]] = set()
    n = len(candidates)
    for k in range(2, min(max_coalition, n) + 1):
        for combo in combinations(range(n), k):
            ids = frozenset(candidates[i][0] for i in combo)
            if ids in seen:
                continue
            union: set[str] = set()
            for i in combo:
                union |= set(candidates[i][1])
            if len(union) < min_slots:
                continue
            # Prefer coalitions that complete a critical combo across members
            critical = bool(union >= _CRITICAL_COMBO) or (
                "directive" in union and "destination" in union
            )
            if not critical and len(union) < min_slots:
                continue
            if not critical and "exfil" not in union and "destination" not in union:
                # weak coalition — skip unless very full
                if len(union) < min_slots + 1:
                    continue
            seen.add(ids)
            coalitions.append(
                {
                    "member_ids": sorted(ids),
                    "union_slots": sorted(union),
                    "slot_count": len(union),
                    "critical": critical,
                    "size": len(ids),
                }
            )
            if len(coalitions) >= limit:
                break
        if len(coalitions) >= limit:
            break

    coalitions.sort(key=lambda c: (-int(c["critical"]), -c["slot_count"], c["size"]))
    return {
        "coalitions": coalitions,
        "count": len(coalitions),
        "fragment_candidates": len(candidates),
        "ok": True,
        "note": "Salami compositional_coalition_scan — joint slots, no single L1",
    }


def collusion_risk_gate(
    hits: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]] | None = None,
    *,
    min_slots: int = 3,
) -> dict[str, Any]:
    """
    Retrieval-time gate: deny when hit set forms a critical salami coalition.
    """
    by_id = {str(e.get("id")): e for e in (entries or []) if isinstance(e, Mapping)}
    pack: list[Mapping[str, Any]] = []
    for h in hits:
        if not isinstance(h, Mapping):
            continue
        eid = str(h.get("id") or "")
        pack.append(by_id.get(eid) or h)
    scan = compositional_coalition_scan(pack, min_slots=min_slots, limit=5)
    critical = [c for c in scan["coalitions"] if c.get("critical")]
    # Also deny if any single hit is L1
    l1 = [threat_tier_classify(e) for e in pack if threat_tier_classify(e)["tier"] == "L1"]
    if l1:
        decision = "deny"
        reason = "l1_in_pack"
    elif critical:
        decision = "deny"
        reason = "critical_coalition"
    elif scan["count"]:
        decision = "review"
        reason = "weak_coalition"
    else:
        decision = "admit"
        reason = "no_coalition"
    return {
        "decision": decision,
        "reason": reason,
        "l1_count": len(l1),
        "critical_coalitions": critical,
        "coalition_count": scan["count"],
        "ok": True,
        "note": "Salami collusion_risk_gate — retrieval pack firewall",
    }


def mempoison_ladder_report(
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 100,
) -> dict[str, Any]:
    """Inventory store by MemPoison L1/L2/L3 + coalition count."""
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    buckets: dict[str, list[dict[str, Any]]] = {
        "L1": [],
        "L2": [],
        "L3": [],
        "clean": [],
    }
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        t = threat_tier_classify(e)
        row = {
            "id": e.get("id"),
            "title": e.get("title"),
            "state": e.get("state"),
            "slots": t["slots"],
        }
        buckets[t["tier"]].append(row)
    coal = compositional_coalition_scan(entries, limit=limit)
    dorm = dormant_trigger_scan(entries, limit=limit)
    return {
        "counts": {k: len(v) for k, v in buckets.items()},
        "L1": buckets["L1"][:limit],
        "L2": buckets["L2"][:limit],
        "L3": buckets["L3"][:limit],
        "coalition_count": coal["count"],
        "dormant_count": dorm["count"],
        "ok": True,
        "note": "MemPoison mempoison_ladder_report — L1–L3 inventory proxy",
    }


def salami_pair_probe(
    entry_a: Mapping[str, Any],
    entry_b: Mapping[str, Any],
) -> dict[str, Any]:
    """
    Two-fragment probe: do A+B form a critical coalition neither alone is L1?
    """
    ta = threat_tier_classify(entry_a)
    tb = threat_tier_classify(entry_b)
    if ta["tier"] == "L1" or tb["tier"] == "L1":
        return {
            "collusive": False,
            "reason": "member_is_l1",
            "tiers": [ta["tier"], tb["tier"]],
            "union_slots": sorted(set(ta["slots"]) | set(tb["slots"])),
            "ok": True,
            "note": "salami_pair_probe",
        }
    union = set(ta["slots"]) | set(tb["slots"])
    critical = union >= _CRITICAL_COMBO or (
        "directive" in union and "destination" in union
    )
    collusive = critical and ta["tier"] != "clean" and tb["tier"] != "clean"
    return {
        "collusive": collusive,
        "critical": critical,
        "reason": "critical_union" if collusive else "no_critical_union",
        "tiers": [ta["tier"], tb["tier"]],
        "union_slots": sorted(union),
        "ok": True,
        "note": "Salami salami_pair_probe — two-fragment collusion",
    }
