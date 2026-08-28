"""Chain of LoRA (COLA) proxies (stdlib; no LLM).

Shaped by Chain of LoRA / COLA (arXiv:2401.04151): residual learning —
tune LoRA, merge into W (tie a knot), extend the chain with a fresh
adapter — Frank-Wolfe-inspired path toward full fine-tune quality.
Proxies only.

Prefix ``col_*`` — not SwitchLoRA (``swl_*``) / Chain-of-Density /
Chain-of-Verification.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def col_tune(*, task: str, rank: int) -> dict[str, Any]:
    """Tune current LoRA link (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tune_id": tid,
        "rank": rank,
        "ok": True,
        "note": "col col_tune",
    }


def col_knot(*, tune_id: str) -> dict[str, Any]:
    """Merge BA into W (tie a knot)."""
    tid = tune_id.strip()
    if not tid:
        raise SchemaError("tune_id required")
    kid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "knot_id": kid,
        "ok": True,
        "note": "col col_knot",
    }


def col_extend(*, knot_id: str) -> dict[str, Any]:
    """Extend the chain with a fresh LoRA module."""
    kid = knot_id.strip()
    if not kid:
        raise SchemaError("knot_id required")
    eid = hashlib.sha256(
        canonical_dumps({"k": kid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "extend_id": eid,
        "ok": True,
        "note": "col col_extend",
    }


def col_score(*, extend_id: str, score: int) -> dict[str, Any]:
    """Score COLA residual chain (0–100)."""
    eid = extend_id.strip()
    if not eid:
        raise SchemaError("extend_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"e": eid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "col col_score",
    }


def col_gap(*, closes_ft_gap: bool) -> dict[str, Any]:
    """Flag closing LoRA↔full-FT generalization gap (report-only)."""
    return {
        "closes_ft_gap": closes_ft_gap,
        "apply": False,
        "ok": True,
        "note": "col col_gap",
    }


def col_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tune → knot → extend → score."""
    order = ("tune", "knot", "extend", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tune"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "col col_loop_plan",
    }
