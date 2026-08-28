"""SHiRA proxies (stdlib; no LLM).

Shaped by SHiRA (arXiv:2406.13175 · NeurIPS 2024): sparse high-rank
adapters — tune ~1–2% of base weights via a sparse mask; rapid fused
switching and lower multi-adapter concept loss. Proxies only.

Prefix ``shr_*`` — not Soft Prompt Mixtures (``msp_*``) / WaveFT (``wft_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def shr_mask(*, task: str, pct: int) -> dict[str, Any]:
    """Declare sparse weight mask (pct 1–100, typically 1–2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if pct < 1 or pct > 100:
        raise SchemaError("pct must be 1..100")
    mid = hashlib.sha256(
        canonical_dumps({"t": t, "p": pct}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mask_id": mid,
        "pct": pct,
        "ok": True,
        "note": "shr shr_mask",
    }


def shr_tune(*, mask_id: str) -> dict[str, Any]:
    """Tune only the masked base weights (high-rank sparse)."""
    mid = mask_id.strip()
    if not mid:
        raise SchemaError("mask_id required")
    tid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tune_id": tid,
        "ok": True,
        "note": "shr shr_tune",
    }


def shr_switch(*, tune_id: str) -> dict[str, Any]:
    """Rapid fused-mode adapter switch."""
    tid = tune_id.strip()
    if not tid:
        raise SchemaError("tune_id required")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "switch_id": sid,
        "ok": True,
        "note": "shr shr_switch",
    }


def shr_score(*, switch_id: str, score: int) -> dict[str, Any]:
    """Score SHiRA adaptation (0–100)."""
    sid = switch_id.strip()
    if not sid:
        raise SchemaError("switch_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    scid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": scid,
        "score": score,
        "ok": True,
        "note": "shr shr_score",
    }


def shr_fusion(*, less_concept_loss: bool) -> dict[str, Any]:
    """Flag reduced multi-adapter concept loss (report-only)."""
    return {
        "less_concept_loss": less_concept_loss,
        "apply": False,
        "ok": True,
        "note": "shr shr_fusion",
    }


def shr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Mask → tune → switch → score."""
    order = ("mask", "tune", "switch", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "mask"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "shr shr_loop_plan",
    }
