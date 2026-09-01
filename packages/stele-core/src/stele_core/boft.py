"""BOFT proxies (stdlib; no LLM).

Shaped by BOFT (arXiv:2311.06243): butterfly-factorized orthogonal
finetuning. Proxies only.

Prefix ``bof_*`` — not BitFit (``bft_*``) / OFT (``oft_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def bof_block(*, task: str) -> dict[str, Any]:
    """Open a butterfly block."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    bid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "block_id": bid,
        "ok": True,
        "note": "bof bof_block",
    }


def bof_orth(*, block_id: str) -> dict[str, Any]:
    """Orthogonal factor on the block."""
    bid = block_id.strip()
    if not bid:
        raise SchemaError("block_id required")
    oid = hashlib.sha256(
        canonical_dumps({"b": bid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "orth_id": oid,
        "ok": True,
        "note": "bof bof_orth",
    }


def bof_butter(*, orth_id: str) -> dict[str, Any]:
    """Butterfly factorization of the orthogonal."""
    oid = orth_id.strip()
    if not oid:
        raise SchemaError("orth_id required")
    fid = hashlib.sha256(
        canonical_dumps({"o": oid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "butter_id": fid,
        "ok": True,
        "note": "bof bof_butter",
    }


def bof_score(*, butter_id: str, score: int) -> dict[str, Any]:
    """Score BOFT run (0–100)."""
    fid = butter_id.strip()
    if not fid:
        raise SchemaError("butter_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"b": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "bof bof_score",
    }


def bof_full(*, full_rank: bool) -> dict[str, Any]:
    """Flag OFT-as-special-case / full orthogonal (report-only)."""
    return {
        "full_rank": full_rank,
        "apply": False,
        "ok": True,
        "note": "bof bof_full",
    }


def bof_loop_plan(*, phase: str) -> dict[str, Any]:
    """Block → orth → butter → score."""
    order = ("block", "orth", "butter", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "block"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "bof bof_loop_plan",
    }
