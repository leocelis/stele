"""FourierFT proxies (stdlib; no LLM).

Shaped by FourierFT (arXiv:2405.03003): learn sparse spectral coefficients
on a Fourier basis and reconstruct ΔW via inverse DFT — extreme parameter
reduction without a low-rank factorization. Proxies only.

Prefix ``fft_*`` — not LoHa (``lha_*``) / LoRA / rsLoRA (``rsl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def fft_basis(*, task: str, n_coeff: int) -> dict[str, Any]:
    """Select Fourier basis / coefficient budget (n_coeff >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_coeff < 1:
        raise SchemaError("n_coeff must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_coeff}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "basis_id": bid,
        "n_coeff": n_coeff,
        "ok": True,
        "note": "fft fft_basis",
    }


def fft_coeff(*, basis_id: str) -> dict[str, Any]:
    """Learn sparse spectral coefficients."""
    bid = basis_id.strip()
    if not bid:
        raise SchemaError("basis_id required")
    cid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "coeff_id": cid,
        "ok": True,
        "note": "fft fft_coeff",
    }


def fft_idft(*, coeff_id: str) -> dict[str, Any]:
    """Reconstruct ΔW via inverse discrete Fourier transform."""
    cid = coeff_id.strip()
    if not cid:
        raise SchemaError("coeff_id required")
    iid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "idft_id": iid,
        "ok": True,
        "note": "fft fft_idft",
    }


def fft_score(*, idft_id: str, score: int) -> dict[str, Any]:
    """Score FourierFT adaptation (0–100)."""
    iid = idft_id.strip()
    if not iid:
        raise SchemaError("idft_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"i": iid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "fft fft_score",
    }


def fft_sparse(*, spectral_sparse: bool) -> dict[str, Any]:
    """Flag spectral sparsity / extreme param reduction (report-only)."""
    return {
        "spectral_sparse": spectral_sparse,
        "apply": False,
        "ok": True,
        "note": "fft fft_sparse",
    }


def fft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Basis → coeff → idft → score."""
    order = ("basis", "coeff", "idft", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "basis"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "fft fft_loop_plan",
    }
