"""LoRA.rar proxies (stdlib; no LLM).

Shaped by LoRA.rar (arXiv:2412.05148): hypernetwork predicts merge
coefficients for unseen subject–style LoRA pairs — real-time merge
without per-pair optimization. Proxies only.

Prefix ``lrr_*`` — not ReLoRA (``rlr_*``) / LoRA-Composer (``lco_*``)
/ SVFT (``svf_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lrr_pair(*, task: str, n_pairs: int) -> dict[str, Any]:
    """Register subject–style LoRA pairs (n_pairs >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_pairs < 1:
        raise SchemaError("n_pairs must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_pairs}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pair_id": pid,
        "n_pairs": n_pairs,
        "ok": True,
        "note": "lrr lrr_pair",
    }


def lrr_hyper(*, pair_id: str) -> dict[str, Any]:
    """Predict merge coefficients via hypernetwork."""
    pid = pair_id.strip()
    if not pid:
        raise SchemaError("pair_id required")
    hid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hyper_id": hid,
        "ok": True,
        "note": "lrr lrr_hyper",
    }


def lrr_merge(*, hyper_id: str) -> dict[str, Any]:
    """Apply predicted subject–style merge."""
    hid = hyper_id.strip()
    if not hid:
        raise SchemaError("hyper_id required")
    mid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "ok": True,
        "note": "lrr lrr_merge",
    }


def lrr_score(*, merge_id: str, score: int) -> dict[str, Any]:
    """Score LoRA.rar merge (0–100)."""
    mid = merge_id.strip()
    if not mid:
        raise SchemaError("merge_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lrr lrr_score",
    }


def lrr_fast(*, realtime_merge: bool) -> dict[str, Any]:
    """Flag real-time merge (report-only)."""
    return {
        "realtime_merge": realtime_merge,
        "apply": False,
        "ok": True,
        "note": "lrr lrr_fast",
    }


def lrr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pair → hyper → merge → score."""
    order = ("pair", "hyper", "merge", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pair"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lrr lrr_loop_plan",
    }
