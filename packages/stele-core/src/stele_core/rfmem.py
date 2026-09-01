"""RF-Mem-shaped recollection–familiarity retrieval (stdlib; no LLM).

Shaped by RF-Mem (arXiv:2603.09250): familiarity uncertainty routes to
top-K familiarity vs recollection expand with alpha-mix. Proxies only.
"""

from __future__ import annotations

from typing import Any

from stele_core.schema import SchemaError


def rfmem_familiarity_score(
    *,
    mean_score: float,
    entropy: float,
) -> dict[str, Any]:
    """Familiarity signal from mean similarity and entropy."""
    if not (0.0 <= mean_score <= 1.0) or entropy < 0.0:
        raise SchemaError("mean_score in [0,1] and entropy >= 0")
    return {
        "mean_score": round(mean_score, 4),
        "entropy": round(entropy, 4),
        "ok": True,
        "note": "rfmem rfmem_familiarity_score",
    }


def rfmem_path_route(
    *,
    mean_score: float,
    entropy: float,
    high_mean: float = 0.7,
    low_entropy: float = 1.0,
) -> dict[str, Any]:
    """Route: high familiarity → familiar path; else recollection."""
    if not (0.0 <= mean_score <= 1.0) or entropy < 0.0:
        raise SchemaError("invalid familiarity inputs")
    familiar = mean_score >= high_mean and entropy <= low_entropy
    return {
        "path": "familiarity" if familiar else "recollection",
        "ok": True,
        "note": "rfmem rfmem_path_route",
    }


def rfmem_top_k_familiar(*, candidates: int, top_k: int) -> dict[str, Any]:
    """Familiarity path: direct top-K retrieval."""
    if candidates < 0 or top_k < 1:
        raise SchemaError("candidates >= 0 and top_k >= 1")
    return {
        "selected": min(candidates, top_k),
        "top_k": top_k,
        "ok": True,
        "note": "rfmem rfmem_top_k_familiar",
    }


def rfmem_recollect_expand(
    *,
    clusters: int,
    hops: int,
    max_hops: int = 3,
) -> dict[str, Any]:
    """Recollection path: cluster and expand evidence hops."""
    if clusters < 0 or hops < 0 or max_hops < 1:
        raise SchemaError("clusters/hops >= 0 and max_hops >= 1")
    expand = clusters > 0 and hops <= max_hops
    return {
        "expand": expand,
        "hops": hops,
        "ok": True,
        "note": "rfmem rfmem_recollect_expand",
    }


def rfmem_alpha_mix(*, alpha: float, query_weight: float) -> dict[str, Any]:
    """Alpha-mix query with cluster centroid in embedding space (proxy)."""
    if not (0.0 <= alpha <= 1.0) or not (0.0 <= query_weight <= 1.0):
        raise SchemaError("alpha and query_weight must be in [0, 1]")
    return {
        "alpha": round(alpha, 4),
        "query_weight": round(query_weight, 4),
        "ok": True,
        "note": "rfmem rfmem_alpha_mix",
    }


def rfmem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Score → route → retrieve → mix."""
    order = ("score", "route", "retrieve", "mix")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "score"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rfmem rfmem_loop_plan",
    }
