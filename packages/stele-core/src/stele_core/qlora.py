"""QLoRA proxies (stdlib; no LLM).

Shaped by QLoRA (arXiv:2305.14314): freeze 4-bit NF4 base; train LoRA;
double quantization + paged optimizers for memory. Proxies only.

Prefix ``qlo_*`` — not AdaLoRA (``adl_*``) / LoRA (``lora_*``) / DoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qlo_quantize(*, bits: int) -> dict[str, Any]:
    """Quantize frozen base to N-bit (typically 4 / NF4)."""
    if bits < 1 or bits > 16:
        raise SchemaError("bits must be 1..16")
    qid = hashlib.sha256(
        canonical_dumps({"b": bits}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "quant_id": qid,
        "bits": bits,
        "ok": True,
        "note": "qlo qlo_quantize",
    }


def qlo_nf4(*, quant_id: str) -> dict[str, Any]:
    """Flag NF4 NormalFloat dtype for normally distributed weights."""
    qid = quant_id.strip()
    if not qid:
        raise SchemaError("quant_id required")
    nid = hashlib.sha256(
        canonical_dumps({"q": qid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "nf4_id": nid,
        "ok": True,
        "note": "qlo qlo_nf4",
    }


def qlo_adapter(*, nf4_id: str, rank: int) -> dict[str, Any]:
    """Attach LoRA adapters on the frozen quantized base (rank >= 1)."""
    nid = nf4_id.strip()
    if not nid:
        raise SchemaError("nf4_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"n": nid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapter_id": aid,
        "rank": rank,
        "ok": True,
        "note": "qlo qlo_adapter",
    }


def qlo_score(*, adapter_id: str, score: int) -> dict[str, Any]:
    """Score QLoRA finetune vs 16-bit FT recovery (0–100)."""
    aid = adapter_id.strip()
    if not aid:
        raise SchemaError("adapter_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "qlo qlo_score",
    }


def qlo_memory(*, double_quant: bool) -> dict[str, Any]:
    """Flag double quantization / paged-optimizer memory path (report-only)."""
    return {
        "double_quant": double_quant,
        "apply": False,
        "ok": True,
        "note": "qlo qlo_memory",
    }


def qlo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Quantize → nf4 → adapter → score."""
    order = ("quantize", "nf4", "adapter", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "quantize"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qlo qlo_loop_plan",
    }
