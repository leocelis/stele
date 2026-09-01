"""Multitask Prompt Tuning (MPT) proxies (stdlib; no LLM).

Shaped by Multitask Prompt Tuning (arXiv:2303.02861): shared shared
prompt matrix × low-rank task-specific factors for transfer. Proxies only.

Prefix ``mptp_*`` — not ATTEMPT (``atm_*``) / Soft Prompt Mixtures (``msp_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mptp_shared(*, corpus: str) -> dict[str, Any]:
    """Learn a shared soft-prompt matrix across multitask sources."""
    c = corpus.strip()
    if not c:
        raise SchemaError("corpus required")
    sid = hashlib.sha256(
        canonical_dumps({"c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "shared_id": sid,
        "ok": True,
        "note": "mptp mptp_shared",
    }


def mptp_factor(*, shared_id: str, task: str) -> dict[str, Any]:
    """Factor a task prompt into shared × low-rank task-specific matrices."""
    sid = shared_id.strip()
    t = task.strip()
    if not sid or not t:
        raise SchemaError("shared_id and task required")
    fid = hashlib.sha256(
        canonical_dumps({"s": sid, "t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "factor_id": fid,
        "ok": True,
        "note": "mptp mptp_factor",
    }


def mptp_transfer(*, factor_id: str) -> dict[str, Any]:
    """Transfer via low-rank multiplicative update to a target task."""
    fid = factor_id.strip()
    if not fid:
        raise SchemaError("factor_id required")
    tid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "xfer_id": tid,
        "ok": True,
        "note": "mptp mptp_transfer",
    }


def mptp_score(*, xfer_id: str, score: int) -> dict[str, Any]:
    """Score transferred prompt on the target task (0–100)."""
    xid = xfer_id.strip()
    if not xid:
        raise SchemaError("xfer_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"x": xid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mptp mptp_score",
    }


def mptp_efficient(*, param_efficient: bool) -> dict[str, Any]:
    """Flag extreme parameter efficiency vs finetuning (report-only)."""
    return {
        "param_efficient": param_efficient,
        "apply": False,
        "ok": True,
        "note": "mptp mptp_efficient",
    }


def mptp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Shared → factor → transfer → score."""
    order = ("shared", "factor", "transfer", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "shared"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mptp mptp_loop_plan",
    }
