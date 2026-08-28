"""Reversible archive tier — utility-weighted forgetting (stdlib; no LLM).

Moves promoted episodic tips out of Select without delete. Unarchive restores
promoted. Report-only plan never mutates; apply requires actor.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from stele_core.fademem import fade_strength
from stele_core.lifecycle import age_days
from stele_core.schema import SchemaError
from stele_core.worth import memory_worth

# Guidance layers stay in Select — archive targets episodic-like notes.
ARCHIVE_ELIGIBLE_LAYERS = frozenset({"goal", "issue"})


def archive_eligible(
    entry: Mapping[str, Any],
    *,
    now: str,
    min_age_days: float = 14.0,
    max_fade_strength: float = 0.35,
    mw_ceiling: float = 0.45,
) -> dict[str, Any]:
    """
    Decide if one entry may enter the archive queue.

    Never eligible: pinned, non-promoted, guidance layers, contested.
    """
    eid = entry.get("id")
    state = str(entry.get("state") or "")
    layer = str(entry.get("layer") or "")
    usage = entry.get("usage") or {}
    if state != "promoted":
        return {"id": eid, "eligible": False, "reasons": ["not_promoted"]}
    if usage.get("pinned"):
        return {"id": eid, "eligible": False, "reasons": ["pinned"]}
    if layer not in ARCHIVE_ELIGIBLE_LAYERS:
        return {"id": eid, "eligible": False, "reasons": ["guidance_layer"]}
    last = str((entry.get("temporal") or {}).get("last_verified") or "")
    if not last:
        last = str((entry.get("provenance") or {}).get("written_at") or "")
    if not last:
        return {"id": eid, "eligible": False, "reasons": ["no_timestamp"]}
    age = age_days(last, now)
    if age < min_age_days:
        return {
            "id": eid,
            "eligible": False,
            "reasons": ["too_young"],
            "age_days": round(age, 2),
        }
    fade = fade_strength(entry, now=now)
    mw = memory_worth(entry)
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    unused = helpful + harmful == 0
    weak_fade = float(fade.get("strength") or 1) <= max_fade_strength
    low_mw = bool(mw.get("known") and float(mw.get("mw") or 1) <= mw_ceiling)
    if not (weak_fade or low_mw or unused):
        return {
            "id": eid,
            "eligible": False,
            "reasons": ["still_useful"],
            "fade_strength": fade.get("strength"),
            "mw": mw.get("mw"),
            "age_days": round(age, 2),
        }
    why: list[str] = []
    if weak_fade:
        why.append("weak_fade")
    if low_mw:
        why.append("low_mw")
    if unused:
        why.append("unused")
    return {
        "id": eid,
        "eligible": True,
        "reasons": why,
        "fade_strength": fade.get("strength"),
        "mw": mw.get("mw"),
        "age_days": round(age, 2),
        "layer": layer,
        "title": entry.get("title"),
    }


def archive_plan(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    min_age_days: float = 14.0,
    max_fade_strength: float = 0.35,
    mw_ceiling: float = 0.45,
    limit: int = 50,
) -> dict[str, Any]:
    """Report-only archive candidates — never mutates."""
    if min_age_days < 0:
        raise SchemaError("min_age_days must be >= 0")
    candidates: list[dict[str, Any]] = []
    skipped = 0
    for e in entries:
        report = archive_eligible(
            e,
            now=now,
            min_age_days=min_age_days,
            max_fade_strength=max_fade_strength,
            mw_ceiling=mw_ceiling,
        )
        if report.get("eligible"):
            candidates.append(report)
        else:
            skipped += 1
    candidates.sort(
        key=lambda r: (
            float(r.get("fade_strength") or 0),
            float(r.get("mw") if r.get("mw") is not None else 1),
            str(r.get("id")),
        )
    )
    candidates = candidates[: max(1, int(limit))]
    return {
        "candidates": candidates,
        "count": len(candidates),
        "skipped": skipped,
        "ok": True,
        "note": "Archive plan — reversible utility-weighted forgetting; never auto-deletes",
    }


def list_archived(entries: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = [
        {
            "id": e.get("id"),
            "title": e.get("title"),
            "layer": e.get("layer"),
            "scope": e.get("scope"),
        }
        for e in entries
        if e.get("state") == "archived"
    ]
    return {"archived": rows, "count": len(rows)}
