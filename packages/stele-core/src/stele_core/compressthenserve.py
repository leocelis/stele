"""Compress-then-Serve proxies (stdlib; no LLM).

Shaped by Compress then Serve (arXiv:2407.00066 · ICML 2025): joint
compression of many LoRAs into a shared basis + per-adapter scales,
with clustering for large collections. Proxies only.

Prefix ``cts_*`` — not S-LoRA (``slr_*``) / FLoRA (``flo_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cts_collect(*, adapters: int) -> dict[str, Any]:
    """Collect LoRA adapters for joint compression (adapters >= 1)."""
    if adapters < 1:
        raise SchemaError("adapters must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"a": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "collect_id": cid,
        "adapters": adapters,
        "ok": True,
        "note": "cts cts_collect",
    }


def cts_basis(*, collect_id: str) -> dict[str, Any]:
    """Learn shared basis via joint diagonalization."""
    cid = collect_id.strip()
    if not cid:
        raise SchemaError("collect_id required")
    bid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "basis_id": bid,
        "ok": True,
        "note": "cts cts_basis",
    }


def cts_scale(*, basis_id: str, adapters: int) -> dict[str, Any]:
    """Per-adapter scaling matrices over shared basis (adapters >= 1)."""
    bid = basis_id.strip()
    if not bid:
        raise SchemaError("basis_id required")
    if adapters < 1:
        raise SchemaError("adapters must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"b": bid, "a": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "adapters": adapters,
        "ok": True,
        "note": "cts cts_scale",
    }


def cts_score(*, scale_id: str, score: int) -> dict[str, Any]:
    """Score compressed serving quality (0–100)."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid, "x": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": xid,
        "score": score,
        "ok": True,
        "note": "cts cts_score",
    }


def cts_cluster(*, cluster_for_large: bool) -> dict[str, Any]:
    """Flag cluster-then-compress for large collections (report-only)."""
    return {
        "cluster_for_large": cluster_for_large,
        "apply": False,
        "ok": True,
        "note": "cts cts_cluster",
    }


def cts_loop_plan(*, phase: str) -> dict[str, Any]:
    """Collect → basis → scale → score."""
    order = ("collect", "basis", "scale", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "collect"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "cts cts_loop_plan",
    }
