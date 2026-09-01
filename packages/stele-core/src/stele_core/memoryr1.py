"""Memory-R1-shaped memory manager ops (stdlib; no LLM / no RL).

Shaped by Memory-R1 (arXiv:2508.19828): ADD / UPDATE / DELETE / NOOP
decisions against an external store. Proxies only — not Memory-R1 scores.
Never trains a manager; report-only plans.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

OPS = frozenset({"ADD", "UPDATE", "DELETE", "NOOP"})
_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def classify_memory_op(
    *,
    candidate: str,
    existing_bodies: Sequence[str],
) -> dict[str, Any]:
    """
    Classify ADD/UPDATE/DELETE/NOOP for a candidate fact vs existing store text.
    Heuristic: high overlap → NOOP; correction cues → UPDATE; revoke cues → DELETE;
    else ADD.
    """
    if not isinstance(candidate, str) or not candidate.strip():
        raise SchemaError("candidate string required")
    low = candidate.lower()
    ctok = _tokens(candidate)
    best_overlap = 0.0
    best_body = ""
    for body in existing_bodies:
        if not isinstance(body, str):
            continue
        btok = _tokens(body)
        if not ctok or not btok:
            continue
        ov = len(ctok & btok) / max(1, len(ctok | btok))
        if ov > best_overlap:
            best_overlap = ov
            best_body = body
    if any(w in low for w in ("revoke", "delete this", "was wrong", "false —", "harmful")):
        op = "DELETE"
    elif any(w in low for w in ("instead", "correction:", "now is", "updated:", "no longer")):
        op = "UPDATE"
    elif best_overlap >= 0.7:
        op = "NOOP"
    elif best_overlap >= 0.35 and any(
        w in low for w in ("but", "except", "actually", "rather")
    ):
        op = "UPDATE"
    else:
        op = "ADD"
    return {
        "op": op,
        "best_overlap": round(best_overlap, 4),
        "matched_preview": best_body[:100] if best_body else None,
        "ok": op in OPS,
        "note": "memoryr1 classify_memory_op",
    }


def noop_gate(
    *,
    candidate: str,
    existing_bodies: Sequence[str],
    min_overlap: float = 0.7,
) -> dict[str, Any]:
    """Gate: NOOP when candidate is redundant with store."""
    c = classify_memory_op(candidate=candidate, existing_bodies=existing_bodies)
    noop = c["op"] == "NOOP" or float(c["best_overlap"]) >= min_overlap
    return {
        "noop": noop,
        "op": "NOOP" if noop else c["op"],
        "best_overlap": c["best_overlap"],
        "min_overlap": min_overlap,
        "ok": True,
        "note": "memoryr1 noop_gate",
    }


def memory_op_plan(
    *,
    candidate: str,
    existing_entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Build a report-only ADD/UPDATE/DELETE/NOOP plan for one candidate."""
    bodies = [
        f"{e.get('title') or ''}\n{e.get('body') or ''}"
        for e in existing_entries
        if isinstance(e, Mapping)
    ]
    decision = classify_memory_op(candidate=candidate, existing_bodies=bodies)
    target_id = None
    if decision["op"] in {"UPDATE", "DELETE"} and decision.get("matched_preview"):
        preview = str(decision["matched_preview"])
        for e in existing_entries:
            if not isinstance(e, Mapping):
                continue
            blob = f"{e.get('title') or ''}\n{e.get('body') or ''}"
            if preview[:40] and preview[:40] in blob:
                target_id = e.get("id")
                break
    return {
        "op": decision["op"],
        "candidate_preview": candidate.strip()[:120],
        "target_id": target_id,
        "best_overlap": decision["best_overlap"],
        "apply": False,
        "ok": True,
        "note": "memoryr1 memory_op_plan — no auto-write",
    }


def conflict_update_plan(
    *,
    old_text: str,
    new_text: str,
) -> dict[str, Any]:
    """UPDATE plan when new text conflicts with old (report-only)."""
    if not isinstance(old_text, str) or not isinstance(new_text, str):
        raise SchemaError("old_text and new_text required")
    ot, nt = _tokens(old_text), _tokens(new_text)
    shared = ot & nt
    novel = nt - ot
    conflict = len(novel) >= 2 and len(shared) >= 1
    return {
        "op": "UPDATE" if conflict else "NOOP",
        "shared_tokens": sorted(shared)[:12],
        "novel_tokens": sorted(novel)[:12],
        "conflict": conflict,
        "apply": False,
        "ok": True,
        "note": "memoryr1 conflict_update_plan",
    }


def delete_stale_plan(
    entries: Sequence[Mapping[str, Any]],
    *,
    revoke_markers: Sequence[str] | None = None,
) -> dict[str, Any]:
    """DELETE plan for entries whose body contains revoke/stale markers."""
    markers = [m.lower() for m in (revoke_markers or ("revoked", "obsolete", "do not use", "stale:"))]
    victims: list[dict[str, Any]] = []
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        blob = f"{e.get('title') or ''}\n{e.get('body') or ''}".lower()
        hit = next((m for m in markers if m in blob), None)
        if hit:
            victims.append({"id": e.get("id"), "marker": hit, "op": "DELETE"})
    return {
        "delete_count": len(victims),
        "targets": victims,
        "apply": False,
        "ok": True,
        "note": "memoryr1 delete_stale_plan",
    }
