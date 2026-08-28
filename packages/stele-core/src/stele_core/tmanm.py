"""TMA-NM-shaped origin-bound authority (stdlib; no LLM).

Write-time origin binding + non-malleable propagation + Sybil-resistant
corroboration-gated elevation. Content/lineage alone are malleable under
self-summarization, trusted-tool echo, and manufactured corroboration.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

ORIGINS = frozenset({"user", "trusted_tool", "agent", "untrusted_external"})
ACT_CLASS = {
    "untrusted_external": "none",
    "agent": "inform",
    "trusted_tool": "act",
    "user": "act",
}

_LAUNDER_MARKERS = {
    "self_summarization": (
        "in my own words",
        "i summarized",
        "paraphrased from",
        "rewrote as",
        "as i understand it",
    ),
    "trusted_tool_echo": (
        "tool returned",
        "according to the tool",
        "api response says",
        "echo from tool",
    ),
    "manufactured_corroboration": (
        "multiple sources agree",
        "everyone confirms",
        "consensus of pages",
        "several websites say",
    ),
}


def origin_bind(
    pending: Mapping[str, Any],
    *,
    channel_origin: str,
) -> dict[str, Any]:
    """
    M1: bind act_class from authenticated channel origin at write time.

    Never infer origin from content.
    """
    origin = str(channel_origin or "").strip().lower()
    if origin not in ORIGINS:
        raise SchemaError(
            f"channel_origin must be one of {sorted(ORIGINS)}"
        )
    act = ACT_CLASS[origin]
    return {
        "origin": origin,
        "act_class": act,
        "title": pending.get("title"),
        "actionable": act == "act",
        "ok": True,
        "note": "TMA-NM origin_bind — A1 channel oracle; not content-inferred",
    }


def propagate_origin(
    derived: Mapping[str, Any],
    sources: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    M2: derived item inherits max untrust of sources (non-malleable).

    Integrity order: untrusted_external ⊏ agent ⊏ trusted_tool|user
    """
    if not sources:
        raise SchemaError("sources is required")
    rank = {
        "untrusted_external": 0,
        "agent": 1,
        "trusted_tool": 2,
        "user": 2,
    }
    worst = "user"
    worst_r = 99
    for s in sources:
        o = str(s.get("origin") or s.get("channel_origin") or "").lower()
        if o not in rank:
            o = "untrusted_external"
        if rank[o] < worst_r:
            worst_r = rank[o]
            worst = o
    bound = origin_bind(derived, channel_origin=worst)
    return {
        **bound,
        "inherited_from": [s.get("id") for s in sources],
        "ok": True,
        "note": "TMA-NM propagate_origin — closes L-a/L-b; paraphrase cannot raise",
    }


def launder_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 40,
) -> dict[str, Any]:
    """
    Report laundering-channel proxies (self-summarization / tool-echo / corroboration).

    Heuristic markers only — not neural detectors.
    """
    hits: list[dict[str, Any]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested", "quarantined"}:
            continue
        text = f"{e.get('title') or ''}\n{e.get('body') or ''}".lower()
        channels: list[str] = []
        for ch, markers in _LAUNDER_MARKERS.items():
            if any(m in text for m in markers):
                channels.append(ch)
        # Manufactured corroboration: same conflict_key many untrusted copies
        # handled separately in elevate — here content markers only
        if channels:
            hits.append(
                {
                    "id": e.get("id"),
                    "title": e.get("title"),
                    "channels": channels,
                    "origin": (e.get("authority") or {}).get("origin")
                    or (e.get("provenance") or {}).get("source"),
                }
            )
            if len(hits) >= limit:
                break
    return {
        "suspects": hits,
        "count": len(hits),
        "ok": True,
        "note": "TMA-NM launder_scan — L-a/b/c marker proxies; not MEM-INV ASR",
    }


def act_authority_gate(
    value: str,
    drivers: Sequence[Mapping[str, Any]],
    *,
    trusted_principals: Sequence[str] | None = None,
    user_auth: bool = False,
    min_principals: int = 2,
) -> dict[str, Any]:
    """
    M3 act gate: allow iff no untrusted drivers, OR ≥k independent trusted
    principals license value, OR fresh user_auth.

    Repeated untrusted items do not count as corroboration (Sybil-resistant).
    """
    if min_principals < 1:
        raise SchemaError("min_principals must be >= 1")
    v = str(value or "").strip()
    if not v:
        raise SchemaError("value is required")

    untrusted: list[dict[str, Any]] = []
    for d in drivers:
        origin = str(
            d.get("origin")
            or (d.get("authority") or {}).get("origin")
            or ""
        ).lower()
        if not origin:
            # Infer from provenance.source prefix if present
            src = str((d.get("provenance") or {}).get("source") or "")
            if src.startswith("user:") or src.startswith("oracle:"):
                origin = "user"
            elif src.startswith("tool:"):
                origin = "trusted_tool"
            elif src.startswith("agent:"):
                origin = "agent"
            else:
                origin = "untrusted_external"
        act = ACT_CLASS.get(origin, "none")
        # Does this driver push the security-relevant value?
        body = f"{d.get('title') or ''}\n{d.get('body') or ''}".lower()
        pushes = v.lower() in body or any(
            t in set(tokenize(body)) for t in tokenize(v) if len(t) > 2
        )
        if pushes and act == "none":
            untrusted.append(
                {"id": d.get("id"), "origin": origin, "title": d.get("title")}
            )

    if not untrusted:
        return {
            "decision": "allow",
            "reason": "value_not_untrusted_derived",
            "value": v,
            "untrusted_drivers": [],
            "ok": True,
            "note": "TMA-NM act_authority_gate — Algorithm 1 allow path",
        }

    principals = sorted(
        {str(p).strip() for p in (trusted_principals or []) if str(p).strip()}
    )
    if len(principals) >= min_principals:
        return {
            "decision": "allow",
            "reason": "elevated_by_independent_principals",
            "value": v,
            "untrusted_drivers": untrusted,
            "principals": principals,
            "ok": True,
            "note": "TMA-NM elevate — Sybil-resistant; copies of same page ≠ independent",
        }
    if user_auth:
        return {
            "decision": "allow",
            "reason": "fresh_user_authorization",
            "value": v,
            "untrusted_drivers": untrusted,
            "ok": True,
            "note": "TMA-NM elevate — action-bound user auth (caller-consumed)",
        }
    return {
        "decision": "deny",
        "reason": "untrusted_uncorroborated",
        "value": v,
        "untrusted_drivers": untrusted,
        "principals": principals,
        "need_principals": min_principals,
        "ok": False,
        "note": "TMA-NM act_authority_gate — deny; content/lineage alone insufficient",
    }
