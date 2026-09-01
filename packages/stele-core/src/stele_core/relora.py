"""ReLoRA proxies (stdlib; no LLM).

Shaped by ReLoRA (arXiv:2307.05695): high-rank training via periodic
low-rank updates — warm-start, merge BA into W, restart LoRA with
jagged LR and partial optimizer reset. Proxies only.

Prefix ``rlr_*`` — not rsLoRA (``rsl_*``) / RandLoRA (``rlo_*``) /
ETHER (``eth_*``) / COLA (``col_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rlr_warm(*, task: str, steps: int) -> dict[str, Any]:
    """Full-rank warm-start (steps >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if steps < 1:
        raise SchemaError("steps must be >= 1")
    wid = hashlib.sha256(
        canonical_dumps({"t": t, "s": steps}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "warm_id": wid,
        "steps": steps,
        "ok": True,
        "note": "rlr rlr_warm",
    }


def rlr_merge(*, warm_id: str) -> dict[str, Any]:
    """Merge current LoRA into W and restart adapters."""
    wid = warm_id.strip()
    if not wid:
        raise SchemaError("warm_id required")
    mid = hashlib.sha256(
        canonical_dumps({"w": wid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "ok": True,
        "note": "rlr rlr_merge",
    }


def rlr_jagged(*, merge_id: str) -> dict[str, Any]:
    """Apply jagged LR + partial optimizer reset."""
    mid = merge_id.strip()
    if not mid:
        raise SchemaError("merge_id required")
    jid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "jagged_id": jid,
        "ok": True,
        "note": "rlr rlr_jagged",
    }


def rlr_score(*, jagged_id: str, score: int) -> dict[str, Any]:
    """Score ReLoRA high-rank training (0–100)."""
    jid = jagged_id.strip()
    if not jid:
        raise SchemaError("jagged_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"j": jid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "rlr rlr_score",
    }


def rlr_high(*, high_rank_update: bool) -> dict[str, Any]:
    """Flag aggregated high-rank update via restarts (report-only)."""
    return {
        "high_rank_update": high_rank_update,
        "apply": False,
        "ok": True,
        "note": "rlr rlr_high",
    }


def rlr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Warm → merge → jagged → score."""
    order = ("warm", "merge", "jagged", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "warm"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rlr rlr_loop_plan",
    }
