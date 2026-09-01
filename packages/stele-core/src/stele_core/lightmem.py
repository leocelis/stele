"""LightMem-shaped sensory filter + Atkinson–Shiffrin stages (stdlib; no LLM).

Stages: sensory · stm · ltm. Sensory pre-filters draft text; STM is WM/hot;
LTM is promoted durable. Proxies only — not LightMem LongMemEval scores.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.lifecycle import lifecycle_tier
from stele_core.schema import SchemaError

LIGHTMEM_STAGES = frozenset({"sensory", "stm", "ltm"})

_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "of",
        "to",
        "in",
        "on",
        "for",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "with",
        "as",
        "at",
        "by",
        "from",
        "that",
        "this",
        "it",
        "its",
    }
)


def sensory_filter(
    text: str,
    *,
    keep_ratio: float = 1.0,
    min_token_len: int = 3,
) -> dict[str, Any]:
    """
    Lightweight pre-compression: drop stopwords / short tokens.

    Optional keep_ratio < 1 further trims by length rank (longest first).
    Deterministic — not LLMLingua.
    """
    if not (0 < keep_ratio <= 1):
        raise SchemaError("keep_ratio must be in (0, 1]")
    raw = str(text or "")
    toks = tokenize(raw)
    kept: list[str] = []
    dropped: list[str] = []
    for t in toks:
        if t in _STOP or len(t) < min_token_len:
            dropped.append(t)
        else:
            kept.append(t)
    if not kept and toks:
        kept = sorted(toks, key=len, reverse=True)[: max(1, int(len(toks) * keep_ratio))]
        dropped = [t for t in toks if t not in kept]
    if keep_ratio < 1.0 and kept:
        target = max(1, int(round(len(kept) * keep_ratio)))
        ranked = sorted(kept, key=lambda t: (-len(t), t))
        final_set = set(ranked[:target])
        ordered = [t for t in kept if t in final_set]
    else:
        ordered = list(kept)
    return {
        "original_tokens": len(toks),
        "kept_tokens": ordered,
        "dropped_count": len(dropped) + max(0, len(kept) - len(ordered)),
        "compressed_text": " ".join(ordered),
        "keep_ratio": keep_ratio,
        "ok": True,
        "note": "LightMem sensory filter proxy — not LLMLingua",
    }


def assign_stage(
    entry: Mapping[str, Any],
    *,
    now: str,
    wm_ids: Sequence[str] | None = None,
) -> str:
    """Map entry → sensory/stm/ltm."""
    state = str(entry.get("state") or "")
    eid = str(entry.get("id") or "")
    if state == "quarantined":
        return "sensory"
    if wm_ids and eid in set(wm_ids):
        return "stm"
    if state == "archived":
        return "ltm"  # cold long-term archive still LTM tier
    if state in {"promoted", "contested"}:
        tier = lifecycle_tier(dict(entry), now=now)
        return "stm" if tier == "hot" else "ltm"
    return "sensory"


def stage_inventory(
    entries: Iterable[Mapping[str, Any]],
    *,
    now: str,
    wm_ids: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Count entries per LightMem stage."""
    counts = {"sensory": 0, "stm": 0, "ltm": 0}
    rows: list[dict[str, Any]] = []
    for e in entries:
        stage = assign_stage(e, now=now, wm_ids=wm_ids)
        counts[stage] = counts.get(stage, 0) + 1
        rows.append(
            {
                "id": e.get("id"),
                "stage": stage,
                "state": e.get("state"),
                "title": e.get("title"),
            }
        )
    return {
        "counts": counts,
        "entries": rows,
        "ok": True,
        "note": "LightMem stage inventory — Atkinson–Shiffrin proxy",
    }


def topic_segments(
    texts: Sequence[str],
    *,
    threshold: float = 0.35,
) -> dict[str, Any]:
    """
    Split a sequence of texts into topic segments (adjacent Jaccard boundary).
    """
    if not (0 < threshold <= 1):
        raise SchemaError("threshold must be in (0, 1]")
    if not texts:
        return {"segments": [], "boundaries": [], "count": 0, "ok": True}
    boundaries: list[int] = []
    for i in range(1, len(texts)):
        a = set(tokenize(texts[i - 1]))
        b = set(tokenize(texts[i]))
        if not a or not b:
            boundaries.append(i)
            continue
        overlap = len(a & b) / max(len(a | b), 1)
        if overlap < threshold:
            boundaries.append(i)
    segments: list[dict[str, Any]] = []
    start = 0
    for b in boundaries + [len(texts)]:
        chunk = list(texts[start:b])
        segments.append(
            {
                "start": start,
                "end": b - 1,
                "size": len(chunk),
                "preview": (chunk[0][:80] if chunk else ""),
            }
        )
        start = b
    return {
        "segments": segments,
        "boundaries": boundaries,
        "count": len(segments),
        "ok": True,
        "note": "LightMem topic segmentation proxy",
    }


def stage_budget_plan(
    query: str,
    hits_by_stage: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    budget: int = 400,
    stm_share: float = 0.35,
    ltm_share: float = 0.55,
) -> dict[str, Any]:
    """
    Allocate reader budget across STM/LTM (sensory last / residual).

    Efficiency-first retrieval plan — LightMem-shaped.
    """
    if budget < 1:
        raise SchemaError("budget must be >= 1")
    if not (0 < stm_share < 1) or not (0 < ltm_share < 1):
        raise SchemaError("shares must be in (0, 1)")
    if stm_share + ltm_share >= 1:
        raise SchemaError("stm_share + ltm_share must be < 1 (residual for sensory)")
    stm_budget = int(budget * stm_share)
    ltm_budget = int(budget * ltm_share)
    sensory_budget = budget - stm_budget - ltm_budget

    def _pack(rows: Sequence[Mapping[str, Any]], limit: int) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        used = 0
        for h in rows:
            cost = len(str(h.get("title") or "")) + len(str(h.get("body") or ""))
            cost = max(1, cost)
            if used + cost > limit and out:
                break
            if used + cost > limit and not out:
                out.append(
                    {
                        "id": h.get("id"),
                        "stage": h.get("stage"),
                        "cost": min(cost, limit),
                    }
                )
                break
            out.append({"id": h.get("id"), "stage": h.get("stage"), "cost": cost})
            used += cost
        return out

    plan = {
        "stm": _pack(list(hits_by_stage.get("stm") or []), stm_budget),
        "ltm": _pack(list(hits_by_stage.get("ltm") or []), ltm_budget),
        "sensory": _pack(list(hits_by_stage.get("sensory") or []), sensory_budget),
    }
    used = sum(
        sum(int(x.get("cost") or 0) for x in plan[k]) for k in ("stm", "ltm", "sensory")
    )
    return {
        "query": query,
        "budget": budget,
        "allocations": {
            "stm": stm_budget,
            "ltm": ltm_budget,
            "sensory": sensory_budget,
        },
        "plan": plan,
        "used": used,
        "ok": used <= budget,
        "note": "LightMem stage budget plan — efficiency proxy",
    }
