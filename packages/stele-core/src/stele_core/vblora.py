"""VB-LoRA proxies (stdlib; no LLM).

Shaped by VB-LoRA (arXiv:2405.15179 · NeurIPS 2024): global vector bank
with top-k admixture composites all LoRA matrices — extreme storage
compression. Proxies only.

Prefix ``vbl_*`` — not VeRA (``vra_*``) / LoRA-drop (``ldr_*``) / LoRA-XS.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def vbl_bank(*, task: str, size: int) -> dict[str, Any]:
    """Declare shared vector bank (size >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if size < 1:
        raise SchemaError("size must be >= 1")
    bid = hashlib.sha256(
        canonical_dumps({"t": t, "s": size}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "bank_id": bid,
        "size": size,
        "ok": True,
        "note": "vbl vbl_bank",
    }


def vbl_topk(*, bank_id: str, k: int) -> dict[str, Any]:
    """Top-k admixture over the vector bank (k >= 1)."""
    bid = bank_id.strip()
    if not bid:
        raise SchemaError("bank_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"b": bid, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "topk_id": tid,
        "k": k,
        "ok": True,
        "note": "vbl vbl_topk",
    }


def vbl_compose(*, topk_id: str) -> dict[str, Any]:
    """Compose LoRA matrices from bank vectors."""
    tid = topk_id.strip()
    if not tid:
        raise SchemaError("topk_id required")
    cid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compose_id": cid,
        "ok": True,
        "note": "vbl vbl_compose",
    }


def vbl_score(*, compose_id: str, score: int) -> dict[str, Any]:
    """Score VB-LoRA adaptation (0–100)."""
    cid = compose_id.strip()
    if not cid:
        raise SchemaError("compose_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"c": cid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "vbl vbl_score",
    }


def vbl_extreme(*, extreme_compression: bool) -> dict[str, Any]:
    """Flag extreme storage vs LoRA (report-only)."""
    return {
        "extreme_compression": extreme_compression,
        "apply": False,
        "ok": True,
        "note": "vbl vbl_extreme",
    }


def vbl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Bank → topk → compose → score."""
    order = ("bank", "topk", "compose", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "bank"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "vbl vbl_loop_plan",
    }
