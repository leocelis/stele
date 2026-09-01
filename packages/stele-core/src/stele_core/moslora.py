"""MoSLoRA proxies (stdlib; no LLM).

Shaped by MoSLoRA (arXiv:2406.11909): learnable mixer between A and B
fuses rank-1 subspaces more flexibly than identity LoRA. Proxies only.

Prefix ``msl_*`` — not MiSS (``mss_*``) / Soft Prompt Mixtures (``msp_*``) /
QPiSSA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def msl_split(*, task: str, rank: int) -> dict[str, Any]:
    """Declare LoRA A/B subspace split (rank >= 1)."""
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
        "note": "msl msl_split",
    }


def msl_mixer(*, split_id: str) -> dict[str, Any]:
    """Insert learnable mixer W between A and B."""
    sid = split_id.strip()
    if not sid:
        raise SchemaError("split_id required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mixer_id": mid,
        "ok": True,
        "note": "msl msl_mixer",
    }


def msl_train(*, mixer_id: str) -> dict[str, Any]:
    """Train MoSLoRA with joint mixer + adapters."""
    mid = mixer_id.strip()
    if not mid:
        raise SchemaError("mixer_id required")
    tid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "msl msl_train",
    }


def msl_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score MoSLoRA adaptation (0–100)."""
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
        "note": "msl msl_score",
    }


def msl_fuse(*, flexible_fuse: bool) -> dict[str, Any]:
    """Flag flexible subspace fusion (report-only)."""
    return {
        "flexible_fuse": flexible_fuse,
        "apply": False,
        "ok": True,
        "note": "msl msl_fuse",
    }


def msl_loop_plan(*, phase: str) -> dict[str, Any]:
    """Split → mixer → train → score."""
    order = ("split", "mixer", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "split"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "msl msl_loop_plan",
    }
