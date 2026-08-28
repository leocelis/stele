"""AsymmetryLoRA proxies (stdlib; no LLM).

Shaped by Asymmetry in Low-Rank Adapters (arXiv:2402.16842): A extracts
features, B maps to output — train B; freeze random orthogonal A.
Proxies only.

Prefix ``asy_*`` — not LoRA-XS (``lxs_*``) / LoRA-FA (``lfa_*``) / LoRA+.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def asy_role(*, task: str) -> dict[str, Any]:
    """Declare asymmetric roles: A=feature extract, B=output map."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    rid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "role_id": rid,
        "ok": True,
        "note": "asy asy_role",
    }


def asy_freeze_a(*, role_id: str) -> dict[str, Any]:
    """Freeze A as a random orthogonal matrix."""
    rid = role_id.strip()
    if not rid:
        raise SchemaError("role_id required")
    aid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "a_id": aid,
        "ok": True,
        "note": "asy asy_freeze_a",
    }


def asy_train_b(*, a_id: str) -> dict[str, Any]:
    """Train B only — the more effective half of BA."""
    aid = a_id.strip()
    if not aid:
        raise SchemaError("a_id required")
    bid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": bid,
        "ok": True,
        "note": "asy asy_train_b",
    }


def asy_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score AsymmetryLoRA adaptation (0–100)."""
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
        "note": "asy asy_score",
    }


def asy_bound(*, tighter_bound: bool) -> dict[str, Any]:
    """Flag tighter generalization bound from training B only (report-only)."""
    return {
        "tighter_bound": tighter_bound,
        "apply": False,
        "ok": True,
        "note": "asy asy_bound",
    }


def asy_loop_plan(*, phase: str) -> dict[str, Any]:
    """Role → freeze_a → train_b → score."""
    order = ("role", "freeze_a", "train_b", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "role"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "asy asy_loop_plan",
    }
