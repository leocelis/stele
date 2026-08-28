"""BudgetMem-shaped query-aware budget-tier routing (stdlib; no LLM / no RL).

Modules expose Low/Mid/High tiers. Router is a deterministic heuristic on query
complexity — not the paper's RL policy (C5).
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError

TIERS = ("low", "mid", "high")
MODULES = (
    "candidate_pull",
    "compress",
    "expand",
    "assemble",
)

# Cost units per (module, tier) — relative, for planning only
_COST: dict[str, dict[str, int]] = {
    "candidate_pull": {"low": 1, "mid": 2, "high": 4},
    "compress": {"low": 1, "mid": 2, "high": 3},
    "expand": {"low": 1, "mid": 3, "high": 5},
    "assemble": {"low": 1, "mid": 2, "high": 4},
}

_COMPLEX_CUES = frozenset(
    {
        "why",
        "how",
        "compare",
        "versus",
        "multi",
        "hop",
        "before",
        "after",
        "between",
        "all",
        "every",
        "history",
        "timeline",
        "conflict",
        "which",
    }
)


def query_complexity(query: str) -> dict[str, Any]:
    """Score query hardness for tier routing (token count + cue hits)."""
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    toks = tokenize(q)
    cues = sorted(set(toks) & _COMPLEX_CUES)
    length = len(toks)
    score = round(min(1.0, length / 20.0 + 0.15 * len(cues)), 4)
    band = "low" if score < 0.35 else ("mid" if score < 0.65 else "high")
    return {
        "query": q,
        "token_count": length,
        "cues": cues,
        "score": score,
        "band": band,
        "ok": True,
        "note": "BudgetMem complexity heuristic — not RL router",
    }


def budget_tier_route(query: str) -> dict[str, Any]:
    """
    Per-module Low/Mid/High tier selection from query complexity.
    """
    cx = query_complexity(query)
    band = str(cx["band"])
    # Escalate expand/assemble first on hard queries; keep compress cheaper
    if band == "low":
        plan = {
            "candidate_pull": "low",
            "compress": "low",
            "expand": "low",
            "assemble": "low",
        }
    elif band == "mid":
        plan = {
            "candidate_pull": "mid",
            "compress": "low",
            "expand": "mid",
            "assemble": "mid",
        }
    else:
        plan = {
            "candidate_pull": "high",
            "compress": "mid",
            "expand": "high",
            "assemble": "high",
        }
    cost = sum(_COST[m][plan[m]] for m in MODULES)
    return {
        "query": query,
        "complexity": cx,
        "tiers": plan,
        "estimated_cost": cost,
        "ok": True,
        "note": "BudgetMem budget_tier_route — deterministic heuristic tiers",
    }


def budget_module_plan(
    query: str,
    *,
    global_budget: int = 10,
) -> dict[str, Any]:
    """
    Fit a tier plan under a global cost budget by stepping down modules.
    """
    if global_budget < 1:
        raise SchemaError("global_budget must be >= 1")
    route = budget_tier_route(query)
    tiers = dict(route["tiers"])
    # Prefer demoting expand then assemble then candidate_pull then compress
    demote_order = ["expand", "assemble", "candidate_pull", "compress"]
    tier_rank = {"high": 2, "mid": 1, "low": 0}
    rank_tier = {2: "high", 1: "mid", 0: "low"}

    def cost_of(t: Mapping[str, str]) -> int:
        return sum(_COST[m][t[m]] for m in MODULES)

    while cost_of(tiers) > global_budget:
        stepped = False
        for m in demote_order:
            r = tier_rank[tiers[m]]
            if r > 0:
                tiers[m] = rank_tier[r - 1]
                stepped = True
                break
        if not stepped:
            break
    return {
        "query": query,
        "global_budget": global_budget,
        "tiers": tiers,
        "estimated_cost": cost_of(tiers),
        "fits": cost_of(tiers) <= global_budget,
        "base_route": route["tiers"],
        "ok": True,
        "note": "BudgetMem module plan — demote expand first under budget",
    }


def tier_params(tier: str) -> dict[str, Any]:
    """Map a tier to concrete Stele Select/assembly knobs."""
    t = str(tier or "").strip().lower()
    if t not in TIERS:
        raise SchemaError(f"tier must be one of {TIERS}")
    if t == "low":
        return {
            "seed_limit": 3,
            "result_limit": 5,
            "follow_links": False,
            "body_max_chars": 200,
            "expand_limit": 3,
        }
    if t == "mid":
        return {
            "seed_limit": 5,
            "result_limit": 10,
            "follow_links": True,
            "body_max_chars": 400,
            "expand_limit": 6,
        }
    return {
        "seed_limit": 8,
        "result_limit": 20,
        "follow_links": True,
        "body_max_chars": 800,
        "expand_limit": 12,
    }
