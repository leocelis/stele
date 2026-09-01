"""Lifecycle eligibility tiers (AMV-L-shaped) — deterministic, no LLM (C5)."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any

LIFECYCLE_TIERS = frozenset({"hot", "warm", "cold"})

_CONFLICT_KEY_RE_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:._/-"


def parse_conflict_key(raw: str) -> str:
    """Normalize a TEPA-shaped conflict key (stable precedent identity)."""
    key = str(raw or "").strip()
    if not key or len(key) > 200:
        raise ValueError("conflict_key must be a non-empty string ≤200 chars")
    if any(c not in _CONFLICT_KEY_RE_CHARS for c in key):
        raise ValueError(
            "conflict_key may only contain alphanumerics and : . _ / -"
        )
    return key


def _parse_ts(ts: str) -> datetime:
    text = str(ts).replace("Z", "+00:00")
    dt = datetime.fromisoformat(text)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def age_days(earlier: str, later: str) -> float:
    """Days from earlier → later (may be negative if later < earlier)."""
    return (_parse_ts(later) - _parse_ts(earlier)).total_seconds() / 86400.0


def lifecycle_tier(
    entry: dict[str, Any],
    *,
    now: str,
    hot_days: float = 7.0,
    warm_days: float = 30.0,
) -> str:
    """
    AMV-L-shaped retrieval eligibility tier from usage + freshness.

    HOT — pinned, strong net-helpful, or recently verified.
    WARM — some helpful signal or mid-horizon freshness.
    COLD — still on disk / maybe searchable, but low eligibility priority.
    """
    if hot_days <= 0 or warm_days < hot_days:
        raise ValueError("require hot_days > 0 and warm_days >= hot_days")
    usage = entry.get("usage") or {}
    if usage.get("pinned"):
        return "hot"
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    net = helpful - harmful
    if net >= 2:
        return "hot"
    last = str((entry.get("temporal") or {}).get("last_verified") or "")
    if last:
        days = age_days(last, now)
        if days <= hot_days and helpful >= 1:
            return "hot"
        if days <= warm_days:
            return "warm"
    if helpful > 0:
        return "warm"
    return "cold"


def lifecycle_inventory(
    entries: Iterable[dict[str, Any]],
    *,
    now: str,
    hot_days: float = 7.0,
    warm_days: float = 30.0,
    states: frozenset[str] | None = None,
) -> dict[str, Any]:
    """Count promoted-surface entries by lifecycle tier."""
    want = states or frozenset({"promoted", "contested"})
    by_tier: dict[str, list[str]] = {"hot": [], "warm": [], "cold": []}
    for e in entries:
        if e.get("state") not in want:
            continue
        tier = lifecycle_tier(e, now=now, hot_days=hot_days, warm_days=warm_days)
        by_tier[tier].append(e["id"])
    return {
        "now": now,
        "hot_days": hot_days,
        "warm_days": warm_days,
        "counts": {t: len(ids) for t, ids in by_tier.items()},
        "ids": by_tier,
        "note": "AMV-L-shaped eligibility proxies — not AMV-L latency claims",
    }
