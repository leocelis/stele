"""SkillFlow-shaped flow orchestration + skill evolution (stdlib; no LLM).

Shaped by SkillFlow (arXiv:2605.14089): Supervisor action types,
Tempered Trajectory Balance residual, step importance, skill marginal
flow, retain/refine/prune/create curation, phase evolve gate.
Proxies only — not SkillFlow paper scores.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError

ACTION_TYPES = frozenset({"skill", "act", "accept"})


def orchestration_action_select(
    *,
    action_type: str,
    skill_id: str | None = None,
    step: int = 0,
    tmax: int = 20,
) -> dict[str, Any]:
    """Supervisor step: skill | act | accept with budget check."""
    if action_type not in ACTION_TYPES:
        raise SchemaError(f"action_type must be one of {sorted(ACTION_TYPES)}")
    if step < 0 or tmax < 1:
        raise SchemaError("invalid step/tmax")
    barriers: list[str] = []
    if action_type == "skill" and not (skill_id and skill_id.strip()):
        barriers.append("skill_id_required")
    if step >= tmax and action_type != "accept":
        barriers.append("budget_exhausted_must_accept")
    terminal = action_type == "accept" or step >= tmax
    return {
        "action_type": action_type,
        "skill_id": skill_id,
        "terminal": terminal,
        "allowed": len(barriers) == 0,
        "barriers": barriers,
        "ok": True,
        "note": "skillflow orchestration_action_select",
    }


def ttb_residual(
    *,
    log_forward: float,
    log_backward: float,
    log_reward: float,
    log_z: float = 0.0,
    length: int = 1,
) -> dict[str, Any]:
    """Tempered Trajectory Balance residual Δ proxy (squared / T²)."""
    if length < 1:
        raise SchemaError("length must be >= 1")
    # TB: log Z + sum log PF ≈ log R + sum log PB  (simplified one-step)
    delta = (log_z + log_forward) - (log_reward + log_backward)
    loss = (delta * delta) / (length * length)
    return {
        "delta": round(delta, 6),
        "loss": round(loss, 6),
        "saturated": abs(delta) < 1e-3,
        "ok": True,
        "note": "skillflow ttb_residual",
    }


def step_importance(
    *,
    log_forward: float,
    log_backward: float,
) -> dict[str, Any]:
    """I(t) = PF / PB credit — large |log I| = appraisal shifted after exec."""
    import math

    # avoid div0
    ratio = math.exp(log_forward - log_backward)
    log_i = log_forward - log_backward
    return {
        "importance": round(ratio, 6),
        "log_importance": round(log_i, 6),
        "high_credit_gap": abs(log_i) >= 1.0,
        "ok": True,
        "note": "skillflow step_importance",
    }


def skill_marginal_flow(
    *,
    skill_flows: Sequence[float],
    skill_id: str,
    target_index: int = 0,
) -> dict[str, Any]:
    """F̂(s) share of total flow for a skill."""
    if not skill_id.strip():
        raise SchemaError("skill_id required")
    flows = [float(f) for f in skill_flows]
    if not flows:
        raise SchemaError("skill_flows required")
    if target_index < 0 or target_index >= len(flows):
        raise SchemaError("target_index out of range")
    total = sum(max(0.0, f) for f in flows) or 1.0
    f_s = max(0.0, flows[target_index])
    share = f_s / total
    return {
        "skill_id": skill_id.strip()[:64],
        "flow": round(f_s, 6),
        "share": round(share, 6),
        "ok": True,
        "note": "skillflow skill_marginal_flow",
    }


def skill_curation_decide(
    *,
    mean_log_flow: float,
    centered_log_share: float,
    jensen_gap: float = 0.0,
    high_importance_step: bool = False,
) -> dict[str, Any]:
    """Φ operator proxy: retain / refine / prune / create."""
    if centered_log_share < -0.5:
        decision = "prune"
    elif mean_log_flow > 0.0 and jensen_gap >= 0.5:
        decision = "refine"
    elif high_importance_step and mean_log_flow <= 0.0:
        decision = "create"
    else:
        decision = "retain"
    return {
        "decision": decision,
        "mean_log_flow": mean_log_flow,
        "centered_log_share": centered_log_share,
        "jensen_gap": jensen_gap,
        "apply": False,
        "ok": True,
        "note": "skillflow skill_curation_decide",
    }


def phase_evolve_gate(
    *,
    residual_mean: float,
    residual_floor: float,
    plateau_eps: float = 0.05,
) -> dict[str, Any]:
    """When: evolve library when residual saturates against floor."""
    if residual_floor < 0:
        raise SchemaError("residual_floor must be >= 0")
    gap = abs(residual_mean - residual_floor)
    evolve = gap <= plateau_eps and residual_mean > 0
    return {
        "evolve": evolve,
        "gap": round(gap, 6),
        "reason": "residual_plateau" if evolve else "still_descending",
        "apply": False,
        "ok": True,
        "note": "skillflow phase_evolve_gate",
    }
