"""SF-AMS-shaped composite importance scoring (stdlib; no LLM).

CIS blends Weibull relevance, Memory Worth, retention, pin, and usage.
Tiers: core / important / secondary / irrelevant — proxies only.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from stele_core.activation import retention_score
from stele_core.fademem import weibull_relevance
from stele_core.schema import SchemaError
from stele_core.worth import memory_worth

IMPORTANCE_TIERS = frozenset({"core", "important", "secondary", "irrelevant"})


def composite_importance(
    entry: Mapping[str, Any],
    *,
    now: str,
    eta_days: float = 30.0,
    kappa: float = 1.0,
    half_life_days: float = 30.0,
) -> dict[str, Any]:
    """Composite Importance Score in [0, 1] with tier label."""
    wb = weibull_relevance(entry, now=now, eta_days=eta_days, kappa=kappa)
    ret = retention_score(entry, now=now, half_life_days=half_life_days)
    mw = memory_worth(entry)
    usage = entry.get("usage") or {}
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    pin = 1.0 if usage.get("pinned") else 0.0
    mw_term = float(mw["mw"]) if mw.get("known") else 0.5
    use_term = min(1.0, helpful / 5.0)
    harm_pen = min(0.3, 0.05 * harmful)
    cis = (
        0.30 * wb
        + 0.25 * mw_term
        + 0.20 * ret
        + 0.15 * pin
        + 0.10 * use_term
        - harm_pen
    )
    cis = round(max(0.0, min(1.0, cis)), 6)
    if cis >= 0.75:
        tier = "core"
    elif cis >= 0.50:
        tier = "important"
    elif cis >= 0.25:
        tier = "secondary"
    else:
        tier = "irrelevant"
    return {
        "id": entry.get("id"),
        "cis": cis,
        "tier": tier,
        "components": {
            "weibull": wb,
            "mw": mw.get("mw"),
            "retention": ret,
            "pin": pin,
            "use": round(use_term, 4),
            "harm_penalty": round(harm_pen, 4),
        },
        "note": "SF-AMS CIS proxy — not paper scores",
    }


def cis_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    tiers: Iterable[str] | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Rank promoted/contested entries by CIS."""
    allow = None
    if tiers is not None:
        allow = {str(t).strip().lower() for t in tiers if t}
        bad = allow - IMPORTANCE_TIERS
        if bad:
            raise SchemaError(f"tiers must be subset of {sorted(IMPORTANCE_TIERS)}")
    rows: list[dict[str, Any]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        report = composite_importance(entry=e, now=now)
        if allow and report["tier"] not in allow:
            continue
        rows.append(
            {
                "id": report["id"],
                "title": e.get("title"),
                "cis": report["cis"],
                "tier": report["tier"],
                "state": e.get("state"),
            }
        )
    rows.sort(key=lambda r: (-float(r["cis"]), str(r["id"])))
    rows = rows[: max(1, int(limit))]
    return {
        "entries": rows,
        "count": len(rows),
        "ok": True,
        "note": "SF-AMS CIS scan — local proxy",
    }
