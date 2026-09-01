"""xMemory-shaped theme hierarchy + top-down expand (stdlib; no LLM).

Decouple → aggregate: group entries into themes; split overcrowded / merge
tiny themes; retrieve top-down and expand to leaf text only under budget need.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def _centroid_tokens(members: Sequence[Mapping[str, Any]]) -> set[str]:
    toks: set[str] = set()
    for m in members:
        toks |= set(tokenize(f"{m.get('title') or ''}\n{m.get('body') or ''}"))
    return toks


def theme_attach(
    entry: Mapping[str, Any],
    themes: Sequence[Mapping[str, Any]],
    *,
    min_overlap: float = 0.2,
) -> dict[str, Any]:
    """
    Attach entry to best theme by Jaccard vs centroid, else create new theme.
    """
    et = set(tokenize(f"{entry.get('title') or ''}\n{entry.get('body') or ''}"))
    if not et:
        raise SchemaError("entry must be tokenizable")
    best_id = None
    best = -1.0
    for th in themes:
        members = th.get("members") or []
        # members may be ids or dicts — centroid from labels if present
        label_toks = set(tokenize(str(th.get("label") or "")))
        cent = label_toks
        for m in members:
            if isinstance(m, Mapping):
                cent |= set(tokenize(f"{m.get('title')}\n{m.get('body')}"))
            else:
                cent |= set(tokenize(str(m)))
        if not cent:
            continue
        sim = len(et & cent) / len(et | cent)
        if sim > best:
            best = sim
            best_id = th.get("id")
    if best_id is None or best < min_overlap:
        return {
            "decision": "create_theme",
            "theme_id": None,
            "similarity": round(max(0.0, best), 4),
            "suggested_label": str(entry.get("title") or "theme")[:80],
            "ok": True,
            "note": "xMemory theme_attach — new theme",
        }
    return {
        "decision": "attach",
        "theme_id": best_id,
        "similarity": round(best, 4),
        "ok": True,
        "note": "xMemory theme_attach — attach to existing",
    }


def split_merge_plan(
    themes: Sequence[Mapping[str, Any]],
    *,
    max_size: int = 6,
    min_size: int = 2,
) -> dict[str, Any]:
    """
    Report-only split (overcrowded) / merge (tiny) plan.

    Split: overcrowded theme → suggest bipartition by title token clusters.
    Merge: tiny themes → nearest neighbor by label Jaccard.
    """
    if max_size < 1:
        raise SchemaError("max_size must be >= 1")
    if min_size < 1:
        raise SchemaError("min_size must be >= 1")
    actions: list[dict[str, Any]] = []
    # Index for merge
    labeled = []
    for th in themes:
        members = th.get("members") or th.get("member_ids") or []
        n = len(members)
        labeled.append(
            {
                "id": th.get("id"),
                "label": th.get("label"),
                "n": n,
                "toks": set(tokenize(str(th.get("label") or ""))),
            }
        )

    for th in themes:
        members = list(th.get("members") or th.get("member_ids") or [])
        n = len(members)
        tid = th.get("id")
        if n > max_size:
            # Simple bipartition: alternate by sorted id/title
            keys = sorted(str(m if not isinstance(m, Mapping) else m.get("id") or m.get("title")) for m in members)
            mid = len(keys) // 2
            actions.append(
                {
                    "action": "split",
                    "theme_id": tid,
                    "reason": "overcrowded",
                    "parts": [keys[:mid], keys[mid:]],
                }
            )
        elif 0 < n < min_size:
            # Find nearest other theme
            me = next((x for x in labeled if x["id"] == tid), None)
            best = None
            best_sim = -1.0
            for other in labeled:
                if other["id"] == tid or other["n"] == 0:
                    continue
                if not me or not me["toks"] or not other["toks"]:
                    continue
                sim = len(me["toks"] & other["toks"]) / len(me["toks"] | other["toks"])
                if sim > best_sim:
                    best_sim = sim
                    best = other["id"]
            actions.append(
                {
                    "action": "merge",
                    "theme_id": tid,
                    "into": best,
                    "similarity": round(max(0.0, best_sim), 4),
                    "reason": "undersized",
                }
            )
    return {
        "actions": actions,
        "count": len(actions),
        "max_size": max_size,
        "min_size": min_size,
        "ok": True,
        "note": "xMemory split_merge_plan — sparsity/faithfulness proxy; report-only",
    }


def top_down_pack(
    query: str,
    themes: Sequence[Mapping[str, Any]],
    entries: Sequence[Mapping[str, Any]],
    *,
    budget: int = 200,
    expand_threshold: float = 0.35,
) -> dict[str, Any]:
    """
    Top-down pack: pick diverse themes, expand to leaves only if overlap weak.

    Uncertainty proxy: if theme-level overlap < expand_threshold, pull leaf text.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    by_id = {str(e.get("id")): e for e in entries}

    ranked: list[dict[str, Any]] = []
    for th in themes:
        label = str(th.get("label") or "")
        stok = set(tokenize(label))
        # Also fold member titles if dicts
        for m in th.get("members") or []:
            if isinstance(m, Mapping):
                stok |= set(tokenize(f"{m.get('title')}"))
        overlap = len(qtok & stok) / max(len(qtok), 1) if qtok else 0.0
        if overlap <= 0:
            continue
        ranked.append(
            {
                "theme_id": th.get("id"),
                "label": label,
                "score": round(overlap, 4),
                "member_ids": [
                    str(m.get("id") if isinstance(m, Mapping) else m)
                    for m in (th.get("members") or th.get("member_ids") or [])
                ],
            }
        )
    ranked.sort(key=lambda x: (-x["score"], str(x["theme_id"])))

    blocks: list[dict[str, Any]] = []
    used = 0
    for th in ranked:
        # Theme-level block first (cheap)
        text = f"THEME: {th['label']}"
        cost = max(1, len(text.split()))
        if used + cost > budget:
            break
        blocks.append(
            {
                "level": "theme",
                "theme_id": th["theme_id"],
                "text": text,
                "score": th["score"],
            }
        )
        used += cost
        if th["score"] >= expand_threshold:
            continue  # enough certainty at theme level
        # Expand leaves
        for mid in th.get("member_ids") or []:
            e = by_id.get(str(mid))
            if e is None:
                continue
            leaf = f"{e.get('title') or ''}. {e.get('body') or ''}".strip()
            lcost = max(1, len(leaf.split()))
            if used + lcost > budget:
                break
            blocks.append(
                {
                    "level": "leaf",
                    "id": e.get("id"),
                    "theme_id": th["theme_id"],
                    "text": leaf,
                }
            )
            used += lcost
    return {
        "query": q,
        "blocks": blocks,
        "used": used,
        "budget": budget,
        "theme_hits": len(ranked),
        "ok": True,
        "note": "xMemory top_down_pack — expand only when theme uncertainty high",
    }


def build_themes_from_entries(
    entries: Sequence[Mapping[str, Any]],
    *,
    scope: str | None = None,
) -> dict[str, Any]:
    """Bootstrap themes by conflict_key or scope|layer fallback."""
    groups: dict[str, list[dict[str, Any]]] = {}
    for e in entries:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        if scope and e.get("scope") != scope:
            continue
        key = str(e.get("conflict_key") or "").strip()
        if not key:
            key = f"{e.get('scope')}|{e.get('layer')}"
        groups.setdefault(key, []).append(
            {
                "id": e.get("id"),
                "title": e.get("title"),
                "body": e.get("body"),
            }
        )
    themes = []
    for i, (key, members) in enumerate(sorted(groups.items())):
        themes.append(
            {
                "id": f"theme:{i}:{key}",
                "label": key,
                "members": members,
                "member_ids": [m["id"] for m in members],
            }
        )
    return {
        "themes": themes,
        "count": len(themes),
        "ok": True,
        "note": "xMemory build_themes_from_entries — conflict_key bootstrap",
    }
