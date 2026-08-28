"""DoRA proxies (stdlib; no LLM).

Shaped by DoRA (arXiv:2402.09353): decompose weight into magnitude + direction;
apply LoRA on the direction component. Proxies only.

Prefix ``dora_*`` — not BitFit (``bft_*``) / LoRA (``lora_*``) / dormant scan.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def dora_decompose(*, task: str) -> dict[str, Any]:
    """Decompose W into magnitude and direction for a task."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    did = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "decomp_id": did,
        "ok": True,
        "note": "dora dora_decompose",
    }


def dora_magnitude(*, decomp_id: str) -> dict[str, Any]:
    """Track / update magnitude component."""
    did = decomp_id.strip()
    if not did:
        raise SchemaError("decomp_id required")
    mid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mag_id": mid,
        "ok": True,
        "note": "dora dora_magnitude",
    }


def dora_direction(*, mag_id: str, rank: int) -> dict[str, Any]:
    """Apply low-rank update on the direction component (rank >= 1)."""
    mid = mag_id.strip()
    if not mid:
        raise SchemaError("mag_id required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"m": mid, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "dir_id": rid,
        "rank": rank,
        "ok": True,
        "note": "dora dora_direction",
    }


def dora_score(*, dir_id: str, score: int) -> dict[str, Any]:
    """Score DoRA adaptation (0–100)."""
    did = dir_id.strip()
    if not did:
        raise SchemaError("dir_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"d": did, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "dora dora_score",
    }


def dora_vs_lora(*, closes_gap: bool) -> dict[str, Any]:
    """Flag DoRA narrowing the LoRA↔full-FT gap (report-only)."""
    return {
        "closes_gap": closes_gap,
        "apply": False,
        "ok": True,
        "note": "dora dora_vs_lora",
    }


def dora_loop_plan(*, phase: str) -> dict[str, Any]:
    """Decompose → magnitude → direction → score."""
    order = ("decompose", "magnitude", "direction", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "decompose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "dora dora_loop_plan",
    }
