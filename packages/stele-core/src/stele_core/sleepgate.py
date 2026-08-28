"""SleepGate-shaped proactive-interference forgetting (stdlib; no LLM/NN).

Conflict-aware temporal tags + forget-gate plan + consolidation merge for
superseded associations. Not a learned KV-cache gate — Stele entry proxies.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _ts(e: Mapping[str, Any]) -> str:
    t = e.get("temporal") if isinstance(e.get("temporal"), Mapping) else {}
    return str(
        t.get("valid_from")
        or (e.get("provenance") or {}).get("written_at")
        or ""
    )


def conflict_tag(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str | None = None,
) -> dict[str, Any]:
    """
    Tag superseded tips under the same conflict_key (σ-flag proxy).

    Newest tip (by valid_from) is current; older same-key tips are superseded.
    """
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested", "quarantined"}
        and (
            conflict_key is None
            or str(e.get("conflict_key") or "") == conflict_key
        )
        and e.get("conflict_key")
    ]
    by_ck: dict[str, list[Mapping[str, Any]]] = {}
    for e in pool:
        by_ck.setdefault(str(e.get("conflict_key")), []).append(e)

    tags: list[dict[str, Any]] = []
    for ck, group in sorted(by_ck.items()):
        ordered = sorted(group, key=lambda e: (_ts(e), str(e.get("id"))))
        if len(ordered) < 2:
            tip = ordered[0] if ordered else None
            if tip:
                tags.append(
                    {
                        "id": tip.get("id"),
                        "conflict_key": ck,
                        "superseded": False,
                        "role": "current",
                    }
                )
            continue
        for e in ordered[:-1]:
            tags.append(
                {
                    "id": e.get("id"),
                    "conflict_key": ck,
                    "superseded": True,
                    "role": "stale",
                    "successor": ordered[-1].get("id"),
                }
            )
        tags.append(
            {
                "id": ordered[-1].get("id"),
                "conflict_key": ck,
                "superseded": False,
                "role": "current",
            }
        )
    return {
        "tags": tags,
        "superseded_count": sum(1 for t in tags if t.get("superseded")),
        "ok": True,
        "note": "SleepGate conflict_tag — temporal supersession σ proxy",
    }


def forget_gate_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str | None = None,
    keep_current: bool = True,
) -> dict[str, Any]:
    """
    Plan compress/evict for superseded (PI) entries — report-only.
    """
    tagged = conflict_tag(entries, conflict_key=conflict_key)
    actions: list[dict[str, Any]] = []
    for t in tagged.get("tags") or []:
        if t.get("superseded"):
            actions.append(
                {
                    "id": t.get("id"),
                    "action": "compress_or_evict",
                    "reason": "proactive_interference",
                    "successor": t.get("successor"),
                }
            )
        elif keep_current:
            actions.append(
                {
                    "id": t.get("id"),
                    "action": "keep",
                    "reason": "current_tip",
                }
            )
    return {
        "actions": actions,
        "evict_count": sum(
            1 for a in actions if a["action"] == "compress_or_evict"
        ),
        "ok": True,
        "note": "SleepGate forget_gate_plan — PI horizon shrink; not learned gate NN",
    }


def consolidate_survivors(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str,
) -> dict[str, Any]:
    """
    Merge related surviving tips under one conflict_key into a summary stub.

    Report-only — does not write. Keeps current tip id as anchor.
    """
    ck = str(conflict_key or "").strip()
    if not ck:
        raise SchemaError("conflict_key is required")
    group = [
        e
        for e in entries
        if str(e.get("conflict_key") or "") == ck
        and e.get("state") in {"promoted", "contested"}
    ]
    if not group:
        return {
            "conflict_key": ck,
            "anchor_id": None,
            "merged_from": [],
            "summary": "",
            "ok": False,
            "note": "SleepGate consolidate — empty group",
        }
    ordered = sorted(group, key=lambda e: (_ts(e), str(e.get("id"))))
    anchor = ordered[-1]
    titles = [str(e.get("title") or "") for e in ordered]
    summary = " | ".join(t for t in titles if t)[:240]
    return {
        "conflict_key": ck,
        "anchor_id": anchor.get("id"),
        "merged_from": [e.get("id") for e in ordered[:-1]],
        "summary": summary,
        "ok": True,
        "note": "SleepGate consolidate_survivors — compact summary; actor writes",
    }


def pi_depth_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str,
) -> dict[str, Any]:
    """Count active same-key tips competing (proactive interference depth)."""
    ck = str(conflict_key or "").strip()
    if not ck:
        raise SchemaError("conflict_key is required")
    active = [
        e
        for e in entries
        if str(e.get("conflict_key") or "") == ck
        and e.get("state") in {"promoted", "contested"}
    ]
    depth = len(active)
    return {
        "conflict_key": ck,
        "depth": depth,
        "ids": [e.get("id") for e in active],
        "high_interference": depth >= 3,
        "ok": True,
        "note": "SleepGate pi_depth_scan — PI depth proxy",
    }
