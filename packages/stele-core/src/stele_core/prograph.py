"""ProGraph-shaped profiles + compression residuals (stdlib; no LLM).

Profile expansion via entity-substring match in bodies.
Residuals = dates, quantities, CapWords / code-like tokens preserved from body.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

_DATE_RE = re.compile(
    r"\b(?:\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}Z?)\b"
)
_QTY_RE = re.compile(
    r"\b\d+(?:\.\d+)?(?:%|ms|s|kb|mb|gb|x)?\b", re.IGNORECASE
)
_NAME_RE = re.compile(r"\b[A-Z][a-zA-Z0-9_]{2,}\b")
_CODE_RE = re.compile(r"\b[a-z]+(?:_[a-z0-9]+)+\b")


def extract_residuals(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    Compression residuals: precision-critical tokens a summary would drop.
    """
    blob = f"{entry.get('title') or ''}\n{entry.get('body') or ''}"
    dates = sorted(set(_DATE_RE.findall(blob)))
    qtys = sorted(set(_QTY_RE.findall(blob)))
    names = sorted(set(_NAME_RE.findall(blob)))
    codes = sorted(set(_CODE_RE.findall(blob)))
    # Cap names that are also common English words — keep short list
    residuals = []
    for kind, vals in (
        ("date", dates),
        ("quantity", qtys),
        ("name", names[:12]),
        ("code", codes[:12]),
    ):
        for v in vals:
            residuals.append({"kind": kind, "value": v})
    return {
        "id": entry.get("id"),
        "residuals": residuals,
        "count": len(residuals),
        "note": "ProGraph compression residuals — regex proxy, not LLM co-extract",
    }


def register_entities(
    entries: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Build entity registry from CapWords / conflict_key tails / title heads.
    """
    entities: dict[str, dict[str, Any]] = {}
    for e in entries:
        if e.get("state") not in {"promoted", "contested", "quarantined"}:
            continue
        eid = str(e.get("id") or "")
        cands: set[str] = set()
        title = str(e.get("title") or "")
        if title:
            # first two significant tokens as entity alias
            toks = [t for t in tokenize(title) if len(t) > 2][:3]
            if toks:
                cands.add(" ".join(toks))
                cands.add(toks[0])
        ck = str(e.get("conflict_key") or "")
        if ck and ":" in ck:
            cands.add(ck.split(":")[-1])
        for m in _NAME_RE.findall(f"{title}\n{e.get('body') or ''}"):
            cands.add(m.lower())
        for name in cands:
            key = name.lower().strip()
            if len(key) < 3:
                continue
            row = entities.setdefault(
                key, {"name": key, "entry_ids": [], "aliases": [key]}
            )
            if eid and eid not in row["entry_ids"]:
                row["entry_ids"].append(eid)
    return {
        "entities": list(entities.values()),
        "count": len(entities),
        "ok": True,
        "note": "ProGraph entity registry — deterministic aliases",
    }


def profile_expand(
    query: str,
    entries: Sequence[Mapping[str, Any]],
    *,
    expand_threshold: float = 0.2,
    seed_limit: int = 5,
    expand_limit: int = 10,
) -> dict[str, Any]:
    """
    Seed by lexical overlap, expand via entity substrings in neighbor bodies.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    if not (0 <= expand_threshold <= 1):
        raise SchemaError("expand_threshold must be in [0, 1]")
    qtok = set(tokenize(q))
    q_l = q.lower()
    pool = [
        e
        for e in entries
        if e.get("state") in {"promoted", "contested"}
    ]
    scored: list[tuple[float, dict[str, Any]]] = []
    for e in pool:
        blob = f"{e.get('title')}\n{e.get('body')}"
        etok = set(tokenize(blob))
        overlap = len(qtok & etok) / max(len(qtok), 1) if qtok else 0.0
        name_boost = 0.15 if any(
            a in blob.lower() for a in qtok if len(a) > 3
        ) else 0.0
        score = overlap + name_boost
        if score > 0:
            scored.append((score, e))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("id"))))
    seeds = [e for _, e in scored[: max(1, int(seed_limit))]]
    seed_ids = {str(e.get("id")) for e in seeds}

    registry = register_entities(pool)
    # map entity name → entry ids
    ent_map = {
        str(ent["name"]): list(ent.get("entry_ids") or [])
        for ent in registry.get("entities") or []
    }

    expanded: list[dict[str, Any]] = []
    seen = set(seed_ids)
    for seed in seeds:
        blob = f"{seed.get('title')}\n{seed.get('body')}".lower()
        for name, ids in ent_map.items():
            if len(name) < 3 or name not in blob:
                continue
            for oid in ids:
                if oid in seen:
                    continue
                # relevance gate: neighbor must share some query tokens
                other = next((e for e in pool if str(e.get("id")) == oid), None)
                if other is None:
                    continue
                otok = set(tokenize(f"{other.get('title')}\n{other.get('body')}"))
                gate = len(qtok & otok) / max(len(qtok), 1) if qtok else 0.0
                if gate < expand_threshold and name not in q_l:
                    continue
                seen.add(oid)
                expanded.append(
                    {
                        "id": oid,
                        "via_entity": name,
                        "from_seed": seed.get("id"),
                        "gate": round(gate, 4),
                        "title": other.get("title"),
                    }
                )
                if len(expanded) >= expand_limit:
                    break
            if len(expanded) >= expand_limit:
                break
        if len(expanded) >= expand_limit:
            break

    return {
        "query": q,
        "seeds": [
            {"id": e.get("id"), "title": e.get("title")} for e in seeds
        ],
        "expanded": expanded,
        "seed_count": len(seeds),
        "expand_count": len(expanded),
        "ok": True,
        "note": "ProGraph profile expansion — substring entity traversal proxy",
    }


def residual_augment(
    query: str,
    entry_ids: Sequence[str],
    entries: Sequence[Mapping[str, Any]],
    *,
    limit_per_entry: int = 5,
) -> dict[str, Any]:
    """Attach query-relevant residuals for selected entries."""
    q = str(query or "").strip().lower()
    qtok = set(tokenize(q))
    by_id = {str(e.get("id")): e for e in entries}
    packs: list[dict[str, Any]] = []
    for eid in entry_ids:
        e = by_id.get(str(eid))
        if e is None:
            continue
        report = extract_residuals(e)
        scored = []
        for r in report.get("residuals") or []:
            val = str(r.get("value") or "")
            hit = val.lower() in q or any(
                t in val.lower() for t in qtok if len(t) > 2
            )
            scored.append((1 if hit else 0, r))
        scored.sort(key=lambda x: (-x[0], str(x[1].get("value"))))
        top = [r for _, r in scored[: max(1, int(limit_per_entry))]]
        packs.append(
            {
                "id": eid,
                "title": e.get("title"),
                "residuals": top,
                "count": len(top),
            }
        )
    return {
        "query": query,
        "packs": packs,
        "count": len(packs),
        "ok": True,
        "note": "ProGraph residual-augmented context — Verified Facts proxy",
    }
