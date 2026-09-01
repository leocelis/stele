"""LoRA-XS proxies (stdlib; no LLM).

Shaped by LoRA-XS (arXiv:2405.17604): freeze SVD-init A,B; train only an
r×r matrix R between them — extreme parameter efficiency. Proxies only.

Prefix ``lxs_*`` — not AsymmetryLoRA (``asy_*``) / LoRA-FA (``lfa_*``) / VeRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lxs_svd(*, task: str, rank: int) -> dict[str, Any]:
    """SVD-init frozen A,B from pretrained W (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "svd_id": sid,
        "rank": rank,
        "ok": True,
        "note": "lxs lxs_svd",
    }


def lxs_r(*, svd_id: str) -> dict[str, Any]:
    """Allocate the trainable r×r latent matrix R."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    rid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "r_id": rid,
        "ok": True,
        "note": "lxs lxs_r",
    }


def lxs_train(*, r_id: str) -> dict[str, Any]:
    """Train only R; keep A,B frozen."""
    rid = r_id.strip()
    if not rid:
        raise SchemaError("r_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lxs lxs_train",
    }


def lxs_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-XS adaptation (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lxs lxs_score",
    }


def lxs_tiny(*, r_squared_only: bool) -> dict[str, Any]:
    """Flag r²-only trainable footprint (report-only)."""
    return {
        "r_squared_only": r_squared_only,
        "apply": False,
        "ok": True,
        "note": "lxs lxs_tiny",
    }


def lxs_loop_plan(*, phase: str) -> dict[str, Any]:
    """SVD → r → train → score."""
    order = ("svd", "r", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "svd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lxs lxs_loop_plan",
    }
