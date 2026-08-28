"""MemoBrain-shaped executive memory for reasoning (stdlib; no LLM).

Shaped by MemoBrain (arXiv:2601.08079): dependency-aware memory graph,
prune invalid steps, fold sub-trajectories, flush under budget, keep
salient backbone. Proxies only — plans report-only, no auto-delete.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def memobrain_dep_edge(*, src_step: str, dst_step: str) -> dict[str, Any]:
    """Add a dependency edge in the reasoning memory graph."""
    s = src_step.strip()
    d = dst_step.strip()
    if not s or not d:
        raise SchemaError("src_step and dst_step required")
    eid = hashlib.sha256(
        canonical_dumps({"s": s, "d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edge_id": eid,
        "ok": True,
        "note": "memobrain memobrain_dep_edge",
    }


def memobrain_prune_invalid(*, step_id: str, invalid: bool) -> dict[str, Any]:
    """Prune invalid reasoning steps (report-only)."""
    sid = step_id.strip()
    if not sid:
        raise SchemaError("step_id required")
    return {
        "step_id": sid[:64],
        "pruned": invalid,
        "apply": False,
        "ok": True,
        "note": "memobrain memobrain_prune_invalid",
    }


def memobrain_fold_subtraj(*, steps: int) -> dict[str, Any]:
    """Fold a completed sub-trajectory into a compact summary node."""
    if steps < 0:
        raise SchemaError("steps must be >= 0")
    return {
        "steps": steps,
        "folded": steps >= 2,
        "apply": False,
        "ok": True,
        "note": "memobrain memobrain_fold_subtraj",
    }


def memobrain_flush_budget(*, used: int, budget: int) -> dict[str, Any]:
    """Flush low-utility context when approaching budget."""
    if used < 0 or budget < 1:
        raise SchemaError("used >= 0 and budget >= 1")
    flush = used >= budget
    return {
        "flush": flush,
        "ratio": round(used / budget, 4),
        "apply": False,
        "ok": True,
        "note": "memobrain memobrain_flush_budget",
    }


def memobrain_salience_keep(*, salience: float, min_keep: float = 0.5) -> dict[str, Any]:
    """Keep high-salience backbone thoughts under fixed budget."""
    if not (0.0 <= salience <= 1.0) or not (0.0 <= min_keep <= 1.0):
        raise SchemaError("salience and min_keep must be in [0, 1]")
    return {
        "keep": salience >= min_keep,
        "salience": round(salience, 4),
        "ok": True,
        "note": "memobrain memobrain_salience_keep",
    }


def memobrain_loop_plan(*, phase: str) -> dict[str, Any]:
    """Dep → prune → fold → flush."""
    order = ("dep", "prune", "fold", "flush")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "dep"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "memobrain memobrain_loop_plan",
    }
