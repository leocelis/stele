"""ProcMEM-shaped procedural skills + non-parametric PPO gate (stdlib; no LLM).

Shaped by ProcMEM / Skill-Pro (arXiv:2602.01869): Skill-MDP triplets
(activation / execution / termination), semantic-gradient candidates,
PPO Gate verification, score-based maintain. Proxies only.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def define_skill_triplet(
    *,
    skill_id: str,
    activation: str,
    execution: str,
    termination: str,
) -> dict[str, Any]:
    """Formalize a Skill as I_ω / π_ω / β_ω."""
    if not skill_id.strip():
        raise SchemaError("skill_id required")
    if not activation.strip() or not execution.strip() or not termination.strip():
        raise SchemaError("activation, execution, termination required")
    key = hashlib.sha256(
        canonical_dumps(
            {
                "id": skill_id.strip(),
                "a": activation.strip(),
                "e": execution.strip(),
                "t": termination.strip(),
            }
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "skill_key": key,
        "skill_id": skill_id.strip()[:64],
        "activation": activation.strip()[:160],
        "execution": execution.strip()[:240],
        "termination": termination.strip()[:160],
        "ok": True,
        "note": "procmem define_skill_triplet",
    }


def skill_select_gate(
    *,
    state_text: str,
    activation: str,
    min_overlap: float = 0.25,
) -> dict[str, Any]:
    """μ(ω|s): activate skill when state overlaps activation condition."""
    if not state_text.strip() or not activation.strip():
        raise SchemaError("state_text and activation required")
    st = set(state_text.lower().split())
    ac = set(activation.lower().split())
    if not ac:
        overlap = 0.0
    else:
        overlap = len(st & ac) / len(ac)
    return {
        "activate": overlap >= min_overlap,
        "overlap": round(overlap, 4),
        "min_overlap": min_overlap,
        "ok": True,
        "note": "procmem skill_select_gate",
    }


def skill_terminate_check(
    *,
    observation: str,
    termination: str,
    min_overlap: float = 0.3,
) -> dict[str, Any]:
    """β_ω: terminate when observation matches termination condition."""
    if not observation.strip() or not termination.strip():
        raise SchemaError("observation and termination required")
    ob = set(observation.lower().split())
    tm = set(termination.lower().split())
    if not tm:
        overlap = 0.0
    else:
        overlap = len(ob & tm) / len(tm)
    return {
        "terminate": overlap >= min_overlap,
        "overlap": round(overlap, 4),
        "ok": True,
        "note": "procmem skill_terminate_check",
    }


def semantic_gradient_candidate(
    *,
    success_trace: str,
    failure_trace: str,
    base_skill_id: str,
) -> dict[str, Any]:
    """Propose refined skill text from success vs failure contrast (proxy)."""
    if not success_trace.strip() or not failure_trace.strip():
        raise SchemaError("success_trace and failure_trace required")
    if not base_skill_id.strip():
        raise SchemaError("base_skill_id required")
    s_tok = set(success_trace.lower().split())
    f_tok = set(failure_trace.lower().split())
    keep = sorted(s_tok - f_tok)[:8]
    avoid = sorted(f_tok - s_tok)[:8]
    proposal = (
        f"Prefer: {' '.join(keep)}. Avoid: {' '.join(avoid)}."
        if keep or avoid
        else "Refine from contrast (no unique tokens)."
    )
    return {
        "base_skill_id": base_skill_id.strip()[:64],
        "proposal": proposal[:240],
        "keep_tokens": keep,
        "avoid_tokens": avoid,
        "apply": False,
        "ok": True,
        "note": "procmem semantic_gradient_candidate",
    }


def ppo_gate_verify(
    *,
    candidate_score: float,
    incumbent_score: float,
    clip_eps: float = 0.2,
) -> dict[str, Any]:
    """PPO Gate: admit candidate only inside trust region vs incumbent."""
    if clip_eps <= 0:
        raise SchemaError("clip_eps must be > 0")
    if incumbent_score == 0:
        ratio = 1.0 if candidate_score >= 0 else 0.0
    else:
        ratio = candidate_score / incumbent_score
    lo, hi = 1.0 - clip_eps, 1.0 + clip_eps
    admit = lo <= ratio <= hi and candidate_score >= incumbent_score
    return {
        "admit": admit,
        "ratio": round(ratio, 4),
        "clip_lo": lo,
        "clip_hi": hi,
        "apply": False,
        "ok": True,
        "note": "procmem ppo_gate_verify",
    }


def skill_score_maintain(
    *,
    frequency: int,
    avg_gain: float,
    min_score: float = 0.1,
) -> dict[str, Any]:
    """Score-based maintain: keep if freq × avg_gain ≥ min_score."""
    if frequency < 0:
        raise SchemaError("frequency must be >= 0")
    score = frequency * avg_gain
    return {
        "score": round(score, 4),
        "keep": score >= min_score,
        "prune": score < min_score,
        "apply": False,
        "ok": True,
        "note": "procmem skill_score_maintain",
    }
