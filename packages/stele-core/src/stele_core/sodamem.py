"""SodaMem-shaped density fusion + cited evidence packs (stdlib; no LLM).

Multi-tunnel masses accumulate on evidence IDs; a reader pack requires citations.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

# Tunnel mass weights (SodaMem-shaped defaults)
_WEIGHTS = {
    ("strong", "direct"): 0.4,
    ("weak", "direct"): 0.2,
    ("strong", "derived"): 0.1,
    ("weak", "derived"): 0.05,
}


def density_fuse(
    tunnels: Sequence[Mapping[str, Any]],
    *,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Fuse multi-tunnel hits by accumulating mass per evidence id.

    Each tunnel item: {id, tunnel?, strength?: strong|weak, kind?: direct|derived, score?}
    """
    if not tunnels:
        raise SchemaError("tunnels is required")
    mass: dict[str, float] = {}
    meta: dict[str, dict[str, Any]] = {}
    for hit in tunnels:
        eid = str(hit.get("id") or "").strip()
        if not eid:
            continue
        strength = str(hit.get("strength") or "strong").lower()
        if strength not in {"strong", "weak"}:
            strength = "strong"
        kind = str(hit.get("kind") or "direct").lower()
        if kind not in {"direct", "derived"}:
            kind = "direct"
        w = _WEIGHTS[(strength, kind)]
        # Optional score scales mass lightly
        score = float(hit.get("score") or 1.0)
        mass[eid] = mass.get(eid, 0.0) + w * max(0.0, min(1.0, score))
        row = meta.setdefault(
            eid,
            {"id": eid, "title": hit.get("title"), "tunnels": [], "mass": 0.0},
        )
        row["tunnels"].append(
            {
                "tunnel": hit.get("tunnel") or "unknown",
                "strength": strength,
                "kind": kind,
            }
        )
        if hit.get("title") and not row.get("title"):
            row["title"] = hit.get("title")
    ranked = sorted(mass.items(), key=lambda x: (-x[1], x[0]))
    fused = []
    for eid, m in ranked[: max(1, int(limit))]:
        row = dict(meta[eid])
        row["mass"] = round(m, 4)
        fused.append(row)
    return {
        "fused": fused,
        "count": len(fused),
        "ok": True,
        "note": "SodaMem density_fuse — connection-density mass; not dense embeds",
    }


def evidence_plan(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    limit: int = 8,
) -> dict[str, Any]:
    """
    Planner step: gather evidence IDs via lexical + link-derived tunnels, fuse.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    by_id = {str(e.get("id")): e for e in entries}
    tunnels: list[dict[str, Any]] = []
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        eid = str(e.get("id") or "")
        etok = set(tokenize(f"{e.get('title')}\n{e.get('body')}"))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        if overlap <= 0:
            continue
        strength = "strong" if overlap >= 0.35 else "weak"
        tunnels.append(
            {
                "id": eid,
                "title": e.get("title"),
                "tunnel": "lexical",
                "strength": strength,
                "kind": "direct",
                "score": overlap,
            }
        )
        # Derived via LINKs
        for link in e.get("links") or []:
            if not isinstance(link, Mapping):
                continue
            if str(link.get("kind") or "") != "entry":
                continue
            ref = str(link.get("ref") or "")
            other = by_id.get(ref)
            if other is None or other.get("state") not in {"promoted", "contested"}:
                continue
            tunnels.append(
                {
                    "id": ref,
                    "title": other.get("title"),
                    "tunnel": "link",
                    "strength": "weak",
                    "kind": "derived",
                    "score": overlap,
                }
            )
    fused = density_fuse(tunnels, limit=limit)
    return {
        "query": q,
        "tunnel_hits": len(tunnels),
        "evidence": fused.get("fused") or [],
        "count": fused.get("count") or 0,
        "ok": True,
        "note": "SodaMem evidence_plan — planner gathers IDs before reader prose",
    }


def cited_pack(
    query: str,
    evidence_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    budget: int = 400,
) -> dict[str, Any]:
    """
    Reader pack: each block carries a mandatory citation id.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    by_id = {str(e.get("id")): e for e in entries}
    blocks: list[dict[str, Any]] = []
    used = 0
    missing: list[str] = []
    for eid in evidence_ids:
        e = by_id.get(str(eid))
        if e is None:
            missing.append(str(eid))
            continue
        text = f"{e.get('title') or ''}. {e.get('body') or ''}".strip()
        cost = max(1, len(text.split()))
        if used + cost > budget:
            break
        blocks.append(
            {
                "citation": str(eid),
                "title": e.get("title"),
                "text": text,
                "state": e.get("state"),
            }
        )
        used += cost
    # Fail closed if any block lacks citation (structural invariant)
    uncited = [b for b in blocks if not b.get("citation")]
    return {
        "query": q,
        "blocks": blocks,
        "count": len(blocks),
        "used": used,
        "budget": budget,
        "missing": missing,
        "all_cited": len(uncited) == 0 and len(blocks) > 0,
        "ok": len(uncited) == 0 and (len(blocks) > 0 or not evidence_ids),
        "note": "SodaMem cited_pack — mandatory citations; reader ≠ planner",
    }
