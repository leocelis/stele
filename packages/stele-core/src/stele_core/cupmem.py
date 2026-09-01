"""CUPMem-shaped write-side adjudication + authorized retrieval (stdlib; no LLM).

Current-state Updating and Propagation-aware Memory: decide activate / revise /
block / unknown-current before query time. Proxies only — not STALE scores.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.execution import authority_score
from stele_core.schema import SchemaError
from stele_core.stale import parse_state_slot, state_resolution
from stele_core.toki_ops import tip_for_conflict_key


def adjudicate_update(
    entries: Iterable[Mapping[str, Any]],
    candidate: Mapping[str, Any],
    *,
    evidence: Sequence[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Write-side adjudication for an incoming candidate under a conflict_key.

    Returns action ∈ {activate, revise, block, unknown_current}.
    Does not write the store.
    """
    if not candidate:
        raise SchemaError("candidate is required")
    key = str(candidate.get("conflict_key") or "").strip()
    if not key:
        return {
            "action": "activate",
            "reason": "no_conflict_key",
            "slot": parse_state_slot(None),
            "tip_id": None,
            "note": "CUPMem-shaped — free slot write",
        }
    entries_list = list(entries)
    tip = tip_for_conflict_key(entries_list, key)
    slot = parse_state_slot(key)
    contested = [
        e
        for e in entries_list
        if str(e.get("conflict_key") or "") == key and e.get("state") == "contested"
    ]
    if contested:
        return {
            "action": "unknown_current",
            "reason": "contested_open",
            "slot": slot,
            "tip_id": (tip or {}).get("id"),
            "contested_ids": [e.get("id") for e in contested],
            "note": "CUPMem-shaped — unsafe slot without settled replacement",
        }
    has_ev = bool(evidence) or bool(candidate.get("evidence"))
    if tip is None:
        return {
            "action": "activate",
            "reason": "no_tip",
            "slot": slot,
            "tip_id": None,
            "note": "CUPMem-shaped — first claim for slot",
        }
    tip_auth = authority_score(tip)["authority"]
    cand_auth = authority_score(candidate)["authority"]
    if not has_ev and cand_auth <= tip_auth:
        return {
            "action": "block",
            "reason": "weaker_without_evidence",
            "slot": slot,
            "tip_id": tip.get("id"),
            "tip_authority": tip_auth,
            "candidate_authority": cand_auth,
            "note": "CUPMem-shaped — refuse overwrite without evidence",
        }
    if has_ev and cand_auth + 0.05 >= tip_auth:
        return {
            "action": "revise",
            "reason": "evidenced_competitive",
            "slot": slot,
            "tip_id": tip.get("id"),
            "tip_authority": tip_auth,
            "candidate_authority": cand_auth,
            "note": "CUPMem-shaped — revise tip under evidence",
        }
    if cand_auth > tip_auth:
        return {
            "action": "revise",
            "reason": "higher_authority",
            "slot": slot,
            "tip_id": tip.get("id"),
            "note": "CUPMem-shaped — revise tip",
        }
    return {
        "action": "block",
        "reason": "tip_dominates",
        "slot": slot,
        "tip_id": tip.get("id"),
        "tip_authority": tip_auth,
        "candidate_authority": cand_auth,
        "note": "CUPMem-shaped — keep tip",
    }


def unknown_current_slots(
    entries: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Slots that are unsafe for assertable retrieval: contested or unresolved
    multi-promoted keys (CUPMem unknown-current).
    """
    entries_list = list(entries)
    res = state_resolution(entries_list)
    unknown: list[dict[str, Any]] = []
    for row in res.get("unresolved") or []:
        unknown.append(
            {
                "conflict_key": row.get("conflict_key"),
                "reason": "unresolved_promoted",
                "promoted_ids": row.get("promoted_ids"),
                "slot": row.get("slot"),
            }
        )
    seen = {u["conflict_key"] for u in unknown}
    by_key: dict[str, list[str]] = {}
    for e in entries_list:
        if e.get("state") != "contested":
            continue
        key = str(e.get("conflict_key") or "")
        if not key or key in seen:
            continue
        by_key.setdefault(key, []).append(str(e.get("id")))
    for key, ids in sorted(by_key.items()):
        unknown.append(
            {
                "conflict_key": key,
                "reason": "contested_open",
                "contested_ids": ids,
                "slot": parse_state_slot(key),
            }
        )
    return {
        "unknown": unknown,
        "count": len(unknown),
        "ok": len(unknown) == 0,
        "note": "CUPMem unknown-current slots — not assertable until settled",
    }


def authorize_retrieval(
    entries: Iterable[Mapping[str, Any]],
    hit_ids: Sequence[str],
) -> dict[str, Any]:
    """
    Filter retrieval hits: drop superseded losers and unknown-current slots.

    Report-only filter plan — callers apply to context construction.
    """
    entries_list = list(entries)
    by_id = {str(e.get("id")): e for e in entries_list}
    unknown = unknown_current_slots(entries_list)
    blocked_keys = {
        str(u.get("conflict_key")) for u in unknown.get("unknown") or []
    }
    authorized: list[dict[str, Any]] = []
    denied: list[dict[str, Any]] = []
    for hid in hit_ids:
        e = by_id.get(str(hid))
        if e is None:
            denied.append({"id": hid, "reason": "missing"})
            continue
        state = str(e.get("state") or "")
        key = str(e.get("conflict_key") or "")
        if state in {"superseded", "revoked", "expired", "quarantined"}:
            denied.append({"id": hid, "reason": f"state={state}"})
            continue
        if key and key in blocked_keys:
            denied.append({"id": hid, "reason": "unknown_current_slot", "conflict_key": key})
            continue
        if state not in {"promoted"}:
            denied.append({"id": hid, "reason": f"state={state}"})
            continue
        authorized.append(
            {
                "id": hid,
                "title": e.get("title"),
                "conflict_key": key or None,
                "state": state,
            }
        )
    return {
        "authorized": authorized,
        "denied": denied,
        "authorized_count": len(authorized),
        "denied_count": len(denied),
        "unknown_slots": unknown.get("count", 0),
        "ok": True,
        "note": "CUPMem authorize retrieval — generation grounded in settled slots only",
    }
