"""Memory Worth (MW) — outcome co-occurrence governance primitive (stdlib)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

from stele_core.schema import SchemaError, normalize_usage


def memory_worth(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    MW = helpful / (helpful + harmful) when samples > 0.

    Associational — not causal (arXiv:2604.12007). Unknown when no outcomes.
    """
    usage = normalize_usage(entry.get("usage") if isinstance(entry, dict) else None)
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    n = helpful + harmful
    if n < 1:
        return {
            "id": entry.get("id"),
            "mw": None,
            "helpful": helpful,
            "harmful": harmful,
            "samples": 0,
            "known": False,
            "note": "Memory Worth unknown until outcome samples exist",
        }
    mw = helpful / n
    return {
        "id": entry.get("id"),
        "mw": round(mw, 6),
        "helpful": helpful,
        "harmful": harmful,
        "samples": n,
        "known": True,
        "note": "associational co-occurrence — not causal utility",
    }


def low_worth_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    threshold: float = 0.4,
    min_samples: int = 2,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Report promoted/contested entries below MW threshold with enough samples.

    Paper θL≈0.40 low-value floor — local proxy only.
    """
    if threshold < 0 or threshold > 1:
        raise SchemaError("threshold must be in [0, 1]")
    if min_samples < 1:
        raise SchemaError("min_samples must be >= 1")
    if limit < 1:
        raise SchemaError("limit must be >= 1")
    low: list[dict[str, Any]] = []
    for e in entries:
        if len(low) >= limit:
            break
        state = str(e.get("state") or "")
        if state not in {"promoted", "contested"}:
            continue
        report = memory_worth(e)
        if not report["known"] or int(report["samples"]) < min_samples:
            continue
        if float(report["mw"]) < threshold:
            low.append(
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "mw": report["mw"],
                    "samples": report["samples"],
                    "state": state,
                    "conflict_key": e.get("conflict_key"),
                }
            )
    low.sort(key=lambda x: (x["mw"], x["id"] or ""))
    return {
        "threshold": threshold,
        "min_samples": min_samples,
        "low": low,
        "count": len(low),
        "note": "Memory Worth low-value scan — suppress via min_worth Select",
    }


def passes_min_worth(
    entry: Mapping[str, Any],
    *,
    min_worth: float,
    min_samples: int = 1,
    unknown_ok: bool = True,
) -> bool:
    """True if entry should survive a min_worth Select filter."""
    if min_worth < 0 or min_worth > 1:
        raise SchemaError("min_worth must be in [0, 1]")
    report = memory_worth(entry)
    if not report["known"] or int(report["samples"]) < min_samples:
        return bool(unknown_ok)
    return float(report["mw"]) >= min_worth
