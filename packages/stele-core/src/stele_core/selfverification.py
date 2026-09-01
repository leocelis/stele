"""Self-Verification proxies (stdlib; no LLM).

Shaped by Self-Verification (arXiv:2212.09561): forward CoT
candidates → backward mask/re-predict → verification score. Proxies only.

Prefix ``sve_*`` — not CoVe (``cove_*``) / Voyager ``voy_self_verify``.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sve_forward(*, problem: str) -> dict[str, Any]:
    """Forward reasoning: generate candidate CoT conclusions."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    fid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "candidate_id": fid,
        "ok": True,
        "note": "sve sve_forward",
    }


def sve_mask(*, candidate_id: str) -> dict[str, Any]:
    """Mask original conditions for backward verification."""
    cid = candidate_id.strip()
    if not cid:
        raise SchemaError("candidate_id required")
    mid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mask_id": mid,
        "ok": True,
        "note": "sve sve_mask",
    }


def sve_repredict(*, mask_id: str) -> dict[str, Any]:
    """Re-predict masked conditions given the candidate conclusion."""
    mid = mask_id.strip()
    if not mid:
        raise SchemaError("mask_id required")
    rid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "repred_id": rid,
        "ok": True,
        "note": "sve sve_repredict",
    }


def sve_score(*, score: int) -> dict[str, Any]:
    """Explainable verification score (0–100)."""
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    return {
        "score": score,
        "ok": True,
        "note": "sve sve_score",
    }


def sve_select(*, pick_best: bool) -> dict[str, Any]:
    """Flag selecting highest-scoring candidate (report-only)."""
    return {
        "pick_best": pick_best,
        "apply": False,
        "ok": True,
        "note": "sve sve_select",
    }


def sve_loop_plan(*, phase: str) -> dict[str, Any]:
    """Forward → mask → repredict → score."""
    order = ("forward", "mask", "repredict", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "forward"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "sve sve_loop_plan",
    }
