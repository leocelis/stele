"""QDyLoRA proxies (stdlib; no LLM).

Shaped by QDyLoRA (arXiv:2402.10462): DyLoRA nested ranks plus
QLoRA-style 4-bit quantization — one fine-tune covers a rank range
under low memory. Proxies only.

Prefix ``qdy_*`` — not QLoRA (``qlo_*``) / DyLoRA (``dyl_*``) /
LoRA-Mini (``lmi_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qdy_range(*, task: str, r_min: int, r_max: int) -> dict[str, Any]:
    """Declare nested rank range (1 <= r_min <= r_max)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if r_min < 1 or r_max < r_min:
        raise SchemaError("need 1 <= r_min <= r_max")
    rid = hashlib.sha256(
        canonical_dumps({"t": t, "a": r_min, "b": r_max}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "range_id": rid,
        "r_min": r_min,
        "r_max": r_max,
        "ok": True,
        "note": "qdy qdy_range",
    }


def qdy_quant(*, range_id: str, bits: int) -> dict[str, Any]:
    """Apply NF4-style quantization (bits in {4, 8})."""
    rid = range_id.strip()
    if not rid:
        raise SchemaError("range_id required")
    if bits not in (4, 8):
        raise SchemaError("bits must be 4 or 8")
    qid = hashlib.sha256(
        canonical_dumps({"r": rid, "b": bits}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "quant_id": qid,
        "bits": bits,
        "ok": True,
        "note": "qdy qdy_quant",
    }


def qdy_train(*, quant_id: str) -> dict[str, Any]:
    """One-shot train across the nested rank spectrum."""
    qid = quant_id.strip()
    if not qid:
        raise SchemaError("quant_id required")
    tid = hashlib.sha256(
        canonical_dumps({"q": qid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "qdy qdy_train",
    }


def qdy_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score QDyLoRA adaptation (0–100)."""
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
        "note": "qdy qdy_score",
    }


def qdy_pick(*, pick_rank_at_infer: bool) -> dict[str, Any]:
    """Flag pick optimal nested rank at inference (report-only)."""
    return {
        "pick_rank_at_infer": pick_rank_at_infer,
        "apply": False,
        "ok": True,
        "note": "qdy qdy_pick",
    }


def qdy_loop_plan(*, phase: str) -> dict[str, Any]:
    """Range → quant → train → score."""
    order = ("range", "quant", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "range"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "qdy qdy_loop_plan",
    }
