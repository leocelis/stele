"""Hybrid PEFT proxies (stdlib; no LLM).

Shaped by Hybrid PEFT (arXiv:2507.18076): fuse LoRA-GA speed
with BOFT orthogonal stability via per-layer gradient-norm
weights. Proxies only.

Prefix ``hyb_*`` — not HiRA (``hir_*``) / HRA (``hra_*``) /
OFT (``oft_*``) / LoRA-GA (``lga_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hyb_lora(*, task: str) -> dict[str, Any]:
    """Open the LoRA-GA branch."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    lid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "lora_id": lid,
        "ok": True,
        "note": "hyb hyb_lora",
    }


def hyb_boft(*, lora_id: str) -> dict[str, Any]:
    """Open the BOFT orthogonal branch."""
    lid = lora_id.strip()
    if not lid:
        raise SchemaError("lora_id required")
    bid = hashlib.sha256(
        canonical_dumps({"l": lid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "boft_id": bid,
        "ok": True,
        "note": "hyb hyb_boft",
    }


def hyb_fuse(*, boft_id: str) -> dict[str, Any]:
    """Fuse LoRA-GA + BOFT by gradient-norm weights."""
    bid = boft_id.strip()
    if not bid:
        raise SchemaError("boft_id required")
    fid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fuse_id": fid,
        "ok": True,
        "note": "hyb hyb_fuse",
    }


def hyb_score(*, fuse_id: str, score: int) -> dict[str, Any]:
    """Score hybrid PEFT run (0–100)."""
    fid = fuse_id.strip()
    if not fid:
        raise SchemaError("fuse_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "hyb hyb_score",
    }


def hyb_stable(*, more_stable: bool) -> dict[str, Any]:
    """Flag hybrid stability vs LoRA-GA alone (report-only)."""
    return {
        "more_stable": more_stable,
        "apply": False,
        "ok": True,
        "note": "hyb hyb_stable",
    }


def hyb_loop_plan(*, phase: str) -> dict[str, Any]:
    """LoRA → boft → fuse → score."""
    order = ("lora", "boft", "fuse", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "lora"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hyb hyb_loop_plan",
    }
