"""TeRA proxies (stdlib; no LLM).

Shaped by TeRA (arXiv:2509.03234): Tucker-like tensor net with
frozen random factors; only tiny per-layer scale vectors train,
so high-rank updates stay cheap. Proxies only.

Prefix ``ter_*`` — not LoRTA (``lrt_*``) / Tied-LoRA (``tld_*``) /
VeRA (``ver_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ter_tucker(*, task: str, order: int) -> dict[str, Any]:
    """Tensorize ΔW (order >= 3)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if order < 3:
        raise SchemaError("order must be >= 3")
    tid = hashlib.sha256(
        canonical_dumps({"t": t, "o": order}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "tucker_id": tid,
        "order": order,
        "ok": True,
        "note": "ter ter_tucker",
    }


def ter_freeze(*, tucker_id: str) -> dict[str, Any]:
    """Freeze shared random factors."""
    tid = tucker_id.strip()
    if not tid:
        raise SchemaError("tucker_id required")
    fid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "freeze_id": fid,
        "ok": True,
        "note": "ter ter_freeze",
    }


def ter_scale(*, freeze_id: str) -> dict[str, Any]:
    """Train per-layer diagonal scale vectors."""
    fid = freeze_id.strip()
    if not fid:
        raise SchemaError("freeze_id required")
    sid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "ter ter_scale",
    }


def ter_score(*, scale_id: str, score: int) -> dict[str, Any]:
    """Score TeRA run (0–100)."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"s": sid, "n": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "ter ter_score",
    }


def ter_highrank(*, high_rank_cheap: bool) -> dict[str, Any]:
    """Flag high-rank updates at vector cost (report-only)."""
    return {
        "high_rank_cheap": high_rank_cheap,
        "apply": False,
        "ok": True,
        "note": "ter ter_highrank",
    }


def ter_loop_plan(*, phase: str) -> dict[str, Any]:
    """Tucker → freeze → scale → score."""
    order = ("tucker", "freeze", "scale", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "tucker"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ter ter_loop_plan",
    }
