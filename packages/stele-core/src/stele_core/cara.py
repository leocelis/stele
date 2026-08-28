"""CaRA proxies (stdlib; no LLM).

Shaped by CaRA (ICML 2025, OpenReview:vexHifrbJg; no arXiv after
live fetch): split ViT into MHA + FFN tensors, then CP-decompose
each. Proxies only.

Prefix ``cra_*`` — not CARE-LoRA (``car_*``) / FacT (``fct_*``) /
LoRETTA (``ltt_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cra_mha(*, task: str) -> dict[str, Any]:
    """Stack Q/K/V across blocks into the MHA tensor."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    mid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mha_id": mid,
        "ok": True,
        "note": "cra cra_mha",
    }


def cra_ffn(*, mha_id: str) -> dict[str, Any]:
    """Stack O/up/down into the FFN tensor."""
    mid = mha_id.strip()
    if not mid:
        raise SchemaError("mha_id required")
    fid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ffn_id": fid,
        "ok": True,
        "note": "cra cra_ffn",
    }


def cra_cpd(*, ffn_id: str) -> dict[str, Any]:
    """CP-decompose both tensors."""
    fid = ffn_id.strip()
    if not fid:
        raise SchemaError("ffn_id required")
    cid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cpd_id": cid,
        "ok": True,
        "note": "cra cra_cpd",
    }


def cra_score(*, cpd_id: str, score: int) -> dict[str, Any]:
    """Score CaRA run (0–100)."""
    cid = cpd_id.strip()
    if not cid:
        raise SchemaError("cpd_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"c": cid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "cra cra_score",
    }


def cra_heads(*, head_mode: bool) -> dict[str, Any]:
    """Flag explicit head-mode CP (report-only)."""
    return {
        "head_mode": head_mode,
        "apply": False,
        "ok": True,
        "note": "cra cra_heads",
    }


def cra_loop_plan(*, phase: str) -> dict[str, Any]:
    """MHA → ffn → cpd → score."""
    order = ("mha", "ffn", "cpd", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "mha"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cra cra_loop_plan",
    }
