"""PeriodicLoRA proxies (stdlib; no LLM).

Shaped by PeriodicLoRA (arXiv:2402.16141): merge LoRA into W each
stage then reinit, so stacked low-rank updates raise effective rank
without extra memory. Proxies only.

Prefix ``plr_*`` — not LoRA-Pro (``lpr_*``) / ReLoRA (``rlr_*``) /
GLoRA (``glo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def plr_stage(*, task: str, stages: int) -> dict[str, Any]:
    """Open a periodic stage (stages >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if stages < 1:
        raise SchemaError("stages must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "n": stages}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "stage_id": sid,
        "stages": stages,
        "ok": True,
        "note": "plr plr_stage",
    }


def plr_merge(*, stage_id: str) -> dict[str, Any]:
    """Unload BA into W at stage end."""
    sid = stage_id.strip()
    if not sid:
        raise SchemaError("stage_id required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "ok": True,
        "note": "plr plr_merge",
    }


def plr_reset(*, merge_id: str) -> dict[str, Any]:
    """Reinit LoRA weights, optimizer, and LR."""
    mid = merge_id.strip()
    if not mid:
        raise SchemaError("merge_id required")
    rid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reset_id": rid,
        "ok": True,
        "note": "plr plr_reset",
    }


def plr_score(*, reset_id: str, score: int) -> dict[str, Any]:
    """Score PeriodicLoRA run (0–100)."""
    rid = reset_id.strip()
    if not rid:
        raise SchemaError("reset_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"r": rid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "plr plr_score",
    }


def plr_rank(*, accum_rank: bool) -> dict[str, Any]:
    """Flag accumulated high-rank via stages (report-only)."""
    return {
        "accum_rank": accum_rank,
        "apply": False,
        "ok": True,
        "note": "plr plr_rank",
    }


def plr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Stage → merge → reset → score."""
    order = ("stage", "merge", "reset", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "stage"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "plr plr_loop_plan",
    }
