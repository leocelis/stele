"""MultiLoRA proxies (stdlib; no LLM).

Shaped by MultiLoRA (arXiv:2311.11501): horizontally scale LoRA along
rank with learnable scales + init change to reduce top-singular
dominance for multi-task adaptation. Proxies only.

Prefix ``mlr_*`` — not LoraHub (``lhb_*``) / MoELoRA (``mel_*``) /
MiLoRA (``mil_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mlr_scale(*, task: str, shards: int) -> dict[str, Any]:
    """Horizontally shard LoRA along rank (shards >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if shards < 2:
        raise SchemaError("shards must be >= 2")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "s": shards}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "shards": shards,
        "ok": True,
        "note": "mlr mlr_scale",
    }


def mlr_init(*, scale_id: str) -> dict[str, Any]:
    """Re-init adaptation matrices to reduce singular dominance."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "init_id": iid,
        "ok": True,
        "note": "mlr mlr_init",
    }


def mlr_train(*, init_id: str) -> dict[str, Any]:
    """Train MultiLoRA on mixed multi-task data."""
    iid = init_id.strip()
    if not iid:
        raise SchemaError("init_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "mlr mlr_train",
    }


def mlr_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score MultiLoRA adaptation (0–100)."""
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
        "note": "mlr mlr_score",
    }


def mlr_demo(*, more_democratic: bool) -> dict[str, Any]:
    """Flag more democratic singular spectrum (report-only)."""
    return {
        "more_democratic": more_democratic,
        "apply": False,
        "ok": True,
        "note": "mlr mlr_demo",
    }


def mlr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Scale → init → train → score."""
    order = ("scale", "init", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "scale"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mlr mlr_loop_plan",
    }
