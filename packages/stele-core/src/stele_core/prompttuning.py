"""Prompt Tuning proxies (stdlib; no LLM).

Shaped by Prompt Tuning (Lester et al., arXiv:2104.08691): soft
prompt embeddings at the input layer only, scaling with model size.
Proxies only.

Prefix ``ptl_*`` — not P-Tuning v2 (``ptv_*``) / Prefix-Tuning (``pfx_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ptl_soft(*, task: str) -> dict[str, Any]:
    """Allocate input-layer soft prompt embeddings for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    sid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "soft_id": sid,
        "ok": True,
        "note": "ptl ptl_soft",
    }


def ptl_prepend(*, soft_id: str) -> dict[str, Any]:
    """Prepend soft prompts to the embedded input sequence."""
    sid = soft_id.strip()
    if not sid:
        raise SchemaError("soft_id required")
    pid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prep_id": pid,
        "ok": True,
        "note": "ptl ptl_prepend",
    }


def ptl_optimize(*, prep_id: str) -> dict[str, Any]:
    """Tune soft prompts with frozen LM parameters."""
    pid = prep_id.strip()
    if not pid:
        raise SchemaError("prep_id required")
    oid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "opt_id": oid,
        "ok": True,
        "note": "ptl ptl_optimize",
    }


def ptl_scale(*, opt_id: str, score: int) -> dict[str, Any]:
    """Score quality; paper notes strong scaling with model size (0–100)."""
    oid = opt_id.strip()
    if not oid:
        raise SchemaError("opt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"o": oid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "score": score,
        "ok": True,
        "note": "ptl ptl_scale",
    }


def ptl_input_only(*, input_layer_only: bool) -> dict[str, Any]:
    """Flag input-layer-only soft prompts vs deep prompts (report-only)."""
    return {
        "input_layer_only": input_layer_only,
        "apply": False,
        "ok": True,
        "note": "ptl ptl_input_only",
    }


def ptl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Soft → prepend → optimize → scale."""
    order = ("soft", "prepend", "optimize", "scale")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "soft"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ptl ptl_loop_plan",
    }
