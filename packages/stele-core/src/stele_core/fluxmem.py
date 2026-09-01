"""FluxMem-shaped connectivity-evolving memory (stdlib; no LLM).

Shaped by FluxMem (arXiv:2605.28773): heterogeneous graph topology refined
via initial connection formation, feedback-driven refinement, and
long-term consolidation — repair, prune, maturity. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def flux_connect_form(*, src: str, dst: str, relation: str) -> dict[str, Any]:
    """Stage 1: form an initial heterogeneous graph edge."""
    s = src.strip()
    d = dst.strip()
    rel = relation.strip()
    if not s or not d or not rel:
        raise SchemaError("src, dst, and relation required")
    eid = hashlib.sha256(
        canonical_dumps({"s": s, "d": d, "r": rel}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edge_id": eid,
        "src": s[:64],
        "dst": d[:64],
        "relation": rel[:64],
        "ok": True,
        "note": "fluxmem flux_connect_form",
    }


def flux_feedback_refine(
    *,
    edge_id: str,
    feedback: str,
    keep: bool,
) -> dict[str, Any]:
    """Stage 2: feedback-driven refinement of an edge."""
    eid = edge_id.strip()
    fb = feedback.strip()
    if not eid or not fb:
        raise SchemaError("edge_id and feedback required")
    return {
        "edge_id": eid[:64],
        "kept": keep,
        "feedback": fb[:120],
        "ok": True,
        "note": "fluxmem flux_feedback_refine",
    }


def flux_consolidate(*, circuits: int, min_success: int = 2) -> dict[str, Any]:
    """Stage 3: distill recurrent trajectories into procedural circuits."""
    if circuits < 0 or min_success < 1:
        raise SchemaError("circuits >= 0 and min_success >= 1")
    ready = circuits >= min_success
    return {
        "circuits": circuits,
        "ready": ready,
        "ok": True,
        "note": "fluxmem flux_consolidate",
    }


def flux_repair_link(*, missing: bool, repaired: bool) -> dict[str, Any]:
    """Repair missing links during execution."""
    return {
        "missing": missing,
        "repaired": repaired if missing else False,
        "ok": True,
        "note": "fluxmem flux_repair_link",
    }


def flux_prune_interference(*, noise_score: float, threshold: float = 0.5) -> dict[str, Any]:
    """Prune interference edges above threshold."""
    if noise_score < 0.0 or threshold < 0.0:
        raise SchemaError("noise_score and threshold must be >= 0")
    pruned = noise_score >= threshold
    return {
        "pruned": pruned,
        "noise_score": round(noise_score, 4),
        "ok": True,
        "note": "fluxmem flux_prune_interference",
    }


def flux_maturity_gate(*, generalizability: float, min_score: float = 0.5) -> dict[str, Any]:
    """Memory generalizability / evolutionary maturity metric."""
    if not (0.0 <= generalizability <= 1.0) or not (0.0 <= min_score <= 1.0):
        raise SchemaError("scores must be in [0, 1]")
    mature = generalizability >= min_score
    return {
        "mature": mature,
        "generalizability": round(generalizability, 4),
        "ok": True,
        "note": "fluxmem flux_maturity_gate",
    }


def flux_loop_plan(*, phase: str) -> dict[str, Any]:
    """Connect → refine → consolidate → mature."""
    order = ("connect", "refine", "consolidate", "mature")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "connect"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "fluxmem flux_loop_plan",
    }
