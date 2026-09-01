"""FacT proxies (stdlib; no LLM).

Shaped by FacT (arXiv:2212.03145): stack ViT increments into one
3D tensor, then Tensor-Train or Tucker factors. Proxies only.

Prefix ``fct_*`` — not LoTR (``ltr_*``) / TensLoRA (``tnl_*``) /
LoRTA (``lrt_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def fct_tensor(*, task: str) -> dict[str, Any]:
    """Stack layer increments into one 3D tensor."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tensor_id": tid,
        "ok": True,
        "note": "fct fct_tensor",
    }


def fct_tt(*, tensor_id: str) -> dict[str, Any]:
    """Tensor-Train factor the increment tensor."""
    tid = tensor_id.strip()
    if not tid:
        raise SchemaError("tensor_id required")
    fid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tt_id": fid,
        "ok": True,
        "note": "fct fct_tt",
    }


def fct_tucker(*, tt_id: str) -> dict[str, Any]:
    """Tucker factor as the FacT-TK variant."""
    fid = tt_id.strip()
    if not fid:
        raise SchemaError("tt_id required")
    kid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tucker_id": kid,
        "ok": True,
        "note": "fct fct_tucker",
    }


def fct_score(*, tucker_id: str, score: int) -> dict[str, Any]:
    """Score FacT run (0–100)."""
    kid = tucker_id.strip()
    if not kid:
        raise SchemaError("tucker_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"k": kid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "fct fct_score",
    }


def fct_tiny(*, tiny_params: bool) -> dict[str, Any]:
    """Flag ~8K-param FacT-TT (report-only)."""
    return {
        "tiny_params": tiny_params,
        "apply": False,
        "ok": True,
        "note": "fct fct_tiny",
    }


def fct_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tensor → tt → tucker → score."""
    order = ("tensor", "tt", "tucker", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tensor"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "fct fct_loop_plan",
    }
