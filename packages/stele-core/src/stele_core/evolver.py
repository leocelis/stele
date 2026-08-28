"""EvolveR-shaped experience lifecycle (stdlib; no LLM / no GRPO train).

Shaped by EvolveR (arXiv:2510.16079): offline principle distillation,
dedupe/merge, metric score, online search_experience action, phase gate.
Proxies only — not EvolveR paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

PRINCIPLE_KINDS = frozenset({"success", "failure"})
PHASES = frozenset({"online", "offline"})
ACTIONS = frozenset({"search_experience", "search_knowledge", "answer"})


def distill_principle(
    *,
    kind: str,
    description: str,
    triples: Sequence[Sequence[str]] | None = None,
) -> dict[str, Any]:
    """Offline: distill a success/failure strategic principle."""
    if kind not in PRINCIPLE_KINDS:
        raise SchemaError(f"kind must be one of {sorted(PRINCIPLE_KINDS)}")
    if not description.strip():
        raise SchemaError("description required")
    trips: list[list[str]] = []
    for t in triples or []:
        if len(t) >= 3:
            trips.append([str(t[0])[:40], str(t[1])[:40], str(t[2])[:40]])
    pid = hashlib.sha256(
        canonical_dumps(
            {"k": kind, "d": description.strip(), "t": trips}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "principle_id": pid,
        "kind": kind,
        "description": description.strip()[:200],
        "triples": trips[:5],
        "use_count": 0,
        "succ_count": 0,
        "ok": True,
        "note": "evolver distill_principle",
    }


def principle_dedupe_plan(
    *,
    candidate_desc: str,
    existing_descs: Sequence[str],
    sim_threshold: float = 0.5,
) -> dict[str, Any]:
    """Dedupe: merge if high token overlap, else add."""
    if not candidate_desc.strip():
        raise SchemaError("candidate_desc required")
    cand = set(candidate_desc.lower().split())
    best_i = -1
    best = 0.0
    for i, d in enumerate(existing_descs):
        other = set(str(d).lower().split())
        if not cand or not other:
            continue
        sim = len(cand & other) / len(cand | other)
        if sim > best:
            best = sim
            best_i = i
    merge = best >= sim_threshold and best_i >= 0
    return {
        "action": "merge" if merge else "add",
        "best_index": best_i if merge else None,
        "similarity": round(best, 4),
        "apply": False,
        "ok": True,
        "note": "evolver principle_dedupe_plan",
    }


def principle_metric_score(
    *,
    succ_count: int,
    use_count: int,
    prune_threshold: float = 0.2,
) -> dict[str, Any]:
    """s(p) = c_succ / c_use (or 0 if unused); prune if below θ."""
    if succ_count < 0 or use_count < 0:
        raise SchemaError("counts must be >= 0")
    if use_count == 0:
        score = 0.0
    else:
        score = succ_count / use_count
    return {
        "score": round(score, 4),
        "prune": score < prune_threshold and use_count > 0,
        "ok": True,
        "note": "evolver principle_metric_score",
    }


def search_experience_action(
    *,
    action: str,
    query: str = "",
) -> dict[str, Any]:
    """Online action space: search_experience | search_knowledge | answer."""
    if action not in ACTIONS:
        raise SchemaError(f"action must be one of {sorted(ACTIONS)}")
    barriers: list[str] = []
    if action == "search_experience" and not query.strip():
        barriers.append("query_required")
    if action == "search_knowledge" and not query.strip():
        barriers.append("query_required")
    return {
        "action": action,
        "allowed": len(barriers) == 0,
        "barriers": barriers,
        "ok": True,
        "note": "evolver search_experience_action",
    }


def lifecycle_phase_gate(
    *,
    phase: str,
    mutate_policy: bool = False,
    distill: bool = False,
) -> dict[str, Any]:
    """Online may RL-update; offline freezes policy for distillation."""
    if phase not in PHASES:
        raise SchemaError(f"phase must be one of {sorted(PHASES)}")
    barriers: list[str] = []
    if phase == "offline" and mutate_policy:
        barriers.append("offline_policy_frozen")
    if phase == "online" and distill:
        barriers.append("distill_is_offline_only")
    return {
        "phase": phase,
        "allowed": len(barriers) == 0,
        "barriers": barriers,
        "ok": True,
        "note": "evolver lifecycle_phase_gate",
    }


def prune_low_score_principles(
    *,
    scores: Sequence[float],
    threshold: float = 0.2,
) -> dict[str, Any]:
    """Report which principle indices fall below prune threshold."""
    if not isinstance(scores, Sequence) or isinstance(scores, (str, bytes)):
        raise SchemaError("scores sequence required")
    drop = [i for i, s in enumerate(scores) if float(s) < threshold]
    return {
        "drop_indices": drop,
        "keep_count": len(scores) - len(drop),
        "apply": False,
        "ok": True,
        "note": "evolver prune_low_score_principles",
    }
