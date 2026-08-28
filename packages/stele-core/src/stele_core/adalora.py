"""AdaLoRA proxies (stdlib; no LLM).

Shaped by AdaLoRA (arXiv:2303.10512): adaptive rank allocation — prune
unimportant singular values; concentrate budget on critical updates.
Proxies only.

Prefix ``adl_*`` — not QLoRA (``qlo_*``) / Adaptive-RAG / adaptive rewrite.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def adl_init(*, task: str, budget: int) -> dict[str, Any]:
    """Initialize adaptive-rank LoRA with a parameter budget (>=1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if budget < 1:
        raise SchemaError("budget must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"t": t, "b": budget}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "budget": budget,
        "ok": True,
        "note": "adl adl_init",
    }


def adl_svd(*, init_id: str) -> dict[str, Any]:
    """Factor updates via SVD for importance scoring."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    sid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "svd_id": sid,
        "ok": True,
        "note": "adl adl_svd",
    }


def adl_prune(*, svd_id: str, keep: int) -> dict[str, Any]:
    """Prune unimportant singular values; keep >=1 components."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    if keep < 1:
        raise SchemaError("keep must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"s": sid, "k": keep}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prune_id": pid,
        "keep": keep,
        "ok": True,
        "note": "adl adl_prune",
    }


def adl_score(*, prune_id: str, score: int) -> dict[str, Any]:
    """Score AdaLoRA adaptation (0–100)."""
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
        "note": "adl adl_score",
    }


def adl_adaptive(*, adaptive_rank: bool) -> dict[str, Any]:
    """Flag dynamic rank reallocation during training (report-only)."""
    return {
        "adaptive_rank": adaptive_rank,
        "apply": False,
        "ok": True,
        "note": "adl adl_adaptive",
    }


def adl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Init → svd → prune → score."""
    order = ("init", "svd", "prune", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "init"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "adl adl_loop_plan",
    }
