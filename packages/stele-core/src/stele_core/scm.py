"""SCM-shaped working memory + value tags + sleep cycle (stdlib; no LLM).

Working memory is a capacity-limited ring of entry ids (file overlay).
Sleep plans are report-only by default; NREM apply may reinforce usage only.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError, canonical_dumps, canonical_loads
from stele_core.sfams import composite_importance
from stele_core.worth import memory_worth

WM_NAME = "working_memory.json"
DEFAULT_WM_CAPACITY = 7


def _wm_path(root: Path) -> Path:
    return Path(root) / WM_NAME


def load_working_memory(root: Path) -> dict[str, Any]:
    path = _wm_path(root)
    if not path.is_file():
        return {"capacity": DEFAULT_WM_CAPACITY, "ids": [], "episodes": []}
    data = canonical_loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SchemaError("working_memory.json must be an object")
    return data


def save_working_memory(root: Path, data: Mapping[str, Any]) -> None:
    path = _wm_path(root)
    path.write_text(canonical_dumps(dict(data)), encoding="utf-8")


def value_tag(
    entry: Mapping[str, Any],
    *,
    now: str,
    peer_entries: Sequence[Mapping[str, Any]] | None = None,
    task_query: str = "",
) -> dict[str, Any]:
    """
    Four-dimensional importance proxy (SCM ValueTagger-shaped).

    novelty · task · repetition · polarity (helpful/harmful) — no embeddings.
    """
    tok = set(tokenize(f"{entry.get('title')}\n{entry.get('body')}"))
    peers = list(peer_entries or [])
    max_overlap = 0.0
    for p in peers:
        if p.get("id") == entry.get("id"):
            continue
        pt = set(tokenize(f"{p.get('title')}\n{p.get('body')}"))
        if tok and pt:
            max_overlap = max(
                max_overlap, len(tok & pt) / max(len(tok | pt), 1)
            )
    novelty = round(1.0 - max_overlap, 6)
    qtok = set(tokenize(task_query)) if task_query else set()
    task = (
        round(len(tok & qtok) / max(len(qtok), 1), 6) if qtok else 0.5
    )
    usage = entry.get("usage") or {}
    helpful = int(usage.get("helpful") or 0)
    harmful = int(usage.get("harmful") or 0)
    n = helpful + harmful
    repetition = round(min(1.0, n / 10.0), 6)
    polarity = 0.0
    if n:
        polarity = round((helpful - harmful) / n, 6)
    importance = round(
        0.30 * novelty + 0.35 * task + 0.15 * repetition + 0.20 * abs(polarity),
        6,
    )
    return {
        "id": entry.get("id"),
        "novelty": novelty,
        "task": task,
        "repetition": repetition,
        "polarity": polarity,
        "importance": importance,
        "note": "SCM value-tag proxy — not embeddings / LLM sentiment",
    }


def wm_push(
    root: Path,
    entry_id: str,
    *,
    capacity: int | None = None,
    note: str = "",
) -> dict[str, Any]:
    """Push entry id into working-memory ring (evict oldest when full)."""
    eid = str(entry_id or "").strip()
    if not eid:
        raise SchemaError("entry_id is required")
    data = load_working_memory(root)
    cap = int(capacity or data.get("capacity") or DEFAULT_WM_CAPACITY)
    if cap < 1:
        raise SchemaError("capacity must be >= 1")
    ids = [str(x) for x in (data.get("ids") or []) if x]
    episodes = list(data.get("episodes") or [])
    if eid in ids:
        ids = [x for x in ids if x != eid]
        episodes = [e for e in episodes if str(e.get("id")) != eid]
    ids.append(eid)
    episodes.append({"id": eid, "note": note})
    evicted: list[str] = []
    while len(ids) > cap:
        evicted.append(ids.pop(0))
        if episodes:
            episodes.pop(0)
    data = {"capacity": cap, "ids": ids, "episodes": episodes[-cap:]}
    save_working_memory(root, data)
    return {
        "ids": ids,
        "capacity": cap,
        "evicted": evicted,
        "count": len(ids),
        "ok": True,
        "note": "SCM working-memory overlay — not SoT",
    }


def wm_list(root: Path) -> dict[str, Any]:
    data = load_working_memory(root)
    ids = list(data.get("ids") or [])
    return {
        "ids": ids,
        "capacity": int(data.get("capacity") or DEFAULT_WM_CAPACITY),
        "count": len(ids),
        "episodes": list(data.get("episodes") or []),
        "ok": True,
    }


def wm_clear(root: Path) -> dict[str, Any]:
    save_working_memory(
        root, {"capacity": DEFAULT_WM_CAPACITY, "ids": [], "episodes": []}
    )
    return {"ok": True, "cleared": True}


def _importance_entropy(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    total = sum(max(0.0, v) for v in values) or 1.0
    h = 0.0
    for v in values:
        p = max(0.0, v) / total
        if p > 0:
            h -= p * math.log(p)
    # normalize by log(n)
    if len(values) > 1:
        h = h / math.log(len(values))
    return round(min(1.0, h), 6)


def sleep_trigger(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    wm_ids: Sequence[str] | None = None,
    entropy_threshold: float = 0.9,
    conflict_density_threshold: float = 0.3,
    force: bool = False,
) -> dict[str, Any]:
    """Decide whether a sleep cycle should run."""
    if force:
        return {
            "should_sleep": True,
            "reasons": ["force"],
            "ok": True,
        }
    pool = {str(e.get("id")): e for e in entries}
    wm = [pool[i] for i in (wm_ids or []) if i in pool]
    if not wm:
        wm = [e for e in pool.values() if e.get("state") == "promoted"][:7]
    tags = [value_tag(e, now=now, peer_entries=list(pool.values())) for e in wm]
    entropy = _importance_entropy([float(t["importance"]) for t in tags])
    contested = sum(1 for e in pool.values() if e.get("state") == "contested")
    total = max(1, len(pool))
    conflict_density = contested / total
    reasons: list[str] = []
    if entropy >= entropy_threshold:
        reasons.append("high_entropy")
    if conflict_density >= conflict_density_threshold:
        reasons.append("high_conflict_density")
    return {
        "should_sleep": bool(reasons),
        "reasons": reasons,
        "entropy": entropy,
        "conflict_density": round(conflict_density, 6),
        "ok": True,
        "note": "SCM sleep trigger — local proxy",
    }


def sleep_cycle_plan(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    wm_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """
    Offline sleep plan: NREM reinforce · REM novel links · FORGET archive cues.

    Report-only — does not mutate.
    """
    pool = list(entries)
    by_id = {str(e.get("id")): e for e in pool}
    wm = [by_id[i] for i in (wm_ids or []) if i in by_id]
    if not wm:
        wm = [e for e in pool if e.get("state") == "promoted"][:7]

    nrem: list[dict[str, Any]] = []
    for e in wm:
        if e.get("state") not in {"promoted", "contested"}:
            continue
        tag = value_tag(e, now=now, peer_entries=pool)
        cis = composite_importance(e, now=now)
        nrem.append(
            {
                "id": e.get("id"),
                "action": "reinforce" if tag["importance"] >= 0.45 else "downscale_flag",
                "importance": tag["importance"],
                "cis": cis.get("cis"),
            }
        )

    rem: list[dict[str, Any]] = []
    high = [
        e
        for e in pool
        if e.get("state") == "promoted"
        and float(composite_importance(e, now=now).get("cis") or 0) >= 0.5
    ]
    for i, a in enumerate(high):
        a_tok = set(tokenize(f"{a.get('title')}\n{a.get('body')}"))
        for b in high[i + 1 :]:
            if a.get("scope") != b.get("scope"):
                continue
            b_tok = set(tokenize(f"{b.get('title')}\n{b.get('body')}"))
            if not a_tok or not b_tok:
                continue
            overlap = len(a_tok & b_tok) / max(len(a_tok | b_tok), 1)
            if 0.15 <= overlap < 0.55:
                rem.append(
                    {
                        "a": a.get("id"),
                        "b": b.get("id"),
                        "action": "propose_link",
                        "overlap": round(overlap, 4),
                        "titles": [a.get("title"), b.get("title")],
                    }
                )
    rem = rem[:20]

    forget: list[dict[str, Any]] = []
    for e in pool:
        if e.get("state") != "promoted":
            continue
        if (e.get("usage") or {}).get("pinned"):
            continue
        mw = memory_worth(e)
        tag = value_tag(e, now=now, peer_entries=pool)
        if tag["importance"] < 0.25 and (
            not mw.get("known") or float(mw.get("mw") or 1) < 0.45
        ):
            forget.append(
                {
                    "id": e.get("id"),
                    "action": "archive_candidate",
                    "importance": tag["importance"],
                    "mw": mw.get("mw"),
                    "title": e.get("title"),
                }
            )
    forget = forget[:30]

    return {
        "nrem": nrem,
        "rem": rem,
        "forget": forget,
        "nrem_count": len(nrem),
        "rem_count": len(rem),
        "forget_count": len(forget),
        "ok": True,
        "note": "SCM sleep plan — report only; apply NREM reinforce separately",
    }
