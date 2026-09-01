"""AgentEvolver-shaped self-question / navigate / attribute (stdlib; no LLM).

Shaped by AgentEvolver (arXiv:2511.10395): curiosity task generation,
when/content experiences, mixed rollout split, step credit attribution.
Proxies only — not AgentEvolver paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def self_question_task(
    *,
    exploration_summary: str,
    user_preference: str = "",
) -> dict[str, Any]:
    """Self-questioning: synthesize a candidate task from exploration."""
    if not exploration_summary.strip():
        raise SchemaError("exploration_summary required")
    pref = user_preference.strip()[:80]
    query = f"Task from explore: {exploration_summary.strip()[:120]}"
    if pref:
        query = f"{query} (prefer: {pref})"
    tid = hashlib.sha256(
        canonical_dumps({"q": query, "p": pref}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "query": query[:200],
        "reference_hint": exploration_summary.strip()[:160],
        "apply": False,
        "ok": True,
        "note": "agentevolver self_question_task",
    }


def experience_when_content(
    *,
    when_to_use: str,
    content: str,
) -> dict[str, Any]:
    """Self-navigating experience unit: When to use + Content."""
    if not when_to_use.strip() or not content.strip():
        raise SchemaError("when_to_use and content required")
    eid = hashlib.sha256(
        canonical_dumps(
            {"w": when_to_use.strip(), "c": content.strip()}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experience_id": eid,
        "when_to_use": when_to_use.strip()[:160],
        "content": content.strip()[:240],
        "ok": True,
        "note": "agentevolver experience_when_content",
    }


def mixed_rollout_split(
    *,
    total_rollouts: int,
    eta: float = 0.5,
) -> dict[str, Any]:
    """Experience-mixed rollout: Ne = floor(η·N) guided, rest vanilla."""
    if total_rollouts < 1:
        raise SchemaError("total_rollouts must be >= 1")
    if not (0.0 <= eta <= 1.0):
        raise SchemaError("eta must be in [0, 1]")
    guided = int(eta * total_rollouts)
    vanilla = total_rollouts - guided
    return {
        "guided": guided,
        "vanilla": vanilla,
        "eta": eta,
        "ok": True,
        "note": "agentevolver mixed_rollout_split",
    }


def attribute_step_credit(
    *,
    step_scores: Sequence[float],
    outcome_reward: float,
) -> dict[str, Any]:
    """Self-attributing: distribute outcome reward by relative step scores."""
    if not isinstance(step_scores, Sequence) or isinstance(
        step_scores, (str, bytes)
    ):
        raise SchemaError("step_scores sequence required")
    scores = [float(s) for s in step_scores]
    if not scores:
        raise SchemaError("step_scores required")
    total = sum(max(0.0, s) for s in scores) or 1.0
    credits = [
        round(outcome_reward * (max(0.0, s) / total), 6) for s in scores
    ]
    return {
        "credits": credits,
        "sum_credits": round(sum(credits), 6),
        "ok": True,
        "note": "agentevolver attribute_step_credit",
    }


def curiosity_explore_plan(
    *,
    visited_states: int,
    novel_states: int,
    budget: int,
) -> dict[str, Any]:
    """Prefer exploring when novelty ratio is high and budget remains."""
    if visited_states < 0 or novel_states < 0 or budget < 0:
        raise SchemaError("counts must be >= 0")
    denom = max(1, visited_states)
    novelty = novel_states / denom
    continue_explore = budget > 0 and novelty >= 0.2
    return {
        "novelty_ratio": round(novelty, 4),
        "continue_explore": continue_explore,
        "budget_left": budget,
        "apply": False,
        "ok": True,
        "note": "agentevolver curiosity_explore_plan",
    }
