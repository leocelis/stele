"""QPiSSA proxies (stdlib; no LLM).

Shaped by QPiSSA (PiSSA + 4-bit quantization; arXiv:2404.02948):
principal-component adapters on a quantized backbone with smaller
quantization error than QLoRA. Proxies only.

Prefix ``qps_*`` — not PiSSA (``psa_*``) / QLoRA (``qlo_*``) / LoftQ.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qps_quant(*, task: str, bits: int) -> dict[str, Any]:
    """Declare quantized backbone for QPiSSA (bits >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if bits < 2:
        raise SchemaError("bits must be >= 2")
    qid = hashlib.sha256(
        canonical_dumps({"t": t, "b": bits}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "quant_id": qid,
        "bits": bits,
        "ok": True,
        "note": "qps qps_quant",
    }


def qps_principal(*, quant_id: str, rank: int) -> dict[str, Any]:
    """Init principal singular adapters on quantized W (rank >= 1)."""
    qid = quant_id.strip()
    if not qid:
        raise SchemaError("quant_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"q": qid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "principal_id": pid,
        "rank": rank,
        "ok": True,
        "note": "qps qps_principal",
    }


def qps_train(*, principal_id: str) -> dict[str, Any]:
    """Train QPiSSA adapters."""
    pid = principal_id.strip()
    if not pid:
        raise SchemaError("principal_id required")
    tid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "qps qps_train",
    }


def qps_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score QPiSSA adaptation (0–100)."""
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
        "note": "qps qps_score",
    }


def qps_error(*, smaller_than_qlora: bool) -> dict[str, Any]:
    """Flag smaller quantization error vs QLoRA (report-only)."""
    return {
        "smaller_than_qlora": smaller_than_qlora,
        "apply": False,
        "ok": True,
        "note": "qps qps_error",
    }


def qps_loop_plan(*, phase: str) -> dict[str, Any]:
    """Quant → principal → train → score."""
    order = ("quant", "principal", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "quant"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qps qps_loop_plan",
    }
