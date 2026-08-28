"""MELoRA proxies (stdlib; no LLM).

Shaped by MELoRA (arXiv:2402.17263): stack mini-LoRAs in parallel as a
block-diagonal ensemble — higher effective rank without extra parameter
overhead vs LoRA. Proxies only.

Prefix ``meo_*`` — not MoELoRA (``mel_*``) / DeLoRA (``dlr_*``) /
MultiLoRA (``mlr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def meo_mini(*, task: str, n_minis: int, mini_rank: int) -> dict[str, Any]:
    """Allocate n mini-LoRAs (n_minis >= 1, mini_rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n_minis < 1 or mini_rank < 1:
        raise SchemaError("n_minis and mini_rank must be >= 1")
    mid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n_minis, "r": mini_rank}).encode(
            "utf-8"
        )
    ).hexdigest()[:12]
    return {
        "mini_id": mid,
        "n_minis": n_minis,
        "mini_rank": mini_rank,
        "ok": True,
        "note": "meo meo_mini",
    }


def meo_diag(*, mini_id: str) -> dict[str, Any]:
    """Assemble block-diagonal ensemble from mini-LoRAs."""
    mid = mini_id.strip()
    if not mid:
        raise SchemaError("mini_id required")
    did = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "diag_id": did,
        "ok": True,
        "note": "meo meo_diag",
    }


def meo_train(*, diag_id: str) -> dict[str, Any]:
    """Train MELoRA ensemble."""
    did = diag_id.strip()
    if not did:
        raise SchemaError("diag_id required")
    tid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "meo meo_train",
    }


def meo_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score MELoRA adaptation (0–100)."""
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
        "note": "meo meo_score",
    }


def meo_rank(*, higher_effective_rank: bool) -> dict[str, Any]:
    """Flag summed mini-rank effective rank (report-only)."""
    return {
        "higher_effective_rank": higher_effective_rank,
        "apply": False,
        "ok": True,
        "note": "meo meo_rank",
    }


def meo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Mini → diag → train → score."""
    order = ("mini", "diag", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "mini"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "meo meo_loop_plan",
    }
