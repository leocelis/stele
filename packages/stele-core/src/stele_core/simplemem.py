"""SimpleMem-shaped semantic lossless compression (stdlib; no LLM).

Shaped by SimpleMem (arXiv:2601.02553): structured compression, online
synthesis, intent-aware retrieval planning with adaptive depth. Proxies
only — not SimpleMem paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def simplemem_compress(
    *,
    raw_turns: int,
    window: int = 20,
) -> dict[str, Any]:
    """Semantic structured compression into multi-view units."""
    if raw_turns < 0 or window < 1:
        raise SchemaError("raw_turns >= 0 and window >= 1")
    units = (raw_turns + window - 1) // window if raw_turns else 0
    uid = hashlib.sha256(
        canonical_dumps({"t": raw_turns, "w": window}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "batch_id": uid,
        "units": units,
        "window": window,
        "ok": True,
        "note": "simplemem simplemem_compress",
    }


def simplemem_synthesize(
    *,
    related_facts: int,
    min_related: int = 2,
) -> dict[str, Any]:
    """Online semantic synthesis: merge related facts into one abstract."""
    if related_facts < 0 or min_related < 1:
        raise SchemaError("related_facts >= 0 and min_related >= 1")
    synthesize = related_facts >= min_related
    return {
        "synthesize": synthesize,
        "related_facts": related_facts,
        "apply": False,
        "ok": True,
        "note": "simplemem simplemem_synthesize",
    }


def simplemem_intent_scope(
    *,
    complexity: str,
) -> dict[str, Any]:
    """Intent-aware retrieval planning: map complexity → depth band."""
    if complexity not in ("simple", "medium", "complex"):
        raise SchemaError("complexity must be simple, medium, or complex")
    depth = {"simple": 3, "medium": 10, "complex": 20}[complexity]
    return {
        "complexity": complexity,
        "k": depth,
        "ok": True,
        "note": "simplemem simplemem_intent_scope",
    }


def simplemem_multiview_index(
    *,
    dense: bool,
    sparse: bool,
    metadata: bool,
) -> dict[str, Any]:
    """Multi-view index: dense + sparse + metadata."""
    views = sum([dense, sparse, metadata])
    return {
        "views": views,
        "ready": views >= 2,
        "ok": True,
        "note": "simplemem simplemem_multiview_index",
    }


def simplemem_token_ratio(
    *,
    tokens_baseline: int,
    tokens_simplemem: int,
) -> dict[str, Any]:
    """Inference token reduction vs baseline (report-only)."""
    if tokens_baseline < 1 or tokens_simplemem < 0:
        raise SchemaError("tokens_baseline >= 1 and tokens_simplemem >= 0")
    if tokens_simplemem > tokens_baseline:
        raise SchemaError("tokens_simplemem must be <= baseline")
    ratio = round(tokens_baseline / max(tokens_simplemem, 1), 4)
    return {
        "reduction_factor": ratio,
        "tokens_baseline": tokens_baseline,
        "tokens_simplemem": tokens_simplemem,
        "ok": True,
        "note": "simplemem simplemem_token_ratio",
    }


def simplemem_loop_plan(*, phase: str) -> dict[str, Any]:
    """Compress → synthesize → retrieve."""
    order = ("compress", "synthesize", "retrieve")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "compress"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "simplemem simplemem_loop_plan",
    }
