"""LoRA-GA proxies (stdlib; no LLM).

Shaped by LoRA-GA (arXiv:2407.05000 · NeurIPS 2024): initialize A,B via
SVD of sampled gradients so the low-rank update approximates full
fine-tuning gradients — faster convergence, same architecture. Proxies only.

Prefix ``lga_*`` — not LoRA-XS (``lxs_*``) / PiSSA (``psa_*``) / AdaLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lga_grad(*, task: str, samples: int) -> dict[str, Any]:
    """Sample gradients for gradient-approximation init (samples >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if samples < 1:
        raise SchemaError("samples must be >= 1")
    gid = hashlib.sha256(
        canonical_dumps({"t": t, "n": samples}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "grad_id": gid,
        "samples": samples,
        "ok": True,
        "note": "lga lga_grad",
    }


def lga_svd(*, grad_id: str) -> dict[str, Any]:
    """SVD on sampled gradients to seed A,B."""
    gid = grad_id.strip()
    if not gid:
        raise SchemaError("grad_id required")
    sid = hashlib.sha256(
        canonical_dumps({"g": gid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "svd_id": sid,
        "ok": True,
        "note": "lga lga_svd",
    }


def lga_scale(*, svd_id: str) -> dict[str, Any]:
    """Apply stable scale so init is rank/input invariant."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    scid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": scid,
        "ok": True,
        "note": "lga lga_scale",
    }


def lga_score(*, scale_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-GA adaptation (0–100)."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    scid = hashlib.sha256(
        canonical_dumps({"s": sid, "c": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": scid,
        "score": score,
        "ok": True,
        "note": "lga lga_score",
    }


def lga_fast(*, faster_convergence: bool) -> dict[str, Any]:
    """Flag faster convergence vs random LoRA init (report-only)."""
    return {
        "faster_convergence": faster_convergence,
        "apply": False,
        "ok": True,
        "note": "lga lga_fast",
    }


def lga_loop_plan(*, phase: str) -> dict[str, Any]:
    """Grad → svd → scale → score."""
    order = ("grad", "svd", "scale", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "grad"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lga lga_loop_plan",
    }
