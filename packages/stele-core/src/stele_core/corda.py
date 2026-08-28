"""CorDA proxies (stdlib; no LLM).

Shaped by CorDA / CorDA++ (arXiv:2506.13187): context-oriented SVD on
W·covariance for task-aware init — KPM (freeze principal) or IPM
(adapt principal) modes. Proxies only.

Prefix ``cda_*`` — not PiSSA (``psa_*``) / MiLoRA (``mil_*``) / LoRA-Pro.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cda_cov(*, task: str) -> dict[str, Any]:
    """Declare task activation covariance for context-oriented SVD."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    cid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cov_id": cid,
        "ok": True,
        "note": "cda cda_cov",
    }


def cda_mode(*, cov_id: str, mode: str) -> dict[str, Any]:
    """Select KPM (preserve) or IPM (instruction preview) mode."""
    cid = cov_id.strip()
    if not cid:
        raise SchemaError("cov_id required")
    m = mode.strip().upper()
    if m not in ("KPM", "IPM"):
        raise SchemaError("mode must be KPM or IPM")
    mid = hashlib.sha256(
        canonical_dumps({"c": cid, "m": m}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mode_id": mid,
        "mode": m,
        "ok": True,
        "note": "cda cda_mode",
    }


def cda_adapt(*, mode_id: str) -> dict[str, Any]:
    """Run CorDA adaptation under selected mode."""
    mid = mode_id.strip()
    if not mid:
        raise SchemaError("mode_id required")
    aid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": aid,
        "ok": True,
        "note": "cda cda_adapt",
    }


def cda_score(*, adapt_id: str, score: int) -> dict[str, Any]:
    """Score CorDA adaptation (0–100)."""
    aid = adapt_id.strip()
    if not aid:
        raise SchemaError("adapt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "cda cda_score",
    }


def cda_forget(*, less_forgetting: bool) -> dict[str, Any]:
    """Flag less pretrained forgetting under KPM (report-only)."""
    return {
        "less_forgetting": less_forgetting,
        "apply": False,
        "ok": True,
        "note": "cda cda_forget",
    }


def cda_loop_plan(*, phase: str) -> dict[str, Any]:
    """Cov → mode → adapt → score."""
    order = ("cov", "mode", "adapt", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "cov"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cda cda_loop_plan",
    }
