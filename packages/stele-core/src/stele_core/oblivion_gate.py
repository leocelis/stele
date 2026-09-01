"""Oblivion-shaped uncertainty-gated retrieval + adaptive budget (stdlib; no LLM).

Shaped by Oblivion (arXiv:2604.00131) Decayer/Activator and MemArchitect
adaptive token budgeting — retrieve only when uncertainty is high.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def uncertainty_score(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    *,
    min_overlap: float = 0.15,
) -> dict[str, Any]:
    """
    High uncertainty when few hits or weak lexical overlap with the query.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    qtok = set(tokenize(q))
    overlaps: list[float] = []
    for h in hits:
        if not isinstance(h, Mapping):
            continue
        text = f"{h.get('title') or ''}\n{h.get('body') or ''}"
        et = set(tokenize(text))
        if not qtok:
            overlaps.append(0.0)
            continue
        overlaps.append(len(qtok & et) / max(len(qtok), 1))
    n = len(overlaps)
    max_ov = max(overlaps) if overlaps else 0.0
    mean_ov = sum(overlaps) / n if n else 0.0
    # Uncertainty rises when coverage is thin
    coverage = min(1.0, n / 3.0) * max_ov
    uncertainty = round(max(0.0, min(1.0, 1.0 - coverage)), 4)
    return {
        "uncertainty": uncertainty,
        "hit_count": n,
        "max_overlap": round(max_ov, 4),
        "mean_overlap": round(mean_ov, 4),
        "high": uncertainty >= 0.55 or (n == 0) or max_ov < min_overlap,
        "ok": True,
        "note": "oblivion_gate uncertainty_score — Decayer proxy",
    }


def uncertainty_retrieve_gate(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    *,
    force: bool = False,
    uncertainty_threshold: float = 0.55,
) -> dict[str, Any]:
    """
    Activate retrieval when uncertainty is high; otherwise skip (use working state).
    """
    if uncertainty_threshold < 0 or uncertainty_threshold > 1:
        raise SchemaError("uncertainty_threshold must be in [0, 1]")
    u = uncertainty_score(query, hits)
    if force:
        decision = "retrieve"
        reason = "forced"
    elif u["uncertainty"] >= uncertainty_threshold or u["high"]:
        decision = "retrieve"
        reason = "high_uncertainty"
    else:
        decision = "skip"
        reason = "low_uncertainty"
    return {
        "decision": decision,
        "reason": reason,
        "uncertainty": u["uncertainty"],
        "hit_count": u["hit_count"],
        "ok": True,
        "note": "oblivion_gate uncertainty_retrieve_gate — Activator proxy",
    }


def reasoning_reserve_plan(
    budget: int,
    *,
    confidence: float,
) -> dict[str, Any]:
    """
    MemArchitect-shaped adaptive split: high confidence → more reasoning reserve;
    low confidence → more recall reserve.
    """
    if budget < 1:
        raise SchemaError("budget must be >= 1")
    conf = float(confidence)
    if conf < 0 or conf > 1:
        raise SchemaError("confidence must be in [0, 1]")
    # High conf → 30% reasoning / 70% recall floor flipped: paper says
    # high-confidence → Reasoning Reserve 30%; low → Recall Reserve heavy (90%)
    if conf >= 0.7:
        reason_frac = 0.30
    elif conf <= 0.3:
        reason_frac = 0.10
    else:
        reason_frac = 0.10 + (conf - 0.3) * (0.20 / 0.4)
    reason_tokens = int(round(budget * reason_frac))
    recall_tokens = budget - reason_tokens
    return {
        "budget": budget,
        "confidence": round(conf, 4),
        "reasoning_reserve": reason_tokens,
        "recall_reserve": recall_tokens,
        "reasoning_fraction": round(reason_frac, 4),
        "ok": True,
        "note": "oblivion_gate reasoning_reserve_plan — MemArchitect adaptive budget",
    }
