"""R-Zero-shaped Challenger–Solver co-evolution (stdlib; no LLM / no GRPO).

Shaped by R-Zero (arXiv:2508.05004): Challenger uncertainty reward near
50% Solver accuracy, majority-vote filter band, co-evolve rounds.
Proxies only — not R-Zero paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def challenger_propose(
    *,
    question: str,
) -> dict[str, Any]:
    """Challenger emits a synthetic question (format-gated)."""
    q = question.strip()
    if not q:
        raise SchemaError("question required")
    # Format check proxy: prefer <question>...</question> or plain text ok
    formatted = q.startswith("<question>") and q.endswith("</question>")
    body = q
    if formatted:
        body = q[len("<question>") : -len("</question>")].strip()
    if not body:
        return {
            "accepted": False,
            "reason": "empty_after_tags",
            "ok": True,
            "note": "rzero challenger_propose",
        }
    qid = hashlib.sha256(
        canonical_dumps({"q": body}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "question_id": qid,
        "question": body[:200],
        "accepted": True,
        "formatted": formatted,
        "ok": True,
        "note": "rzero challenger_propose",
    }


def uncertainty_reward(
    *,
    empirical_accuracy: float,
) -> dict[str, Any]:
    """r ∝ 1 − 2|p̂ − 1/2| — max at 50% Solver accuracy."""
    if not (0.0 <= empirical_accuracy <= 1.0):
        raise SchemaError("empirical_accuracy must be in [0, 1]")
    r = 1.0 - 2.0 * abs(empirical_accuracy - 0.5)
    return {
        "r_uncertainty": round(max(0.0, r), 4),
        "at_edge": abs(empirical_accuracy - 0.5) <= 0.1,
        "ok": True,
        "note": "rzero uncertainty_reward",
    }


def majority_vote_label(
    *,
    answers: Sequence[str],
) -> dict[str, Any]:
    """Pseudo-label via majority vote among Solver answers."""
    if not isinstance(answers, Sequence) or isinstance(answers, (str, bytes)):
        raise SchemaError("answers sequence required")
    cleaned = [str(a).strip() for a in answers if str(a).strip()]
    if not cleaned:
        raise SchemaError("answers required")
    counts: dict[str, int] = {}
    for a in cleaned:
        counts[a] = counts.get(a, 0) + 1
    label = max(counts, key=lambda k: counts[k])
    acc = counts[label] / len(cleaned)
    return {
        "pseudo_label": label[:120],
        "empirical_accuracy": round(acc, 4),
        "vote_count": counts[label],
        "ok": True,
        "note": "rzero majority_vote_label",
    }


def curriculum_band_filter(
    *,
    empirical_accuracy: float,
    delta: float = 0.2,
) -> dict[str, Any]:
    """Keep if |p̂ − 1/2| ≤ δ (neither too easy nor too hard)."""
    if not (0.0 <= empirical_accuracy <= 1.0):
        raise SchemaError("empirical_accuracy must be in [0, 1]")
    if delta < 0:
        raise SchemaError("delta must be >= 0")
    keep = abs(empirical_accuracy - 0.5) <= delta
    return {
        "keep": keep,
        "empirical_accuracy": empirical_accuracy,
        "delta": delta,
        "ok": True,
        "note": "rzero curriculum_band_filter",
    }


def solver_binary_reward(
    *,
    answer: str,
    pseudo_label: str,
) -> dict[str, Any]:
    """Solver GRPO binary reward vs majority pseudo-label."""
    match = answer.strip() == pseudo_label.strip()
    return {
        "r_solver": 1.0 if match else 0.0,
        "match": match,
        "ok": True,
        "note": "rzero solver_binary_reward",
    }


def coevolve_round_plan(
    *,
    round_index: int,
    challenger_updated: bool,
    solver_updated: bool,
) -> dict[str, Any]:
    """One co-evolve round: Challenger then Solver (order gate)."""
    if round_index < 0:
        raise SchemaError("round_index must be >= 0")
    # Challenger trains first with frozen Solver; then Solver with frozen Challenger
    order_ok = (not solver_updated) or challenger_updated
    return {
        "round_index": round_index,
        "order_ok": order_ok,
        "next": "solver" if challenger_updated and not solver_updated else "challenger",
        "apply": False,
        "ok": True,
        "note": "rzero coevolve_round_plan",
    }
