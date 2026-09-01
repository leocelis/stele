"""Deterministic freshness assembly (stdlib; no LLM).

Bottleneck on conflict resolution is assembly, not storage (arXiv:2606.01435).
Extract version markers → Python max(timestamp|serial) — never ask an LLM
which memory is fresher.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

_SERIAL_RE = re.compile(
    r"\b(?:v|version|rev|serial|seq)[_\-\s]?(\d+)\b", re.IGNORECASE
)
_ISO_RE = re.compile(r"\b(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z?)?)\b")


def extract_version_markers(entry: Mapping[str, Any]) -> dict[str, Any]:
    """Pull serial / ISO markers from body + temporal fields."""
    blob = f"{entry.get('title') or ''}\n{entry.get('body') or ''}"
    serials = [int(m) for m in _SERIAL_RE.findall(blob)]
    dates = list(_ISO_RE.findall(blob))
    temporal = entry.get("temporal") or {}
    last_verified = str(temporal.get("last_verified") or "")
    valid_from = str(temporal.get("valid_from") or "")
    if last_verified:
        dates.append(last_verified)
    if valid_from:
        dates.append(valid_from)
    dates = sorted(set(d for d in dates if d))
    max_serial = max(serials) if serials else None
    max_ts = max(dates) if dates else None
    return {
        "id": entry.get("id"),
        "serials": sorted(set(serials)),
        "dates": dates,
        "max_serial": max_serial,
        "max_ts": max_ts,
        "last_verified": last_verified or None,
        "ok": True,
        "note": "Deterministic version markers — regex + temporal fields",
    }


def _freshness_key(entry: Mapping[str, Any]) -> tuple[Any, ...]:
    m = extract_version_markers(entry)
    # Prefer serial when present, else timestamp (ISO strings sort lexicographically)
    serial = m.get("max_serial")
    ts = m.get("max_ts") or ""
    # Higher is fresher: (has_serial, serial, ts, id)
    return (
        1 if serial is not None else 0,
        int(serial or 0),
        str(ts),
        str(entry.get("id") or ""),
    )


def freshness_resolve(
    entries: Sequence[Mapping[str, Any]],
    *,
    conflict_key: str | None = None,
) -> dict[str, Any]:
    """
    Among candidates (optionally one conflict_key), pick the freshest via max().
    """
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested", "quarantined"}
    ]
    if conflict_key is not None:
        ck = str(conflict_key).strip()
        if not ck:
            raise SchemaError("conflict_key must be non-empty when provided")
        pool = [e for e in pool if str(e.get("conflict_key") or "") == ck]
    if not pool:
        return {
            "winner": None,
            "candidates": [],
            "count": 0,
            "ok": False,
            "note": "No candidates for freshness_resolve",
        }
    ranked = sorted(pool, key=_freshness_key, reverse=True)
    winner = ranked[0]
    cand = []
    for e in ranked:
        m = extract_version_markers(e)
        cand.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "state": e.get("state"),
                "conflict_key": e.get("conflict_key"),
                "max_serial": m.get("max_serial"),
                "max_ts": m.get("max_ts"),
            }
        )
    return {
        "winner": {
            "id": winner.get("id"),
            "title": winner.get("title"),
            "state": winner.get("state"),
            "conflict_key": winner.get("conflict_key"),
            "markers": extract_version_markers(winner),
        },
        "candidates": cand,
        "count": len(cand),
        "ok": True,
        "note": "Deterministic max(serial|ts) — not LLM freshness judgment",
    }


def assemble_current(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Lexical candidate extract → group by conflict_key → resolve each group.
    Ungrouped entries compete as singleton groups keyed by id.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    scored: list[tuple[float, dict[str, Any]]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        if overlap <= 0:
            continue
        scored.append((overlap, e))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    top = [e for _, e in scored[: max(limit * 3, 5)]]

    groups: dict[str, list[dict[str, Any]]] = {}
    for e in top:
        ck = str(e.get("conflict_key") or "") or f"id:{e.get('id')}"
        groups.setdefault(ck, []).append(e)

    resolved: list[dict[str, Any]] = []
    for ck, members in groups.items():
        report = freshness_resolve(members)
        if report.get("winner"):
            w = dict(report["winner"])
            w["group"] = ck
            w["group_size"] = len(members)
            resolved.append(w)
    resolved.sort(
        key=lambda r: (
            -int((r.get("markers") or {}).get("max_serial") or 0),
            str((r.get("markers") or {}).get("max_ts") or ""),
            str(r.get("id")),
        ),
        reverse=True,
    )
    resolved = resolved[: max(1, int(limit))]
    return {
        "query": q,
        "resolved": resolved,
        "count": len(resolved),
        "groups": len(groups),
        "ok": True,
        "note": "assemble_current — candidate extract + deterministic freshness",
    }


def hop_freshness(
    hops: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    limit_per_hop: int = 3,
) -> dict[str, Any]:
    """
    Per-hop assemble_current (Self-Ask-shaped multi-hop freshness extension).
    """
    if not hops:
        raise SchemaError("hops is required")
    results: list[dict[str, Any]] = []
    for hop in hops:
        q = str(hop or "").strip()
        if not q:
            continue
        part = assemble_current(q, entries, limit=limit_per_hop)
        results.append(
            {
                "hop": q,
                "resolved": part.get("resolved") or [],
                "count": part.get("count") or 0,
            }
        )
    return {
        "hops": results,
        "hop_count": len(results),
        "ok": True,
        "note": "hop_freshness — per-hop deterministic assemble; not Self-Ask LLM",
    }
