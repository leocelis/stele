"""LoRA-drop proxies (stdlib; no LLM).

Shaped by LoRA-drop (COLING 2025 / arXiv:2402.07721): prune LoRA by
output importance — keep important layers, share LoRA across the rest.
Proxies only.

Prefix ``ldr_*`` — not DropLoRA (``drl_*``) / LoRA-Dash (``lds_*``) / VB-LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ldr_eval(*, task: str) -> dict[str, Any]:
    """Evaluate LoRA output importance across layers."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    eid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "eval_id": eid,
        "ok": True,
        "note": "ldr ldr_eval",
    }


def ldr_keep(*, eval_id: str, keep_pct: int) -> dict[str, Any]:
    """Retain top layers by output importance (keep_pct 1..100)."""
    eid = eval_id.strip()
    if not eid:
        raise SchemaError("eval_id required")
    if keep_pct < 1 or keep_pct > 100:
        raise SchemaError("keep_pct must be 1..100")
    kid = hashlib.sha256(
        canonical_dumps({"e": eid, "k": keep_pct}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "keep_id": kid,
        "keep_pct": keep_pct,
        "ok": True,
        "note": "ldr ldr_keep",
    }


def ldr_share(*, keep_id: str) -> dict[str, Any]:
    """Share one LoRA across non-kept layers."""
    kid = keep_id.strip()
    if not kid:
        raise SchemaError("keep_id required")
    sid = hashlib.sha256(
        canonical_dumps({"k": kid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": sid,
        "ok": True,
        "note": "ldr ldr_share",
    }


def ldr_score(*, share_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-drop adaptation (0–100)."""
    sid = share_id.strip()
    if not sid:
        raise SchemaError("share_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    scid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": scid,
        "score": score,
        "ok": True,
        "note": "ldr ldr_score",
    }


def ldr_prune(*, half_params: bool) -> dict[str, Any]:
    """Flag ~50% LoRA param retention (report-only)."""
    return {
        "half_params": half_params,
        "apply": False,
        "ok": True,
        "note": "ldr ldr_prune",
    }


def ldr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Eval → keep → share → score."""
    order = ("eval", "keep", "share", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "eval"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ldr ldr_loop_plan",
    }
