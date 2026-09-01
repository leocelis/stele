"""Auto-CoT-shaped automatic demonstration construction (stdlib; no LLM).

Shaped by Auto-CoT (arXiv:2210.03493): cluster questions, sample diverse
demos, generate Zero-Shot-CoT chains. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def autocot_cluster(*, questions: int, clusters: int) -> dict[str, Any]:
    """Partition questions into diversity clusters."""
    if questions < 1:
        raise SchemaError("questions must be >= 1")
    if clusters < 1:
        raise SchemaError("clusters must be >= 1")
    cid = hashlib.sha256(
        canonical_dumps({"q": questions, "c": clusters}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "cluster_id": cid,
        "clusters": clusters,
        "ok": True,
        "note": "autocot autocot_cluster",
    }


def autocot_sample(*, cluster_id: str) -> dict[str, Any]:
    """Sample a representative question from a cluster."""
    cid = cluster_id.strip()
    if not cid:
        raise SchemaError("cluster_id required")
    sid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "demo_id": sid,
        "ok": True,
        "note": "autocot autocot_sample",
    }


def autocot_generate(*, demo_id: str) -> dict[str, Any]:
    """Generate a Zero-Shot-CoT reasoning chain for a demo."""
    did = demo_id.strip()
    if not did:
        raise SchemaError("demo_id required")
    rid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "chain_id": rid,
        "ok": True,
        "note": "autocot autocot_generate",
    }


def autocot_heuristic(*, max_steps: int) -> dict[str, Any]:
    """Simple length/steps heuristic for demo quality."""
    if max_steps < 1:
        raise SchemaError("max_steps must be >= 1")
    return {
        "max_steps": max_steps,
        "ok": True,
        "note": "autocot autocot_heuristic",
    }


def autocot_diversity(*, diverse: bool) -> dict[str, Any]:
    """Flag that diversity mitigates mistaken chains."""
    return {
        "diverse": diverse,
        "ok": True,
        "note": "autocot autocot_diversity",
    }


def autocot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Cluster → sample → generate → heuristic."""
    order = ("cluster", "sample", "generate", "heuristic")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "cluster"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "autocot autocot_loop_plan",
    }
