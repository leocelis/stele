"""MemTxn-shaped Ordered PatchTest + Temporal Resolver (stdlib; no LLM).

Source-supported updates: cited span must appear in source body.
Temporal resolve: pick visible version under chronology contract.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.freshness import freshness_resolve
from stele_core.schema import SchemaError


def patch_test(
    pending: Mapping[str, Any],
    source: Mapping[str, Any],
    *,
    cited_span: str | None = None,
) -> dict[str, Any]:
    """
    Ordered PatchTest proxy: pending body/title must be supported by source text.

    When cited_span is given, it must appear in source body (case-insensitive).
    Otherwise require substantial token overlap of pending vs source.
    """
    src_blob = f"{source.get('title') or ''}\n{source.get('body') or ''}".lower()
    if not src_blob.strip():
        raise SchemaError("source body/title required")
    span = str(cited_span or "").strip()
    if span:
        supported = span.lower() in src_blob
        return {
            "ok": supported,
            "mode": "cited_span",
            "cited_span": span,
            "source_id": source.get("id"),
            "pending_title": pending.get("title"),
            "verdict": "accept" if supported else "reject",
            "note": "MemTxn Ordered PatchTest — span must occur in source",
        }
    from stele_core.index.lexical import tokenize

    pt = set(tokenize(f"{pending.get('title') or ''}\n{pending.get('body') or ''}"))
    st = set(tokenize(src_blob))
    if not pt:
        raise SchemaError("pending title/body required when cited_span omitted")
    overlap = len(pt & st) / max(len(pt), 1)
    supported = overlap >= 0.5
    return {
        "ok": supported,
        "mode": "token_overlap",
        "overlap": round(overlap, 4),
        "source_id": source.get("id"),
        "pending_title": pending.get("title"),
        "verdict": "accept" if supported else "reject",
        "note": "MemTxn Ordered PatchTest — ≥50% pending tokens in source",
    }


def temporal_resolve(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str,
) -> dict[str, Any]:
    """
    Temporal Resolver: visible tip under conflict_key via deterministic freshness.
    Contested/quarantined lose to promoted when timestamps equal (prefer promoted).
    """
    ck = str(conflict_key or "").strip()
    if not ck:
        raise SchemaError("conflict_key is required")
    pool = [
        e
        for e in entries
        if str(e.get("conflict_key") or "") == ck
        and e.get("state")
        in {"promoted", "contested", "quarantined", "superseded"}
    ]
    if not pool:
        return {
            "conflict_key": ck,
            "visible": None,
            "ok": False,
            "note": "No entries for temporal_resolve",
        }
    # Prefer promoted among equal freshness by sorting key augmentation
    def key(e: Mapping[str, Any]) -> tuple[Any, ...]:
        from stele_core.freshness import _freshness_key

        state_rank = {
            "promoted": 3,
            "contested": 2,
            "quarantined": 1,
            "superseded": 0,
        }.get(str(e.get("state")), 0)
        return (*_freshness_key(e), state_rank)

    ranked = sorted(pool, key=key, reverse=True)
    visible = ranked[0]
    # If winner is superseded, fall through to first non-superseded
    for e in ranked:
        if e.get("state") != "superseded":
            visible = e
            break
    fr = freshness_resolve([visible])
    return {
        "conflict_key": ck,
        "visible": {
            "id": visible.get("id"),
            "title": visible.get("title"),
            "state": visible.get("state"),
            "markers": (fr.get("winner") or {}).get("markers"),
        },
        "candidate_count": len(pool),
        "ok": True,
        "note": "MemTxn Temporal Resolver — deterministic chronology; not LLM pick",
    }


def recover_active_map(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_keys: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Complete-state recovery proxy: one visible tip per conflict_key.
    """
    keys = list(conflict_keys) if conflict_keys is not None else sorted(
        {
            str(e.get("conflict_key"))
            for e in entries
            if e.get("conflict_key")
        }
    )
    active: dict[str, Any] = {}
    for ck in keys:
        if not ck:
            continue
        report = temporal_resolve(entries, conflict_key=ck)
        if report.get("ok") and report.get("visible"):
            active[ck] = report["visible"]
    return {
        "active": active,
        "count": len(active),
        "ok": True,
        "note": "MemTxn recover_active_map — audited tips without physical write set",
    }
