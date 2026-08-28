"""EverMemOS-shaped MemCell / MemScene lifecycle (stdlib; no LLM).

Shaped by EverMemOS (ACL 2026 long): Episodic Trace Formation →
Semantic Consolidation → Reconstructive Recollection with foresight
filtering and necessity/sufficiency. Proxies only — not LoCoMo scores.
"""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def form_memcell(entry: Mapping[str, Any]) -> dict[str, Any]:
    """
    MemCell c = (E, F, P, M): episode, atomic facts, foresight, metadata.
    """
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    title = str(entry.get("title") or "").strip()
    body = str(entry.get("body") or "").strip()
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t0 = temporal.get("valid_from") or entry.get("created_at")
    episode = title or (body.split(".")[0].strip() if body else "episode")
    # Atomic facts: short lines / conflict key
    facts: list[str] = []
    ck = str(entry.get("conflict_key") or "").strip()
    if ck:
        facts.append(f"key:{ck}")
    if title:
        facts.append(title)
    for line in body.split("."):
        line = line.strip()
        if len(line) > 12:
            facts.append(line[:120])
            if len(facts) >= 4:
                break
    # Foresight: temporary vs durable cues
    low = body.lower()
    foresight: list[dict[str, Any]] = []
    if any(w in low for w in ("temporary", "while", "until", "this week", "antibiotics")):
        foresight.append(
            {
                "signal": "temporary_constraint",
                "t_start": t0,
                "t_end": None,
                "hint": "time_bounded",
            }
        )
    if any(w in low for w in ("always", "prefer", "policy", "never")):
        foresight.append(
            {
                "signal": "durable_preference",
                "t_start": t0,
                "t_end": None,
                "hint": "open_ended",
            }
        )
    meta = {
        "layer": entry.get("layer"),
        "scope": entry.get("scope"),
        "state": entry.get("state"),
        "entry_id": entry.get("id"),
    }
    cell_id = hashlib.sha256(
        canonical_dumps({"e": episode, "id": entry.get("id")}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cell_id": cell_id,
        "episode": episode,
        "facts": facts[:6],
        "foresight": foresight,
        "metadata": meta,
        "ok": True,
        "note": "evermemos form_memcell — E/F/P/M proxy",
    }


def consolidate_memscenes(
    entries: Sequence[Mapping[str, Any]],
    *,
    sim_threshold: float = 0.15,
) -> dict[str, Any]:
    """
    Online thematic MemScenes: cluster MemCells by lexical overlap + conflict_key.
    No embeddings — token Jaccard as sim proxy.
    """
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence is required")
    cells = [form_memcell(e) for e in entries if isinstance(e, Mapping)]
    scenes: list[dict[str, Any]] = []
    for cell in cells:
        toks = _tokens(f"{cell['episode']} {' '.join(cell['facts'])}")
        placed = False
        for scene in scenes:
            stoks = set(scene.get("centroid_tokens") or [])
            if not toks or not stoks:
                continue
            sim = len(toks & stoks) / len(toks | stoks)
            if sim >= sim_threshold:
                scene["cell_ids"].append(cell["cell_id"])
                scene["entry_ids"].append(cell["metadata"].get("entry_id"))
                scene["centroid_tokens"] = sorted(stoks | toks)[:48]
                scene["t_last"] = cell["metadata"].get("entry_id")
                placed = True
                break
        if not placed:
            # Also group by conflict_key stem when present
            ck = ""
            for f in cell["facts"]:
                if f.startswith("key:"):
                    ck = f[4:].split(":")[0]
                    break
            scenes.append(
                {
                    "scene_id": f"ms_{cell['cell_id']}",
                    "theme": ck or cell["episode"][:40],
                    "cell_ids": [cell["cell_id"]],
                    "entry_ids": [cell["metadata"].get("entry_id")],
                    "centroid_tokens": sorted(toks)[:48],
                    "t_last": cell["metadata"].get("entry_id"),
                }
            )
    return {
        "scene_count": len(scenes),
        "cell_count": len(cells),
        "scenes": scenes,
        "cells": cells,
        "ok": True,
        "note": "evermemos consolidate_memscenes — online cluster proxy",
    }


def foresight_filter(
    cells: Sequence[Mapping[str, Any]],
    *,
    now: str,
) -> dict[str, Any]:
    """Retain foresight whose validity window contains now (report-only)."""
    if not isinstance(now, str) or not now.strip():
        raise SchemaError("now timestamp required")
    now_s = now.strip()
    active: list[dict[str, Any]] = []
    expired: list[dict[str, Any]] = []
    for cell in cells:
        if not isinstance(cell, Mapping):
            continue
        for f in cell.get("foresight") or []:
            if not isinstance(f, Mapping):
                continue
            t_start = str(f.get("t_start") or "")
            t_end = f.get("t_end")
            row = {
                "cell_id": cell.get("cell_id"),
                "signal": f.get("signal"),
                "t_start": t_start,
                "t_end": t_end,
            }
            if t_end and str(t_end) < now_s:
                expired.append(row)
            elif t_start and t_start > now_s:
                expired.append(row)
            else:
                active.append(row)
    return {
        "now": now_s,
        "active": active,
        "expired": expired,
        "active_count": len(active),
        "expired_count": len(expired),
        "ok": True,
        "note": "evermemos foresight_filter",
    }


def reconstructive_recollect(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    n_scenes: int = 3,
    k_episodes: int = 5,
) -> dict[str, Any]:
    """MemScene-guided reconstructive recollection (necessity/sufficiency goal)."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string required")
    consol = consolidate_memscenes(entries)
    qtok = _tokens(query)
    scored: list[tuple[float, dict[str, Any]]] = []
    for scene in consol["scenes"]:
        stoks = set(scene.get("centroid_tokens") or [])
        sim = len(qtok & stoks) / max(1, len(qtok | stoks))
        scored.append((sim, scene))
    scored.sort(key=lambda x: (-x[0], x[1].get("scene_id")))
    top_scenes = [s for _, s in scored[: max(1, n_scenes)]]
    # Pool episodes from selected scenes
    entry_ids: list[str] = []
    for s in top_scenes:
        for eid in s.get("entry_ids") or []:
            if eid and eid not in entry_ids:
                entry_ids.append(str(eid))
    entry_ids = entry_ids[: max(1, k_episodes)]
    by_id = {
        str(e.get("id")): e for e in entries if isinstance(e, Mapping) and e.get("id")
    }
    episodes = []
    for eid in entry_ids:
        e = by_id.get(eid)
        if e:
            episodes.append(
                {
                    "id": eid,
                    "title": e.get("title"),
                    "layer": e.get("layer"),
                }
            )
    # Necessity/sufficiency: prefer fewer high-overlap episodes
    return {
        "query": query.strip(),
        "scenes": [
            {"scene_id": s.get("scene_id"), "theme": s.get("theme")}
            for s in top_scenes[:n_scenes]
        ],
        "episodes": episodes,
        "n_scenes": len(top_scenes[:n_scenes]),
        "k_episodes": len(episodes),
        "goal": "necessity_and_sufficiency",
        "ok": True,
        "note": "evermemos reconstructive_recollect — agentic recall proxy",
    }


def profile_evolve_plan(
    entries: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Scene-driven profile evolution plan (report-only; no auto-write)."""
    consol = consolidate_memscenes(entries)
    traits: list[str] = []
    facts: list[str] = []
    conflicts: list[dict[str, Any]] = []
    by_theme: dict[str, list[str]] = defaultdict(list)
    for scene in consol["scenes"]:
        theme = str(scene.get("theme") or "")
        by_theme[theme].extend(
            [str(i) for i in (scene.get("entry_ids") or []) if i]
        )
    for theme, ids in sorted(by_theme.items()):
        if len(ids) >= 2:
            traits.append(f"stable_theme:{theme}")
        facts.append(f"scene:{theme}:n={len(ids)}")
    # Conflict: same theme, divergent bodies
    for theme, ids in by_theme.items():
        bodies = set()
        for e in entries:
            if not isinstance(e, Mapping):
                continue
            if str(e.get("id")) in ids:
                bodies.add(str(e.get("body") or "").strip()[:80])
        if len(bodies) >= 2:
            conflicts.append(
                {
                    "theme": theme,
                    "action": "track_conflict",
                    "variants": len(bodies),
                }
            )
    return {
        "traits": traits[:12],
        "facts": facts[:12],
        "conflicts": conflicts,
        "apply": False,
        "ok": True,
        "note": "evermemos profile_evolve_plan — scene summaries only; no auto-write",
    }


def necessity_sufficiency_check(
    *,
    retrieved_count: int,
    min_needed: int = 1,
    max_sufficient: int = 10,
) -> dict[str, Any]:
    """Phase-III budget check: enough evidence, not over-retrieved."""
    if retrieved_count < 0:
        raise SchemaError("retrieved_count must be >= 0")
    necessary = retrieved_count >= min_needed
    sufficient = retrieved_count <= max_sufficient
    return {
        "retrieved_count": retrieved_count,
        "necessary": necessary,
        "sufficient": sufficient,
        "pass": necessary and sufficient,
        "ok": True,
        "note": "evermemos necessity_sufficiency_check",
    }
