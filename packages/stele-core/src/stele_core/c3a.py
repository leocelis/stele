"""C3A proxies (stdlib; no LLM).

Shaped by C3A (arXiv:2407.19342): circular-convolution kernels
(circulant ΔW via FFT) instead of BA. Proxies only.

Prefix ``c3a_*`` — not CaRA (``cra_*``) / CARE-LoRA (``car_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def c3a_kernel(*, task: str) -> dict[str, Any]:
    """Open the convolution kernel."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    kid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "kernel_id": kid,
        "ok": True,
        "note": "c3a c3a_kernel",
    }


def c3a_circ(*, kernel_id: str) -> dict[str, Any]:
    """Lift kernel to a circulant ΔW."""
    kid = kernel_id.strip()
    if not kid:
        raise SchemaError("kernel_id required")
    cid = hashlib.sha256(
        canonical_dumps({"k": kid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "circ_id": cid,
        "ok": True,
        "note": "c3a c3a_circ",
    }


def c3a_fft(*, circ_id: str) -> dict[str, Any]:
    """FFT-multiply the circulant."""
    cid = circ_id.strip()
    if not cid:
        raise SchemaError("circ_id required")
    fid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fft_id": fid,
        "ok": True,
        "note": "c3a c3a_fft",
    }


def c3a_score(*, fft_id: str, score: int) -> dict[str, Any]:
    """Score C3A run (0–100)."""
    fid = fft_id.strip()
    if not fid:
        raise SchemaError("fft_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "c3a c3a_score",
    }


def c3a_rank(*, high_rank: bool) -> dict[str, Any]:
    """Flag rank decoupled from param count (report-only)."""
    return {
        "high_rank": high_rank,
        "apply": False,
        "ok": True,
        "note": "c3a c3a_rank",
    }


def c3a_loop_plan(*, phase: str) -> dict[str, Any]:
    """Kernel → circ → fft → score."""
    order = ("kernel", "circ", "fft", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "kernel"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "c3a c3a_loop_plan",
    }
