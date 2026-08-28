"""Multimodal-CoT proxies (stdlib; no LLM / no vision).

Shaped by Multimodal-CoT (arXiv:2302.00923): fuse text+vision,
generate rationale, then answer inference. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mmcot_fuse(*, text: str, vision_ref: str) -> dict[str, Any]:
    """Fuse language and vision modality refs (proxy ids)."""
    t = text.strip()
    v = vision_ref.strip()
    if not t or not v:
        raise SchemaError("text and vision_ref required")
    fid = hashlib.sha256(
        canonical_dumps({"t": t, "v": v}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fuse_id": fid,
        "ok": True,
        "note": "mmcot mmcot_fuse",
    }


def mmcot_rationale(*, fuse_id: str) -> dict[str, Any]:
    """Stage 1: generate multimodal rationale."""
    fid = fuse_id.strip()
    if not fid:
        raise SchemaError("fuse_id required")
    rid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "rationale_id": rid,
        "ok": True,
        "note": "mmcot mmcot_rationale",
    }


def mmcot_infer(*, rationale_id: str) -> dict[str, Any]:
    """Stage 2: answer inference from rationale."""
    rid = rationale_id.strip()
    if not rid:
        raise SchemaError("rationale_id required")
    aid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": aid,
        "ok": True,
        "note": "mmcot mmcot_infer",
    }


def mmcot_hallucination(*, mitigated: bool) -> dict[str, Any]:
    """Flag hallucination mitigation from multimodal rationales."""
    return {
        "mitigated": mitigated,
        "ok": True,
        "note": "mmcot mmcot_hallucination",
    }


def mmcot_separate(*, two_stage: bool) -> dict[str, Any]:
    """Flag rationale/answer separation (report-only)."""
    return {
        "two_stage": two_stage,
        "apply": False,
        "ok": True,
        "note": "mmcot mmcot_separate",
    }


def mmcot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Fuse → rationale → infer → flag."""
    order = ("fuse", "rationale", "infer", "flag")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "fuse"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mmcot mmcot_loop_plan",
    }
