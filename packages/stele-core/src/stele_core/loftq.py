"""LoftQ proxies (stdlib; no LLM).

Shaped by LoftQ (arXiv:2310.08659): alternate quantization and low-rank
approx so LoRA init closes the QLoRA discrepancy vs full precision.
Proxies only.

Prefix ``lfq_*`` — not QLoRA (``qlo_*``) / PiSSA (``psa_*``) / LoRA-Dash.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lfq_quant(*, task: str, bits: int) -> dict[str, Any]:
    """Declare quantization backbone (bits >= 2)."""
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
        "note": "lfq lfq_quant",
    }


def lfq_init(*, quant_id: str, rank: int) -> dict[str, Any]:
    """Find LoRA A/B init that approximates W − Q (rank >= 1)."""
    qid = quant_id.strip()
    if not qid:
        raise SchemaError("quant_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"q": qid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "rank": rank,
        "ok": True,
        "note": "lfq lfq_init",
    }


def lfq_train(*, init_id: str) -> dict[str, Any]:
    """Train LoRA from LoftQ initialization."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lfq lfq_train",
    }


def lfq_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoftQ adaptation (0–100)."""
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
        "note": "lfq lfq_score",
    }


def lfq_gap(*, closes_qlora_gap: bool) -> dict[str, Any]:
    """Flag closer to full-precision vs QLoRA (report-only)."""
    return {
        "closes_qlora_gap": closes_qlora_gap,
        "apply": False,
        "ok": True,
        "note": "lfq lfq_gap",
    }


def lfq_loop_plan(*, phase: str) -> dict[str, Any]:
    """Quant → init → train → score."""
    order = ("quant", "init", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "quant"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lfq lfq_loop_plan",
    }
