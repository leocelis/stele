"""(IA)^3 proxies (stdlib; no LLM).

Shaped by (IA)^3 (arXiv:2205.05638): Infused Adapter by Inhibiting and Amplifying
Inner Activations — learned vectors rescale activations; mixed-task batches OK.
Proxies only.

Prefix ``ia3_*`` — not Compacter (``cmp_*``) / LoRA (``lora_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ia3_vector(*, task: str) -> dict[str, Any]:
    """Allocate learned rescale vectors l_W for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    vid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "vector_id": vid,
        "ok": True,
        "note": "ia3 ia3_vector",
    }


def ia3_scale(*, vector_id: str) -> dict[str, Any]:
    """Element-wise rescale of inner activations (composition_mode=scale)."""
    vid = vector_id.strip()
    if not vid:
        raise SchemaError("vector_id required")
    sid = hashlib.sha256(
        canonical_dumps({"v": vid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "ia3 ia3_scale",
    }


def ia3_train(*, scale_id: str) -> dict[str, Any]:
    """Train only the (IA)^3 vectors; freeze base weights."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    tid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "ia3 ia3_train",
    }


def ia3_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score (IA)^3 few-shot adaptation (0–100)."""
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
        "note": "ia3 ia3_score",
    }


def ia3_mixed(*, mixed_batch: bool) -> dict[str, Any]:
    """Flag mixed-task batching support (report-only)."""
    return {
        "mixed_batch": mixed_batch,
        "apply": False,
        "ok": True,
        "note": "ia3 ia3_mixed",
    }


def ia3_loop_plan(*, phase: str) -> dict[str, Any]:
    """Vector → scale → train → score."""
    order = ("vector", "scale", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "vector"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ia3 ia3_loop_plan",
    }
