"""SDT proxies (stdlib; no LLM).

Shaped by *Parameter-Efficient Fine-Tuning of State Space Models*
(arXiv:2410.09016): Sparse Dimension Tuning (SDT) for SSM modules,
paired with LoRA on linear projections. Proxies only.

Prefix ``sdt_*`` — unused at ship time (grep CLI + ops + modules).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sdt_dim(*, task: str) -> dict[str, Any]:
    """Open a sparse SSM dimension slot."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    did = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dim_id": did,
        "ok": True,
        "note": "sdt sdt_dim",
    }


def sdt_mask(*, dim_id: str) -> dict[str, Any]:
    """Build a sparse mask over SSM dimensions."""
    did = dim_id.strip()
    if not did:
        raise SchemaError("dim_id required")
    mid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mask_id": mid,
        "ok": True,
        "note": "sdt sdt_mask",
    }


def sdt_tune(*, mask_id: str) -> dict[str, Any]:
    """Apply sparse dimension tune on the masked slots."""
    mid = mask_id.strip()
    if not mid:
        raise SchemaError("mask_id required")
    tid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tune_id": tid,
        "ok": True,
        "note": "sdt sdt_tune",
    }


def sdt_score(*, tune_id: str, score: int) -> dict[str, Any]:
    """Score SDT run (0–100)."""
    tid = tune_id.strip()
    if not tid:
        raise SchemaError("tune_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "sdt sdt_score",
    }


def sdt_ssm(*, ssm_only: bool) -> dict[str, Any]:
    """Flag SSM-targeted SDT (vs LoRA-on-projections) — report-only."""
    return {
        "ssm_only": ssm_only,
        "apply": False,
        "ok": True,
        "note": "sdt sdt_ssm",
    }


def sdt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Dim → mask → tune → score."""
    order = ("dim", "mask", "tune", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "dim"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "sdt sdt_loop_plan",
    }
