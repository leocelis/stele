"""SVFT proxies (stdlib; no LLM).

Shaped by SVFT (arXiv:2405.19597): weight-dependent PEFT — ΔW is a
sparse combination of W's own singular vectors; only coefficients
train. Proxies only.

Prefix ``svf_*`` — not LoRA.rar (``lrr_*``) / PiSSA / LoRA-XS (`lxs_*`).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def svf_svd(*, task: str, keep: int) -> dict[str, Any]:
    """Factor W into singular vectors (keep >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if keep < 1:
        raise SchemaError("keep must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "k": keep}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "svd_id": sid,
        "keep": keep,
        "ok": True,
        "note": "svf svf_svd",
    }


def svf_sparse(*, svd_id: str) -> dict[str, Any]:
    """Fix sparse coefficient pattern Ω."""
    sid = svd_id.strip()
    if not sid:
        raise SchemaError("svd_id required")
    pid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sparse_id": pid,
        "ok": True,
        "note": "svf svf_sparse",
    }


def svf_train(*, sparse_id: str) -> dict[str, Any]:
    """Train sparse singular-vector coefficients."""
    pid = sparse_id.strip()
    if not pid:
        raise SchemaError("sparse_id required")
    tid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "svf svf_train",
    }


def svf_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score SVFT adaptation (0–100)."""
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
        "note": "svf svf_score",
    }


def svf_geom(*, weight_dependent: bool) -> dict[str, Any]:
    """Flag weight-dependent ΔW geometry (report-only)."""
    return {
        "weight_dependent": weight_dependent,
        "apply": False,
        "ok": True,
        "note": "svf svf_geom",
    }


def svf_loop_plan(*, phase: str) -> dict[str, Any]:
    """Svd → sparse → train → score."""
    order = ("svd", "sparse", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "svd"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "svf svf_loop_plan",
    }
