"""MoRA proxies (stdlib; no LLM).

Shaped by MoRA (arXiv:2405.12130): square matrix M plus non-parameter
compress/decompress ops to maximize rank(ΔW) at the same parameter budget
as LoRA — better for knowledge-heavy fine-tuning. Proxies only.

Prefix ``mor_*`` — not MemoRAG (``memorag_*``) / LoRA-GA (``lga_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mor_square(*, task: str, side: int) -> dict[str, Any]:
    """Allocate square high-rank matrix M (side >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if side < 1:
        raise SchemaError("side must be >= 1")
    mid = hashlib.sha256(
        canonical_dumps({"t": t, "s": side}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "square_id": mid,
        "side": side,
        "ok": True,
        "note": "mor mor_square",
    }


def mor_compress(*, square_id: str) -> dict[str, Any]:
    """Non-parameter operator: compress input dim into M."""
    sid = square_id.strip()
    if not sid:
        raise SchemaError("square_id required")
    cid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compress_id": cid,
        "ok": True,
        "note": "mor mor_compress",
    }


def mor_expand(*, compress_id: str) -> dict[str, Any]:
    """Non-parameter operator: expand M output back to hidden dim."""
    cid = compress_id.strip()
    if not cid:
        raise SchemaError("compress_id required")
    eid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "expand_id": eid,
        "ok": True,
        "note": "mor mor_expand",
    }


def mor_score(*, expand_id: str, score: int) -> dict[str, Any]:
    """Score MoRA adaptation (0–100)."""
    eid = expand_id.strip()
    if not eid:
        raise SchemaError("expand_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"e": eid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "mor mor_score",
    }


def mor_merge(*, mergeable: bool) -> dict[str, Any]:
    """Flag that M+ops can merge into ΔW like LoRA (report-only)."""
    return {
        "mergeable": mergeable,
        "apply": False,
        "ok": True,
        "note": "mor mor_merge",
    }


def mor_loop_plan(*, phase: str) -> dict[str, Any]:
    """Square → compress → expand → score."""
    order = ("square", "compress", "expand", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "square"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mor mor_loop_plan",
    }
