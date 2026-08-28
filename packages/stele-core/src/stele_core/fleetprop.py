"""Fleet / governed shared-memory propagation proxies (stdlib; no LLM).

Failure modes: unauthorized leakage, stale propagation, contradiction
persistence, provenance collapse (arXiv:2606.24535).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def fleet_scope_gate(
    entry: Mapping[str, Any],
    *,
    allowed_scopes: Sequence[str],
) -> dict[str, Any]:
    """Tenant/fleet scope gate for read or propagate."""
    allow = {str(s).strip() for s in allowed_scopes if s and str(s).strip()}
    if not allow:
        raise SchemaError("allowed_scopes is required")
    scope = str(entry.get("scope") or "")
    ok = scope in allow
    return {
        "id": entry.get("id"),
        "scope": scope,
        "allowed_scopes": sorted(allow),
        "ok": ok,
        "verdict": "allow" if ok else "deny",
        "note": "Fleet scope gate — explicit allowlist; no implicit universal",
    }


def propagate_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    source_scope: str,
    target_scopes: Sequence[str],
    query: str = "",
    limit: int = 10,
) -> dict[str, Any]:
    """
    Policy-governed propagation plan: which promoted entries may copy outward.

    Never auto-writes. Contested/quarantined never propagate.
    """
    src = str(source_scope or "").strip()
    targets = [str(t).strip() for t in target_scopes if t and str(t).strip()]
    if not src:
        raise SchemaError("source_scope is required")
    if not targets:
        raise SchemaError("target_scopes is required")
    if src in targets:
        raise SchemaError("target_scopes must not include source_scope")
    qtok = set(tokenize(query)) if query else set()
    candidates: list[dict[str, Any]] = []
    for e in entries:
        if str(e.get("scope") or "") != src:
            continue
        if e.get("state") != "promoted":
            continue
        if (e.get("usage") or {}).get("harmful", 0) and int(
            (e.get("usage") or {}).get("harmful") or 0
        ) > int((e.get("usage") or {}).get("helpful") or 0):
            continue
        blob = f"{e.get('title')}\n{e.get('body')}"
        etok = set(tokenize(blob))
        score = 1.0
        if qtok:
            score = len(qtok & etok) / max(len(qtok), 1)
            if score <= 0:
                continue
        candidates.append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "score": round(score, 4),
                "to_scopes": targets,
                "action": "copy_redacted",
            }
        )
    candidates.sort(key=lambda r: (-float(r["score"]), str(r["id"])))
    candidates = candidates[: max(1, int(limit))]
    return {
        "source_scope": src,
        "target_scopes": targets,
        "items": candidates,
        "count": len(candidates),
        "ok": True,
        "note": "Fleet propagate_plan — report-only; never silent merge",
    }


def stale_propagation_scan(
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Flag same conflict_key with an older tip still promoted alongside a newer tip.
    """
    by_ck: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        ck = str(e.get("conflict_key") or "")
        if not ck or e.get("state") not in {"promoted", "contested"}:
            continue
        by_ck.setdefault(ck, []).append(e)
    suspects: list[dict[str, Any]] = []
    from stele_core.freshness import extract_version_markers, freshness_resolve

    for ck, members in by_ck.items():
        if len(members) < 2:
            continue
        report = freshness_resolve(members, conflict_key=ck)
        winner_id = (report.get("winner") or {}).get("id")
        for e in members:
            if e.get("id") == winner_id:
                continue
            if e.get("state") != "promoted":
                continue
            m = extract_version_markers(e)
            suspects.append(
                {
                    "id": e.get("id"),
                    "conflict_key": ck,
                    "title": e.get("title"),
                    "winner_id": winner_id,
                    "max_ts": m.get("max_ts"),
                    "reason": "stale_promoted_beside_fresher_tip",
                }
            )
    suspects.sort(key=lambda r: (str(r.get("conflict_key")), str(r.get("id"))))
    suspects = suspects[: max(1, int(limit))]
    return {
        "suspects": suspects,
        "count": len(suspects),
        "ok": True,
        "note": "Fleet stale_propagation_scan — contradiction persistence detector",
    }
