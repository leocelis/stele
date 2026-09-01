"""MemoryOS-shaped hierarchical STM/MTM/LPM (stdlib; no LLM).

Shaped by MemoryOS (arXiv:2506.06326): three-tier storage, segmented
paging, heat-based eviction/promotion, hierarchical retrieve.
Proxies only — not MemoryOS paper scores.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

TIERS = frozenset({"stm", "mtm", "lpm"})

_DEFAULT_ALPHA = 1.0
_DEFAULT_BETA = 0.5
_DEFAULT_GAMMA = 1.0
_DEFAULT_MU = 1e7
_DEFAULT_HEAT_TAU = 5.0


def classify_memory_tier(
    entry: Mapping[str, Any],
    *,
    now: str,
    stm_hours: float = 24.0,
) -> dict[str, Any]:
    """Heuristic tier: recent → STM; persona/preference → LPM; else MTM."""
    if not isinstance(entry, Mapping):
        raise SchemaError("entry mapping is required")
    layer = str(entry.get("layer") or "")
    body = f"{entry.get('title') or ''}\n{entry.get('body') or ''}".lower()
    temporal = entry.get("temporal") if isinstance(entry.get("temporal"), Mapping) else {}
    t = str(temporal.get("valid_from") or entry.get("created_at") or "")
    if any(w in body for w in ("prefer", "i am", "personality", "always like")):
        tier = "lpm"
    elif layer in {"decision", "workflow", "skill_artifact"} and "prefer" not in body:
        tier = "mtm"
    else:
        tier = "stm"
        # Without real clock math on ISO, treat missing time as stm
        if t and now and t[:10] < now[:10]:
            # older than "today" proxy → mid-term unless persona
            tier = "mtm"
    return {
        "id": entry.get("id"),
        "tier": tier,
        "ok": tier in TIERS,
        "note": "memoryos classify_memory_tier",
    }


def heat_score(
    *,
    n_visit: int = 0,
    l_interaction: int = 1,
    delta_t_seconds: float = 0.0,
    alpha: float = _DEFAULT_ALPHA,
    beta: float = _DEFAULT_BETA,
    gamma: float = _DEFAULT_GAMMA,
    mu: float = _DEFAULT_MU,
) -> dict[str, Any]:
    """Heat = α·N_visit + β·L_interaction + γ·R_recency; R=exp(-Δt/μ)."""
    if n_visit < 0 or l_interaction < 0:
        raise SchemaError("counts must be >= 0")
    if mu <= 0:
        raise SchemaError("mu must be > 0")
    r_recency = math.exp(-float(delta_t_seconds) / float(mu))
    heat = (
        alpha * float(n_visit)
        + beta * float(l_interaction)
        + gamma * r_recency
    )
    return {
        "heat": round(heat, 6),
        "n_visit": n_visit,
        "l_interaction": l_interaction,
        "r_recency": round(r_recency, 6),
        "delta_t_seconds": delta_t_seconds,
        "ok": True,
        "note": "memoryos heat_score — Eq.4 proxy",
    }


def segment_pages(
    entries: Sequence[Mapping[str, Any]],
    *,
    theta: float = 0.15,
) -> dict[str, Any]:
    """Segmented paging: group pages by conflict_key / lexical topic."""
    if not isinstance(entries, Sequence) or isinstance(entries, (str, bytes)):
        raise SchemaError("entries sequence required")
    by_key: dict[str, list[str]] = defaultdict(list)
    for e in entries:
        if not isinstance(e, Mapping) or not e.get("id"):
            continue
        ck = str(e.get("conflict_key") or "").strip()
        theme = ck.split(":")[0] if ck else str(e.get("layer") or "misc")
        by_key[theme].append(str(e.get("id")))
    segments: list[dict[str, Any]] = []
    for theme, ids in sorted(by_key.items()):
        segments.append(
            {
                "segment_id": f"seg:{theme}",
                "theme": theme,
                "page_ids": ids,
                "l_interaction": len(ids),
                "theta": theta,
            }
        )
    return {
        "segment_count": len(segments),
        "segments": segments,
        "ok": True,
        "note": "memoryos segment_pages — topic segments proxy",
    }


def stm_to_mtm_plan(
    stm_page_ids: Sequence[str],
    *,
    capacity: int = 5,
) -> dict[str, Any]:
    """FIFO STM overflow → transfer oldest pages to MTM (report-only)."""
    if capacity < 1:
        raise SchemaError("capacity must be >= 1")
    pages = [str(p) for p in stm_page_ids if p]
    overflow = max(0, len(pages) - capacity)
    transfer = pages[:overflow]  # oldest first
    retain = pages[overflow:]
    return {
        "capacity": capacity,
        "stm_count": len(pages),
        "transfer_to_mtm": transfer,
        "retain_in_stm": retain,
        "apply": False,
        "ok": True,
        "note": "memoryos stm_to_mtm_plan — FIFO proxy",
    }


def mtm_evict_plan(
    segments: Sequence[Mapping[str, Any]],
    *,
    max_segments: int = 3,
    alpha: float = _DEFAULT_ALPHA,
    beta: float = _DEFAULT_BETA,
    gamma: float = _DEFAULT_GAMMA,
) -> dict[str, Any]:
    """Evict lowest-heat MTM segments when over capacity (report-only)."""
    if max_segments < 1:
        raise SchemaError("max_segments must be >= 1")
    scored: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, Mapping):
            continue
        h = heat_score(
            n_visit=int(seg.get("n_visit") or 0),
            l_interaction=int(seg.get("l_interaction") or len(seg.get("page_ids") or [])),
            delta_t_seconds=float(seg.get("delta_t_seconds") or 0.0),
            alpha=alpha,
            beta=beta,
            gamma=gamma,
        )
        scored.append(
            {
                "segment_id": seg.get("segment_id") or seg.get("theme"),
                "heat": h["heat"],
                "page_ids": list(seg.get("page_ids") or []),
            }
        )
    scored.sort(key=lambda x: (x["heat"], str(x["segment_id"])))
    overflow = max(0, len(scored) - max_segments)
    evict = scored[:overflow]
    keep = scored[overflow:]
    return {
        "max_segments": max_segments,
        "evict": evict,
        "keep": keep,
        "apply": False,
        "ok": True,
        "note": "memoryos mtm_evict_plan — lowest heat first",
    }


def promote_to_lpm_plan(
    segments: Sequence[Mapping[str, Any]],
    *,
    tau: float = _DEFAULT_HEAT_TAU,
) -> dict[str, Any]:
    """Promote segments with heat > τ to LPM (report-only)."""
    promote: list[dict[str, Any]] = []
    for seg in segments:
        if not isinstance(seg, Mapping):
            continue
        heat = float(seg.get("heat") or 0.0)
        if "heat" not in seg:
            heat = heat_score(
                n_visit=int(seg.get("n_visit") or 0),
                l_interaction=int(
                    seg.get("l_interaction") or len(seg.get("page_ids") or [])
                ),
                delta_t_seconds=float(seg.get("delta_t_seconds") or 0.0),
            )["heat"]
        if heat >= tau:
            promote.append(
                {
                    "segment_id": seg.get("segment_id") or seg.get("theme"),
                    "heat": heat,
                    "action": "promote_lpm",
                }
            )
    return {
        "tau": tau,
        "promote_count": len(promote),
        "promote": promote,
        "apply": False,
        "ok": True,
        "note": "memoryos promote_to_lpm_plan",
    }


def hierarchical_retrieve(
    entries: Sequence[Mapping[str, Any]],
    *,
    query: str,
    now: str,
    top_m_segments: int = 2,
    top_k_pages: int = 3,
) -> dict[str, Any]:
    """Retrieve from STM (all recent) + MTM two-stage + LPM persona hits."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string required")
    q = query.lower()
    stm: list[str] = []
    mtm_pages: list[str] = []
    lpm: list[str] = []
    segs = segment_pages(entries)["segments"]
    # Score segments by keyword overlap with query
    scored_segs: list[tuple[int, dict[str, Any]]] = []
    for seg in segs:
        theme = str(seg.get("theme") or "").lower()
        score = sum(1 for w in q.split() if w and w in theme)
        scored_segs.append((score, seg))
    scored_segs.sort(key=lambda x: (-x[0], str(x[1].get("segment_id"))))
    chosen = [s for sc, s in scored_segs[:top_m_segments] if sc >= 0]

    by_id = {
        str(e.get("id")): e for e in entries if isinstance(e, Mapping) and e.get("id")
    }
    for e in entries:
        if not isinstance(e, Mapping):
            continue
        tier = classify_memory_tier(e, now=now)["tier"]
        eid = str(e.get("id"))
        blob = f"{e.get('title') or ''} {e.get('body') or ''}".lower()
        hit = any(w in blob for w in q.split() if len(w) > 2)
        if tier == "stm":
            stm.append(eid)
        elif tier == "lpm" and hit:
            lpm.append(eid)
    for seg in chosen:
        for pid in (seg.get("page_ids") or [])[:top_k_pages]:
            if pid not in mtm_pages:
                mtm_pages.append(str(pid))
    return {
        "query": query.strip(),
        "stm": stm[:10],
        "mtm_segments": [s.get("segment_id") for s in chosen],
        "mtm_pages": mtm_pages[: top_m_segments * top_k_pages],
        "lpm": lpm[:10],
        "ok": True,
        "note": "memoryos hierarchical_retrieve — STM+MTM+LPM proxy",
    }
