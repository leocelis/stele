"""LoRA-LEGO proxies (stdlib; no LLM).

Shaped by LoRA-LEGO (arXiv:2409.16167): treat per-rank LoRA columns as
Minimal Semantic Units (MSUs), cluster across adapters, assemble a
merged LoRA from cluster centroids + dual reweight. Proxies only.

Prefix ``llg_*`` — not HydraLoRA (``hyd_*``) / LoRAHub / LoraHub.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def llg_msu(*, task: str, adapters: int) -> dict[str, Any]:
    """Collect MSUs from adapters (adapters >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if adapters < 2:
        raise SchemaError("adapters must be >= 2")
    mid = hashlib.sha256(
        canonical_dumps({"t": t, "a": adapters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "msu_id": mid,
        "adapters": adapters,
        "ok": True,
        "note": "llg llg_msu",
    }


def llg_cluster(*, msu_id: str, k: int) -> dict[str, Any]:
    """Rank-wise cluster MSUs into k centroids (k >= 1)."""
    mid = msu_id.strip()
    if not mid:
        raise SchemaError("msu_id required")
    if k < 1:
        raise SchemaError("k must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"m": mid, "k": k}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cluster_id": cid,
        "k": k,
        "ok": True,
        "note": "llg llg_cluster",
    }


def llg_merge(*, cluster_id: str) -> dict[str, Any]:
    """Assemble merged LoRA from cluster centroids + reweight."""
    cid = cluster_id.strip()
    if not cid:
        raise SchemaError("cluster_id required")
    mid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "merge_id": mid,
        "ok": True,
        "note": "llg llg_merge",
    }


def llg_score(*, merge_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-LEGO merge (0–100)."""
    mid = merge_id.strip()
    if not mid:
        raise SchemaError("merge_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"m": mid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "llg llg_score",
    }


def llg_modular(*, modular_merge: bool) -> dict[str, Any]:
    """Flag modular LEGO-style merge (report-only)."""
    return {
        "modular_merge": modular_merge,
        "apply": False,
        "ok": True,
        "note": "llg llg_modular",
    }


def llg_loop_plan(*, phase: str) -> dict[str, Any]:
    """Msu → cluster → merge → score."""
    order = ("msu", "cluster", "merge", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "msu"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "llg llg_loop_plan",
    }
