"""Agent0-shaped curriculum–executor co-evolution (stdlib; no LLM / no tools).

Shaped by Agent0 (arXiv:2511.16043): curriculum agent + executor agent,
tool-use reward, uncertainty frontier filter, symbiotic rounds.
Proxies only — not Agent0 paper scores.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def curriculum_propose_task(
    *,
    task: str,
    requires_tool: bool = False,
) -> dict[str, Any]:
    """Curriculum agent proposes a frontier task."""
    body = task.strip()
    if not body:
        raise SchemaError("task required")
    tid = hashlib.sha256(
        canonical_dumps({"t": body, "tool": requires_tool}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "task": body[:200],
        "requires_tool": requires_tool,
        "ok": True,
        "note": "agent0 curriculum_propose_task",
    }


def tool_use_reward(
    *,
    tool_call_count: int,
    gamma: float = 0.25,
    cap: int = 4,
) -> dict[str, Any]:
    """R_tool = γ · min(N_tool, C)."""
    if tool_call_count < 0:
        raise SchemaError("tool_call_count must be >= 0")
    if gamma < 0 or cap < 0:
        raise SchemaError("gamma and cap must be >= 0")
    r = gamma * min(tool_call_count, cap)
    return {
        "r_tool": round(r, 4),
        "capped": tool_call_count > cap,
        "ok": True,
        "note": "agent0 tool_use_reward",
    }


def curriculum_reward(
    *,
    r_uncertainty: float,
    r_tool: float,
    r_repetition: float = 0.0,
    lambda_unc: float = 0.5,
    lambda_tool: float = 0.6,
    format_ok: bool = True,
) -> dict[str, Any]:
    """R_C = format · max(0, λ_unc R_unc + λ_tool R_tool − R_rep)."""
    if not format_ok:
        return {
            "r_curriculum": 0.0,
            "format_ok": False,
            "ok": True,
            "note": "agent0 curriculum_reward",
        }
    raw = lambda_unc * r_uncertainty + lambda_tool * r_tool - r_repetition
    return {
        "r_curriculum": round(max(0.0, raw), 4),
        "format_ok": True,
        "ok": True,
        "note": "agent0 curriculum_reward",
    }


def executor_frontier_filter(
    *,
    self_consistency: float,
    low: float = 0.3,
    high: float = 0.8,
) -> dict[str, Any]:
    """Keep tasks with self-consistency in the informative band."""
    if not (0.0 <= self_consistency <= 1.0):
        raise SchemaError("self_consistency must be in [0, 1]")
    keep = low <= self_consistency <= high
    return {
        "keep": keep,
        "self_consistency": self_consistency,
        "band": [low, high],
        "ok": True,
        "note": "agent0 executor_frontier_filter",
    }


def tool_aware_pressure(
    *,
    executor_tool_success_rate: float,
    prior_task_complexity: float,
) -> dict[str, Any]:
    """Higher executor tool success → pressure curriculum to raise complexity."""
    if not (0.0 <= executor_tool_success_rate <= 1.0):
        raise SchemaError("executor_tool_success_rate must be in [0, 1]")
    if prior_task_complexity < 0:
        raise SchemaError("prior_task_complexity must be >= 0")
    boost = round(executor_tool_success_rate * 0.5, 4)
    target = round(prior_task_complexity + boost, 4)
    return {
        "target_complexity": target,
        "pressure_boost": boost,
        "ok": True,
        "note": "agent0 tool_aware_pressure",
    }


def symbiotic_round_plan(
    *,
    round_index: int,
    curriculum_updated: bool,
    executor_updated: bool,
) -> dict[str, Any]:
    """Curriculum evolves first (frozen executor), then executor on filtered set."""
    if round_index < 0:
        raise SchemaError("round_index must be >= 0")
    order_ok = (not executor_updated) or curriculum_updated
    if curriculum_updated and not executor_updated:
        nxt = "executor"
    else:
        nxt = "curriculum"
    return {
        "round_index": round_index,
        "order_ok": order_ok,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "agent0 symbiotic_round_plan",
    }
