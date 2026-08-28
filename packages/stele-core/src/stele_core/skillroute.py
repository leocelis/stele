"""Compositional skill routing + SAD (stdlib; no LLM / no FAISS).

Shaped by Compositional Skill Routing / SkillWeaver (arXiv:2606.18051):
decompose → retrieve → compose DAG; Skill-Aware Decomposition feedback.
Proxies only — not CompSkillBench scores.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError


def decompose_task_steps(
    *,
    query: str,
    max_steps: int = 6,
) -> dict[str, Any]:
    """Decompose query into atomic sub-tasks (heuristic split)."""
    if not query.strip():
        raise SchemaError("query required")
    if max_steps < 1:
        raise SchemaError("max_steps must be >= 1")
    # Split on " then " / " and " / ";" as crude atomic steps
    raw = query.strip()
    for sep in (" then ", " and then ", "; ", " → "):
        if sep in raw.lower():
            # case-insensitive split via lower index scan
            parts: list[str] = []
            remaining = raw
            low = remaining.lower()
            while sep in low and len(parts) < max_steps - 1:
                i = low.index(sep)
                parts.append(remaining[:i].strip())
                remaining = remaining[i + len(sep) :].strip()
                low = remaining.lower()
            if remaining:
                parts.append(remaining)
            steps = [p for p in parts if p][:max_steps]
            break
    else:
        steps = [raw[:120]]
    return {
        "steps": steps,
        "step_count": len(steps),
        "ok": True,
        "note": "skillroute decompose_task_steps",
    }


def retrieve_skills_for_steps(
    *,
    steps: Sequence[str],
    skill_catalog: Sequence[dict[str, Any]],
    top_m: int = 2,
) -> dict[str, Any]:
    """Per-step skill retrieval by token overlap with catalog descriptions."""
    if not isinstance(steps, Sequence) or isinstance(steps, (str, bytes)):
        raise SchemaError("steps sequence required")
    if top_m < 1:
        raise SchemaError("top_m must be >= 1")
    per_step: list[dict[str, Any]] = []
    for step in steps:
        st = set(str(step).lower().split())
        scored: list[dict[str, Any]] = []
        for sk in skill_catalog:
            if not isinstance(sk, dict):
                continue
            text = f"{sk.get('name') or ''} {sk.get('description') or ''}"
            tok = set(text.lower().split())
            sim = (
                len(st & tok) / len(st | tok) if st and tok else 0.0
            )
            scored.append(
                {
                    "skill_id": sk.get("skill_id") or sk.get("name"),
                    "similarity": round(sim, 4),
                }
            )
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        per_step.append({"step": str(step)[:80], "candidates": scored[:top_m]})
    return {
        "per_step": per_step,
        "ok": True,
        "note": "skillroute retrieve_skills_for_steps",
    }


def compose_skill_dag(
    *,
    step_skills: Sequence[str],
) -> dict[str, Any]:
    """Compose linear DAG edges between consecutive step skills."""
    if not isinstance(step_skills, Sequence) or isinstance(
        step_skills, (str, bytes)
    ):
        raise SchemaError("step_skills sequence required")
    nodes = [str(s).strip() for s in step_skills if str(s).strip()]
    if not nodes:
        raise SchemaError("step_skills required")
    edges = [
        {"from": nodes[i], "to": nodes[i + 1]} for i in range(len(nodes) - 1)
    ]
    return {
        "nodes": nodes,
        "edges": edges,
        "parallel_ok": False,
        "apply": False,
        "ok": True,
        "note": "skillroute compose_skill_dag",
    }


def sad_feedback_loop(
    *,
    prior_steps: Sequence[str],
    hint_skill_names: Sequence[str],
) -> dict[str, Any]:
    """SAD: re-decompose using retrieved skill names as vocabulary hints."""
    if not isinstance(prior_steps, Sequence) or isinstance(
        prior_steps, (str, bytes)
    ):
        raise SchemaError("prior_steps sequence required")
    hints = [str(h).strip() for h in hint_skill_names if str(h).strip()]
    # Prefer hint-aligned step labels when available
    revised: list[str] = []
    for i, step in enumerate(prior_steps):
        if i < len(hints):
            revised.append(f"{hints[i]}: {str(step).strip()}"[:120])
        else:
            revised.append(str(step).strip()[:120])
    return {
        "revised_steps": revised,
        "hint_count": len(hints),
        "apply": False,
        "ok": True,
        "note": "skillroute sad_feedback_loop",
    }


def granularity_match_check(
    *,
    step_count: int,
    expected_skills: int,
) -> dict[str, Any]:
    """DA proxy: decomposition agrees when step count == expected skills."""
    if step_count < 1 or expected_skills < 1:
        raise SchemaError("counts must be >= 1")
    matched = step_count == expected_skills
    return {
        "da_match": matched,
        "step_count": step_count,
        "expected_skills": expected_skills,
        "ok": True,
        "note": "skillroute granularity_match_check",
    }
