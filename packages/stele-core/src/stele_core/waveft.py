"""WaveFT proxies (stdlib; no LLM).

Shaped by WaveFT (arXiv:2505.12532): learn sparse updates in the wavelet
domain of ΔW, then IDWT back — fine-grained parameter budgets below
LoRA's minimum rank. Proxies only.

Prefix ``wft_*`` — not FourierFT (``fft_*``) / SHiRA (``shr_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def wft_wave(*, task: str, n_coeff: int) -> dict[str, Any]:
    """Select wavelet basis / sparse coeff budget (n_coeff >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_coeff < 1:
        raise SchemaError("n_coeff must be >= 1")
    wid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_coeff}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "wave_id": wid,
        "n_coeff": n_coeff,
        "ok": True,
        "note": "wft wft_wave",
    }


def wft_sparse(*, wave_id: str) -> dict[str, Any]:
    """Learn sparse wavelet-domain coefficients."""
    wid = wave_id.strip()
    if not wid:
        raise SchemaError("wave_id required")
    sid = hashlib.sha256(
        canonical_dumps({"w": wid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sparse_id": sid,
        "ok": True,
        "note": "wft wft_sparse",
    }


def wft_idwt(*, sparse_id: str) -> dict[str, Any]:
    """Inverse discrete wavelet transform → weight-domain ΔW."""
    sid = sparse_id.strip()
    if not sid:
        raise SchemaError("sparse_id required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "idwt_id": iid,
        "ok": True,
        "note": "wft wft_idwt",
    }


def wft_score(*, idwt_id: str, score: int) -> dict[str, Any]:
    """Score WaveFT adaptation (0–100)."""
    iid = idwt_id.strip()
    if not iid:
        raise SchemaError("idwt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"i": iid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "wft wft_score",
    }


def wft_granular(*, below_lora_min: bool) -> dict[str, Any]:
    """Flag finer budget than LoRA min-rank (report-only)."""
    return {
        "below_lora_min": below_lora_min,
        "apply": False,
        "ok": True,
        "note": "wft wft_granular",
    }


def wft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Wave → sparse → idwt → score."""
    order = ("wave", "sparse", "idwt", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "wave"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "wft wft_loop_plan",
    }
