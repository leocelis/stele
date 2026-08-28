"""MemRL-shaped value-aware episodic retrieval (stdlib; no LLM).

Shaped by MemRL (arXiv:2601.03192): Intent-Experience-Utility bank,
two-phase retrieval (semantic then Q), runtime utility update.
Proxies only — not MemRL paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ieu_record(
    *,
    intent: str,
    experience: str,
    utility: float = 0.0,
) -> dict[str, Any]:
    """Intent-Experience-Utility memory item."""
    if not intent.strip() or not experience.strip():
        raise SchemaError("intent and experience required")
    mid = hashlib.sha256(
        canonical_dumps(
            {"i": intent.strip(), "e": experience.strip()}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "intent": intent.strip()[:160],
        "experience": experience.strip()[:240],
        "utility": float(utility),
        "ok": True,
        "note": "memrl ieu_record",
    }


def _token_overlap(a: str, b: str) -> float:
    ta = set(a.lower().split())
    tb = set(b.lower().split())
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def two_phase_retrieve(
    *,
    query: str,
    memories: Sequence[dict[str, Any]],
    top_k_semantic: int = 5,
    top_k_utility: int = 2,
) -> dict[str, Any]:
    """Phase A semantic recall → Phase B value-aware select."""
    if not query.strip():
        raise SchemaError("query required")
    if not isinstance(memories, Sequence) or isinstance(memories, (str, bytes)):
        raise SchemaError("memories sequence required")
    if top_k_semantic < 1 or top_k_utility < 1:
        raise SchemaError("top_k must be >= 1")
    scored: list[dict[str, Any]] = []
    for m in memories:
        if not isinstance(m, dict):
            continue
        text = f"{m.get('intent') or ''} {m.get('experience') or ''}"
        sim = _token_overlap(query, text)
        scored.append(
            {
                "memory_id": m.get("memory_id"),
                "similarity": round(sim, 4),
                "utility": float(m.get("utility") or 0.0),
            }
        )
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    phase_a = scored[:top_k_semantic]
    phase_b = sorted(phase_a, key=lambda x: x["utility"], reverse=True)[
        :top_k_utility
    ]
    return {
        "phase_a": phase_a,
        "phase_b": phase_b,
        "selected_ids": [x.get("memory_id") for x in phase_b],
        "ok": True,
        "note": "memrl two_phase_retrieve",
    }


def utility_q_update(
    *,
    current_q: float,
    reward: float,
    next_max_q: float = 0.0,
    alpha: float = 0.3,
    gamma: float = 0.9,
) -> dict[str, Any]:
    """Runtime utility update via Bellman-style backup."""
    if not (0.0 < alpha <= 1.0):
        raise SchemaError("alpha must be in (0, 1]")
    if not (0.0 <= gamma <= 1.0):
        raise SchemaError("gamma must be in [0, 1]")
    target = reward + gamma * next_max_q
    new_q = current_q + alpha * (target - current_q)
    return {
        "old_q": current_q,
        "new_q": round(new_q, 6),
        "target": round(target, 6),
        "delta": round(new_q - current_q, 6),
        "ok": True,
        "note": "memrl utility_q_update",
    }


def value_aware_select(
    *,
    candidates: Sequence[dict[str, Any]],
    min_utility: float = 0.0,
) -> dict[str, Any]:
    """Pick highest-utility candidate above floor."""
    if not isinstance(candidates, Sequence) or isinstance(candidates, (str, bytes)):
        raise SchemaError("candidates sequence required")
    ranked = sorted(
        [c for c in candidates if isinstance(c, dict)],
        key=lambda x: float(x.get("utility") or 0.0),
        reverse=True,
    )
    chosen = None
    for c in ranked:
        if float(c.get("utility") or 0.0) >= min_utility:
            chosen = c
            break
    return {
        "chosen": chosen,
        "ranked_ids": [c.get("memory_id") for c in ranked],
        "ok": True,
        "note": "memrl value_aware_select",
    }


def semantic_vs_utility_warn(
    *,
    similarity: float,
    utility: float,
    sim_high: float = 0.7,
    util_low: float = 0.1,
) -> dict[str, Any]:
    """Flag 'similar ≠ useful' trap when high sim but low Q."""
    trap = similarity >= sim_high and utility <= util_low
    return {
        "trap": trap,
        "similarity": similarity,
        "utility": utility,
        "warn": "high_similarity_low_utility" if trap else None,
        "ok": True,
        "note": "memrl semantic_vs_utility_warn",
    }
