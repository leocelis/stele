"""LoRA-Null proxies (stdlib; no LLM).

Shaped by LoRA-Null (arXiv:2503.02659): initialize adapters in the
null space of pre-trained *activations* (not weights) to preserve
world knowledge while fine-tuning. Proxies only.

Prefix ``lnu_*`` — not LoRA-Init (``lin_*``) / MiLoRA (``mil_*``) /
OLoRA (``olr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lnu_act(*, task: str, samples: int) -> dict[str, Any]:
    """Sample pretrain-representative activations (samples >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if samples < 1:
        raise SchemaError("samples must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"t": t, "n": samples}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "act_id": aid,
        "samples": samples,
        "ok": True,
        "note": "lnu lnu_act",
    }


def lnu_null(*, act_id: str) -> dict[str, Any]:
    """Extract activation null space for LoRA init."""
    aid = act_id.strip()
    if not aid:
        raise SchemaError("act_id required")
    nid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "null_id": nid,
        "ok": True,
        "note": "lnu lnu_null",
    }


def lnu_train(*, null_id: str) -> dict[str, Any]:
    """Train LoRA initialized in activation null space."""
    nid = null_id.strip()
    if not nid:
        raise SchemaError("null_id required")
    tid = hashlib.sha256(
        canonical_dumps({"n": nid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lnu lnu_train",
    }


def lnu_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Null adaptation (0–100)."""
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
        "note": "lnu lnu_score",
    }


def lnu_forget(*, preserves_knowledge: bool) -> dict[str, Any]:
    """Flag reduced catastrophic forgetting (report-only)."""
    return {
        "preserves_knowledge": preserves_knowledge,
        "apply": False,
        "ok": True,
        "note": "lnu lnu_forget",
    }


def lnu_loop_plan(*, phase: str) -> dict[str, Any]:
    """Act → null → train → score."""
    order = ("act", "null", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "act"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lnu lnu_loop_plan",
    }
