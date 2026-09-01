"""ABBA proxies (stdlib; no LLM).

Shaped by ABBA-Adapters (arXiv:2505.14238): Hadamard of two learned
low-rank factors — high effective rank without tying to W0. Proxies
only.

Prefix ``abb_*`` — not LoHA (``lha_*``) / HiRA / RoSA (``ros_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def abb_left(*, task: str, rank: int) -> dict[str, Any]:
    """Allocate the first low-rank factor (rank >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if rank < 1:
        raise SchemaError("rank must be >= 1")
    lid = hashlib.sha256(
        canonical_dumps({"t": t, "r": rank}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "left_id": lid,
        "rank": rank,
        "ok": True,
        "note": "abb abb_left",
    }


def abb_right(*, left_id: str) -> dict[str, Any]:
    """Allocate the second low-rank factor."""
    lid = left_id.strip()
    if not lid:
        raise SchemaError("left_id required")
    rid = hashlib.sha256(
        canonical_dumps({"l": lid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "right_id": rid,
        "ok": True,
        "note": "abb abb_right",
    }


def abb_hadamard(*, right_id: str) -> dict[str, Any]:
    """Form ΔW = (B1 A1) ⊙ (B2 A2)."""
    rid = right_id.strip()
    if not rid:
        raise SchemaError("right_id required")
    hid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hadamard_id": hid,
        "ok": True,
        "note": "abb abb_hadamard",
    }


def abb_score(*, hadamard_id: str, score: int) -> dict[str, Any]:
    """Score ABBA run (0–100)."""
    hid = hadamard_id.strip()
    if not hid:
        raise SchemaError("hadamard_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"h": hid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "abb abb_score",
    }


def abb_expr(*, expressive: bool) -> dict[str, Any]:
    """Flag W0-free Hadamard expressivity (report-only)."""
    return {
        "expressive": expressive,
        "apply": False,
        "ok": True,
        "note": "abb abb_expr",
    }


def abb_loop_plan(*, phase: str) -> dict[str, Any]:
    """Left → right → hadamard → score."""
    order = ("left", "right", "hadamard", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "left"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "abb abb_loop_plan",
    }
