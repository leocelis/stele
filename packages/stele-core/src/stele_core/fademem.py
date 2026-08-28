"""FadeMem-shaped dual-layer decay + fusion plans (stdlib; no LLM).

Differential decay across short-term (SML) vs long-term (LML) layers.
Fade scan is report-only — never auto-deletes. Fusion is a deterministic
merge plan (token overlap), not LLM conflict resolution.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.lifecycle import age_days, lifecycle_tier
from stele_core.schema import SchemaError

FADE_LAYERS = frozenset({"sml", "lml"})


def assign_fade_layer(
    entry: Mapping[str, Any],
    *,
    now: str,
    hot_days: float = 7.0,
    warm_days: float = 30.0,
) -> str:
    """
    Map entry → FadeMem layer proxy.

    SML — hot lifecycle (fast decay). LML — warm/cold or pinned (slow decay).
    """
    usage = entry.get("usage") or {}
    if usage.get("pinned"):
        return "lml"
    tier = lifecycle_tier(
        dict(entry), now=now, hot_days=hot_days, warm_days=warm_days
    )
    return "sml" if tier == "hot" else "lml"


def weibull_relevance(
    entry: Mapping[str, Any],
    *,
    now: str,
    eta_days: float = 30.0,
    kappa: float = 1.0,
) -> float:
    """
    SSGM/FadeMem Weibull relevance w(Δτ) = exp(-(Δτ/η)^κ) in (0, 1].

    Δτ from last_verified (or written_at). Reinforced by helpful/pin.
    """
    if eta_days <= 0:
        raise SchemaError("eta_days must be > 0")
    if kappa <= 0:
        raise SchemaError("kappa must be > 0")
    last = str((entry.get("temporal") or {}).get("last_verified") or "")
    if not last:
        last = str((entry.get("provenance") or {}).get("written_at") or "")
    if not last:
        base = 0.05
    else:
        age = max(0.0, age_days(last, now))
        base = math.exp(-((age / eta_days) ** kappa))
    usage = entry.get("usage") or {}
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    boost = min(0.25, 0.04 * max(0, helpful - harmful))
    if usage.get("pinned"):
        boost = max(boost, 0.2)
    return round(min(1.0, base + boost), 6)


def fade_strength(
    entry: Mapping[str, Any],
    *,
    now: str,
    eta_sml: float = 14.0,
    eta_lml: float = 45.0,
    kappa_sml: float = 1.2,
    kappa_lml: float = 0.8,
) -> dict[str, Any]:
    """
    Dual-layer fade strength (FadeMem-shaped).

    SML uses faster Weibull (higher κ, smaller η); LML slower.
    """
    layer = assign_fade_layer(entry, now=now)
    if layer == "sml":
        strength = weibull_relevance(
            entry, now=now, eta_days=eta_sml, kappa=kappa_sml
        )
        eta, kappa = eta_sml, kappa_sml
    else:
        strength = weibull_relevance(
            entry, now=now, eta_days=eta_lml, kappa=kappa_lml
        )
        eta, kappa = eta_lml, kappa_lml
    return {
        "id": entry.get("id"),
        "fade_layer": layer,
        "strength": strength,
        "eta_days": eta,
        "kappa": kappa,
        "note": "FadeMem dual-layer strength — report only",
    }


def fade_scan(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    threshold: float = 0.15,
    limit: int = 50,
    eta_sml: float = 14.0,
    eta_lml: float = 45.0,
) -> dict[str, Any]:
    """
    Candidates below fade threshold (archive/suppress queue — no auto-delete).
    """
    if threshold < 0 or threshold > 1:
        raise SchemaError("threshold must be in [0, 1]")
    faded: list[dict[str, Any]] = []
    kept = 0
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        report = fade_strength(
            e, now=now, eta_sml=eta_sml, eta_lml=eta_lml
        )
        if report["strength"] < threshold:
            faded.append(
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "state": e.get("state"),
                    "fade_layer": report["fade_layer"],
                    "strength": report["strength"],
                }
            )
        else:
            kept += 1
    faded.sort(key=lambda r: (float(r["strength"]), str(r["id"])))
    faded = faded[: max(1, int(limit))]
    return {
        "faded": faded,
        "fade_count": len(faded),
        "kept_count": kept,
        "threshold": threshold,
        "ok": True,
        "note": "FadeMem fade scan — never auto-deletes (report only)",
    }


def fusion_candidates(
    entries: Iterable[Mapping[str, Any]],
    *,
    min_overlap: float = 0.45,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Deterministic merge-candidate pairs (FadeMem fusion proxy without LLM).

    Same conflict_key or high title/body token overlap → fuse plan.
    """
    if not (0 < min_overlap <= 1):
        raise SchemaError("min_overlap must be in (0, 1]")
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested", "quarantined"}
    ]
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(pool):
        a_tok = set(tokenize(f"{a.get('title')}\n{a.get('body')}"))
        a_key = str(a.get("conflict_key") or "")
        for b in pool[i + 1 :]:
            if a.get("id") == b.get("id"):
                continue
            reason = None
            score = 0.0
            b_key = str(b.get("conflict_key") or "")
            if a_key and a_key == b_key:
                reason = "same_conflict_key"
                score = 1.0
            else:
                b_tok = set(tokenize(f"{b.get('title')}\n{b.get('body')}"))
                if a_tok and b_tok:
                    score = len(a_tok & b_tok) / max(len(a_tok | b_tok), 1)
                    if score >= min_overlap:
                        reason = "token_overlap"
            if not reason:
                continue
            pairs.append(
                {
                    "a": a.get("id"),
                    "b": b.get("id"),
                    "score": round(score, 4),
                    "reason": reason,
                    "action": "fuse_or_supersede",
                    "titles": [a.get("title"), b.get("title")],
                }
            )
    pairs.sort(key=lambda r: (-float(r["score"]), str(r["a"]), str(r["b"])))
    pairs = pairs[: max(1, int(limit))]
    return {
        "pairs": pairs,
        "count": len(pairs),
        "min_overlap": min_overlap,
        "note": "FadeMem fusion candidates — deterministic plan, not LLM merge",
    }
