"""ETHER proxies (stdlib; no LLM).

Shaped by ETHER (arXiv:2405.20271): hyperplane-reflection PEFT —
extremely parameter-efficient orthogonal-style updates with strong
learning-rate robustness (ETHER / ETHER+). Proxies only.

Prefix ``eth_*`` — not ReLoRA (``rlr_*``) / VeRA / OFT / DeLoRA (``dlr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def eth_plane(*, task: str, reflections: int) -> dict[str, Any]:
    """Allocate hyperplane reflections (reflections >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if reflections < 1:
        raise SchemaError("reflections must be >= 1")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "r": reflections}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "plane_id": pid,
        "reflections": reflections,
        "ok": True,
        "note": "eth eth_plane",
    }


def eth_reflect(*, plane_id: str) -> dict[str, Any]:
    """Apply reflection-based weight transform."""
    pid = plane_id.strip()
    if not pid:
        raise SchemaError("plane_id required")
    rid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reflect_id": rid,
        "ok": True,
        "note": "eth eth_reflect",
    }


def eth_train(*, reflect_id: str) -> dict[str, Any]:
    """Train ETHER adapters."""
    rid = reflect_id.strip()
    if not rid:
        raise SchemaError("reflect_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "eth eth_train",
    }


def eth_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score ETHER adaptation (0–100)."""
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
        "note": "eth eth_score",
    }


def eth_plus(*, ether_plus: bool) -> dict[str, Any]:
    """Flag ETHER+ extended reflection variant (report-only)."""
    return {
        "ether_plus": ether_plus,
        "apply": False,
        "ok": True,
        "note": "eth eth_plus",
    }


def eth_loop_plan(*, phase: str) -> dict[str, Any]:
    """Plane → reflect → train → score."""
    order = ("plane", "reflect", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "plane"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "eth eth_loop_plan",
    }
