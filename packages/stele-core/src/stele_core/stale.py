"""STALE-shaped stale-state probes + VTA transition verify (stdlib; no LLM)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError
from stele_core.strata import supersession_winners


def parse_state_slot(conflict_key: str | None) -> dict[str, str | None]:
    """Map conflict_key 'domain:slot' → state_domain / state_slot (CUPMem-shaped)."""
    if not conflict_key:
        return {"state_domain": None, "state_slot": None}
    key = str(conflict_key).strip()
    if ":" in key:
        domain, slot = key.split(":", 1)
        return {"state_domain": domain or None, "state_slot": slot or None}
    return {"state_domain": key, "state_slot": None}


def state_resolution(
    entries: Iterable[Mapping[str, Any]],
    *,
    conflict_key: str | None = None,
) -> dict[str, Any]:
    """
    STALE State Resolution proxy: is there a clear current winner per key?

    Reports keys with multiple promoted actives (unresolved) vs winners.
    """
    entries_list = list(entries)
    winners = supersession_winners(entries_list)
    by_key: dict[str, list[dict[str, Any]]] = {}
    for e in entries_list:
        if e.get("state") not in {"promoted", "superseded", "contested"}:
            continue
        key = e.get("conflict_key")
        if not key:
            continue
        if conflict_key and str(key) != str(conflict_key):
            continue
        by_key.setdefault(str(key), []).append(
            {
                "id": e.get("id"),
                "state": e.get("state"),
                "title": e.get("title"),
            }
        )
    resolved: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for key, rows in sorted(by_key.items()):
        promoted = [r for r in rows if r["state"] == "promoted"]
        winner = winners.get(key)
        if len(promoted) <= 1 and (not promoted or winner == promoted[0]["id"]):
            resolved.append(
                {
                    "conflict_key": key,
                    "winner": winner,
                    "slot": parse_state_slot(key),
                }
            )
        else:
            unresolved.append(
                {
                    "conflict_key": key,
                    "promoted_ids": [r["id"] for r in promoted],
                    "winner": winner,
                    "slot": parse_state_slot(key),
                }
            )
    return {
        "resolved": resolved,
        "unresolved": unresolved,
        "resolved_count": len(resolved),
        "unresolved_count": len(unresolved),
        "ok": len(unresolved) == 0,
        "note": "STALE State Resolution proxy — explicit keys only (no implicit NLI)",
    }


def premise_resistance(
    query: str,
    entries: Iterable[Mapping[str, Any]],
    *,
    winners: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    """
    STALE Premise Resistance proxy: query tokens align with superseded more
    than with current winners → refuse_premise.
    """
    q = set(tokenize(query or ""))
    if not q:
        return {
            "refuse_premise": False,
            "reason": "empty_query",
            "stale_hits": [],
            "current_hits": [],
            "note": "STALE Premise Resistance proxy",
        }
    entries_list = list(entries)
    win = winners or supersession_winners(entries_list)
    stale_hits: list[dict[str, Any]] = []
    current_hits: list[dict[str, Any]] = []
    for e in entries_list:
        key = e.get("conflict_key")
        text = f"{e.get('title') or ''} {e.get('body') or ''}"
        etok = set(tokenize(text))
        overlap = len(q & etok)
        if overlap < 1:
            continue
        eid = str(e.get("id") or "")
        is_winner = key and win.get(str(key)) == eid
        is_stale = e.get("state") == "superseded" or (
            key and win.get(str(key)) and win.get(str(key)) != eid
        )
        row = {"id": eid, "overlap": overlap, "conflict_key": key, "state": e.get("state")}
        if is_stale and not is_winner:
            stale_hits.append(row)
        elif is_winner or e.get("state") == "promoted":
            current_hits.append(row)
    stale_hits.sort(key=lambda x: -x["overlap"])
    current_hits.sort(key=lambda x: -x["overlap"])
    best_stale = stale_hits[0]["overlap"] if stale_hits else 0
    best_cur = current_hits[0]["overlap"] if current_hits else 0
    refuse = best_stale > best_cur and best_stale >= 2
    return {
        "refuse_premise": refuse,
        "best_stale_overlap": best_stale,
        "best_current_overlap": best_cur,
        "stale_hits": stale_hits[:10],
        "current_hits": current_hits[:10],
        "reason": "stale_tokens_dominate_query" if refuse else "current_or_neutral",
        "note": "STALE Premise Resistance proxy — token overlap heuristic, not IPA",
    }


def ipa_gap_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    live_hit_ids: Sequence[str],
) -> dict[str, Any]:
    """
    STALE IPA gap proxy: current winner exists but live Select still surfaces
    superseded ids (exclude_superseded was off).
    """
    entries_list = list(entries)
    by_id = {str(e.get("id")): e for e in entries_list}
    winners = supersession_winners(entries_list)
    gaps: list[dict[str, Any]] = []
    for eid in live_hit_ids:
        e = by_id.get(str(eid))
        if e is None:
            continue
        key = e.get("conflict_key")
        if not key:
            continue
        winner = winners.get(str(key))
        if winner and winner != eid and e.get("state") in {"superseded", "promoted"}:
            gaps.append(
                {
                    "stale_id": eid,
                    "winner_id": winner,
                    "conflict_key": key,
                    "evidence_visible": winner in set(map(str, live_hit_ids))
                    or by_id.get(winner) is not None,
                }
            )
    return {
        "gaps": gaps,
        "count": len(gaps),
        "ok": len(gaps) == 0,
        "note": "STALE IPA gap proxy — fix with exclude_superseded / VTA repair",
    }


def verify_transition(
    old: Mapping[str, Any],
    new: Mapping[str, Any],
) -> dict[str, Any]:
    """
    VTA-shaped provenance/chronology check for a supersede pair.

    Verified = provenance+chronology, not semantic truth (paper definition).
    """
    barriers: list[str] = []
    old_ts = str((old.get("temporal") or {}).get("valid_from") or "")
    new_ts = str((new.get("temporal") or {}).get("valid_from") or "")
    if old_ts and new_ts and new_ts < old_ts:
        barriers.append("chronology_new_before_old")
    ok_key = old.get("conflict_key") and old.get("conflict_key") == new.get("conflict_key")
    if not ok_key:
        barriers.append("conflict_key_mismatch")
    old_src = str((old.get("provenance") or {}).get("source") or "")
    new_src = str((new.get("provenance") or {}).get("source") or "")
    if not new_src:
        barriers.append("new_missing_source")
    sb = (old.get("temporal") or {}).get("superseded_by")
    if sb and str(sb) != str(new.get("id") or ""):
        barriers.append("superseded_by_mismatch")
    ok = len(barriers) == 0
    return {
        "ok": ok,
        "verified": ok,
        "barriers": barriers,
        "old_id": old.get("id"),
        "new_id": new.get("id"),
        "old_source": old_src,
        "new_source": new_src,
        "slot": parse_state_slot(str(old.get("conflict_key") or "")),
        "note": "VTA-shaped — provenance/chronology verify, not semantic entailment",
    }


def related_slot_scan(
    entries: Iterable[Mapping[str, Any]],
    conflict_key: str,
) -> dict[str, Any]:
    """Propagation-aware candidates in the same state_domain (CUPMem-shaped)."""
    slot = parse_state_slot(conflict_key)
    domain = slot.get("state_domain")
    if not domain:
        raise SchemaError("conflict_key must include a domain prefix")
    related: list[dict[str, Any]] = []
    for e in entries:
        key = e.get("conflict_key")
        if not key:
            continue
        parsed = parse_state_slot(str(key))
        if parsed.get("state_domain") != domain:
            continue
        if str(key) == str(conflict_key):
            continue
        related.append(
            {
                "id": e.get("id"),
                "conflict_key": key,
                "state": e.get("state"),
                "slot": parsed,
                "needs_reverify": e.get("state") == "promoted",
            }
        )
    return {
        "domain": domain,
        "origin_key": conflict_key,
        "related": related,
        "count": len(related),
        "reverify_count": sum(1 for r in related if r.get("needs_reverify")),
        "note": "same-domain propagation candidates — human/oracle reverify",
    }
