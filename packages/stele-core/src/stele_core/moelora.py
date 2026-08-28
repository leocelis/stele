"""MoELoRA proxies (stdlib; no LLM).

Shaped by MoELoRA (arXiv:2402.12851): treat LoRA modules as MoE
experts with contrastive guidance so experts learn distinct features
and a gate activates task-relevant ones. Proxies only.

Prefix ``mel_*`` — not LoRAMoE (``lme_*``) / MiLoRA (``mil_*``) /
HydraLoRA (``hyd_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mel_experts(*, task: str, count: int) -> dict[str, Any]:
    """Declare LoRA experts for MoELoRA (count >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if count < 2:
        raise SchemaError("count must be >= 2")
    eid = hashlib.sha256(
        canonical_dumps({"t": t, "c": count}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experts_id": eid,
        "count": count,
        "ok": True,
        "note": "mel mel_experts",
    }


def mel_contrast(*, experts_id: str) -> dict[str, Any]:
    """Contrastive guidance so experts specialize."""
    eid = experts_id.strip()
    if not eid:
        raise SchemaError("experts_id required")
    cid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "contrast_id": cid,
        "ok": True,
        "note": "mel mel_contrast",
    }


def mel_gate(*, contrast_id: str) -> dict[str, Any]:
    """Gate / activate task-relevant LoRA experts."""
    cid = contrast_id.strip()
    if not cid:
        raise SchemaError("contrast_id required")
    gid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gate_id": gid,
        "ok": True,
        "note": "mel mel_gate",
    }


def mel_score(*, gate_id: str, score: int) -> dict[str, Any]:
    """Score MoELoRA adaptation (0–100)."""
    gid = gate_id.strip()
    if not gid:
        raise SchemaError("gate_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"g": gid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mel mel_score",
    }


def mel_sparse(*, sparse_activate: bool) -> dict[str, Any]:
    """Flag sparse expert activation (report-only)."""
    return {
        "sparse_activate": sparse_activate,
        "apply": False,
        "ok": True,
        "note": "mel mel_sparse",
    }


def mel_loop_plan(*, phase: str) -> dict[str, Any]:
    """Experts → contrast → gate → score."""
    order = ("experts", "contrast", "gate", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "experts"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mel mel_loop_plan",
    }
