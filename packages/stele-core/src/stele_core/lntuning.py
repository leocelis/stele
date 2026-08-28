"""LN Tuning proxies (stdlib; no LLM).

Shaped by LN Tuning (arXiv:2312.11420): train attention LayerNorm
scales instead of full LoRA. Proxies only.

Prefix ``lnt_*`` — not LoRA-Null (``lnu_*``) / LoRA-TSD (``tsd_*``) /
ALoRA (``alo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lnt_attn(*, task: str) -> dict[str, Any]:
    """Select attention LayerNorms."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    aid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "attn_id": aid,
        "ok": True,
        "note": "lnt lnt_attn",
    }


def lnt_scale(*, attn_id: str) -> dict[str, Any]:
    """Train LN scale (gamma) only."""
    aid = attn_id.strip()
    if not aid:
        raise SchemaError("attn_id required")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "lnt lnt_scale",
    }


def lnt_train(*, scale_id: str) -> dict[str, Any]:
    """Run LN-only fine-tune."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lnt lnt_train",
    }


def lnt_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LN Tuning run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "lnt lnt_score",
    }


def lnt_cheap(*, cheaper_than_lora: bool) -> dict[str, Any]:
    """Flag cheaper than LoRA (report-only)."""
    return {
        "cheaper_than_lora": cheaper_than_lora,
        "apply": False,
        "ok": True,
        "note": "lnt lnt_cheap",
    }


def lnt_loop_plan(*, phase: str) -> dict[str, Any]:
    """Attn → scale → train → score."""
    order = ("attn", "scale", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "attn"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lnt lnt_loop_plan",
    }
