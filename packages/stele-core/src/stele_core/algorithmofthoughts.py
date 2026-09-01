"""Algorithm-of-Thoughts-shaped in-context search (stdlib; no LLM).

Shaped by Algorithm of Thoughts (arXiv:2308.10379): algorithmic
exemplars, subtree explore, tunnel-vision prune, single-query budget.
Proxies only — not Sel et al. AoT runtime.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def aot_load_algorithm(*, name: str) -> dict[str, Any]:
    """Load an algorithmic in-context exemplar name."""
    n = name.strip()
    if not n:
        raise SchemaError("name required")
    aid = hashlib.sha256(
        canonical_dumps({"n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "algo_id": aid,
        "name": n[:64],
        "ok": True,
        "note": "aot aot_load_algorithm",
    }


def aot_explore_subtree(*, depth: int, branch: int) -> dict[str, Any]:
    """Explore one algorithmic subtree (proxy counts)."""
    if depth < 0 or branch < 0:
        raise SchemaError("depth and branch must be >= 0")
    return {
        "depth": depth,
        "branch": branch,
        "ok": True,
        "note": "aot aot_explore_subtree",
    }


def aot_tunnel_vision(*, activate: bool) -> dict[str, Any]:
    """Tunnel-vision prune of hopeless branches (report-only)."""
    return {
        "activate": activate,
        "apply": False,
        "ok": True,
        "note": "aot aot_tunnel_vision",
    }


def aot_query_budget(*, queries: int) -> dict[str, Any]:
    """Record single/few-query budget (AoT goal: few queries)."""
    if queries < 1:
        raise SchemaError("queries must be >= 1")
    return {
        "queries": queries,
        "ok": True,
        "note": "aot aot_query_budget",
    }


def aot_surpass_algo(*, intuition: bool) -> dict[str, Any]:
    """Flag that LLM intuition may surpass the base algorithm."""
    return {
        "intuition": intuition,
        "ok": True,
        "note": "aot aot_surpass_algo",
    }


def aot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Load → explore → tunnel → budget."""
    order = ("load", "explore", "tunnel", "budget")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "load"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "aot aot_loop_plan",
    }
