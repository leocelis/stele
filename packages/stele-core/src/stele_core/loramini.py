"""LoRA-Mini proxies (stdlib; no LLM).

Shaped by LoRA-Mini (arXiv:2411.15804 · AAAI CoLoRAI 2025): split
each low-rank factor into four parts and train only the two inner
matrices — up to ~20× fewer trainable params vs LoRA. Proxies only.

Prefix ``lmi_*`` — not LoRA-XS (``lxs_*``) / QDyLoRA (``qdy_*``) /
MiLoRA (``mil_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lmi_split(*, task: str, rank: int) -> dict[str, Any]:
    """Split LoRA factors into four parts (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "split_id": sid,
        "rank": rank,
        "ok": True,
        "note": "lmi lmi_split",
    }


def lmi_inner(*, split_id: str) -> dict[str, Any]:
    """Mark only the two inner matrices as trainable."""
    sid = split_id.strip()
    if not sid:
        raise SchemaError("split_id required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "inner_id": iid,
        "ok": True,
        "note": "lmi lmi_inner",
    }


def lmi_train(*, inner_id: str) -> dict[str, Any]:
    """Train LoRA-Mini selective adapters."""
    iid = inner_id.strip()
    if not iid:
        raise SchemaError("inner_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lmi lmi_train",
    }


def lmi_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-Mini adaptation (0–100)."""
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
        "note": "lmi lmi_score",
    }


def lmi_tiny(*, extreme_compress: bool) -> dict[str, Any]:
    """Flag extreme trainable-param compression (report-only)."""
    return {
        "extreme_compress": extreme_compress,
        "apply": False,
        "ok": True,
        "note": "lmi lmi_tiny",
    }


def lmi_loop_plan(*, phase: str) -> dict[str, Any]:
    """Split → inner → train → score."""
    order = ("split", "inner", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "split"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lmi lmi_loop_plan",
    }
