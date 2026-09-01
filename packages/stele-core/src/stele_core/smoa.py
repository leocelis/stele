"""SMoA proxies (stdlib; no LLM).

Shaped by High-Rank Structured Modulation (arXiv:2601.07507):
modulate disjoint subspaces so effective rank rises without extra
params. Proxies only.

Prefix ``smo_*`` — not BoHA (``bha_*``) / MoRA (``mor_*``) / MixLoRA
(``mxl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def smo_struct(*, task: str, subspaces: int) -> dict[str, Any]:
    """Carve disjoint subspaces (subspaces >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if subspaces < 1:
        raise SchemaError("subspaces must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "n": subspaces}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "struct_id": sid,
        "subspaces": subspaces,
        "ok": True,
        "note": "smo smo_struct",
    }


def smo_mod(*, struct_id: str) -> dict[str, Any]:
    """Apply per-subspace structured modulation."""
    sid = struct_id.strip()
    if not sid:
        raise SchemaError("struct_id required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "mod_id": mid,
        "ok": True,
        "note": "smo smo_mod",
    }


def smo_train(*, mod_id: str) -> dict[str, Any]:
    """Train SMoA modulators."""
    mid = mod_id.strip()
    if not mid:
        raise SchemaError("mod_id required")
    tid = hashlib.sha256(
        canonical_dumps({"m": mid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "smo smo_train",
    }


def smo_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score SMoA run (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "smo smo_score",
    }


def smo_rank(*, high_rank: bool) -> dict[str, Any]:
    """Flag high effective rank without extra params (report-only)."""
    return {
        "high_rank": high_rank,
        "apply": False,
        "ok": True,
        "note": "smo smo_rank",
    }


def smo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Struct → mod → train → score."""
    order = ("struct", "mod", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "struct"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "smo smo_loop_plan",
    }
