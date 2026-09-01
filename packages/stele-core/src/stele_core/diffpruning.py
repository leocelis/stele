"""Diff Pruning proxies (stdlib; no LLM).

Shaped by Diff Pruning (arXiv:2012.07463): learn a sparse task-specific
difference-vector over frozen pretrained weights. Proxies only.

Prefix ``dpr_*`` — not PiSSA (``psa_*``) / BitFit (``bft_*``) / AdapterDrop.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dpr_diff(*, task: str) -> dict[str, Any]:
    """Allocate a task-specific difference-vector over frozen W0."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    did = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "diff_id": did,
        "ok": True,
        "note": "dpr dpr_diff",
    }


def dpr_mask(*, diff_id: str) -> dict[str, Any]:
    """Learn a sparsity mask over the difference-vector."""
    did = diff_id.strip()
    if not did:
        raise SchemaError("diff_id required")
    mid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mask_id": mid,
        "ok": True,
        "note": "dpr dpr_mask",
    }


def dpr_prune(*, mask_id: str, sparsity_pct: int) -> dict[str, Any]:
    """Prune to target sparsity percentage (0–100)."""
    mid = mask_id.strip()
    if not mid:
        raise SchemaError("mask_id required")
    if sparsity_pct < 0 or sparsity_pct > 100:
        raise SchemaError("sparsity_pct must be 0..100")
    pid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": sparsity_pct}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prune_id": pid,
        "sparsity_pct": sparsity_pct,
        "ok": True,
        "note": "dpr dpr_prune",
    }


def dpr_score(*, prune_id: str, score: int) -> dict[str, Any]:
    """Score Diff Pruning adaptation (0–100)."""
    pid = prune_id.strip()
    if not pid:
        raise SchemaError("prune_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "dpr dpr_score",
    }


def dpr_sparse(*, no_new_params: bool) -> dict[str, Any]:
    """Flag no new architecture params — sparse ΔW only (report-only)."""
    return {
        "no_new_params": no_new_params,
        "apply": False,
        "ok": True,
        "note": "dpr dpr_sparse",
    }


def dpr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Diff → mask → prune → score."""
    order = ("diff", "mask", "prune", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "diff"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dpr dpr_loop_plan",
    }
