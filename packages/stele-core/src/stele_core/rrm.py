"""RRM-shaped reflective retrieval memory (stdlib; no LLM).

Shaped by RRM (arXiv:2607.28156): procedural retrieval experience
(success/failure), query-level guidance only (never answer facts),
lifecycle utility + prune. Proxies only — not RRM paper scores.
"""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)
ANOMALIES = frozenset(
    {"empty_hits", "duplicate_query", "off_topic", "budget_exhausted", "none"}
)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def distill_retrieval_experience(
    *,
    query: str,
    outcome: str,
    anomaly: str = "none",
    strategy_hint: str = "",
) -> dict[str, Any]:
    """
    Distill procedural retrieval experience (not factual answers).
    outcome: success | failure
    """
    if outcome not in {"success", "failure"}:
        raise SchemaError("outcome must be success|failure")
    if anomaly not in ANOMALIES:
        raise SchemaError(f"anomaly must be one of {sorted(ANOMALIES)}")
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    if outcome == "success":
        pattern = strategy_hint.strip() or "broaden_then_narrow; require temporal anchors"
        bank = "M+"
    else:
        pattern = (
            strategy_hint.strip()
            or f"on_{anomaly}: reformulate orthogonal attributes; avoid near-duplicate queries"
        )
        bank = "M-"
    eid = hashlib.sha256(
        canonical_dumps(
            {"q": query, "outcome": outcome, "anomaly": anomaly, "p": pattern}
        ).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experience_id": eid,
        "bank": bank,
        "outcome": outcome,
        "anomaly": anomaly,
        "applicability": query.strip()[:80],
        "procedure": pattern[:240],
        "usage": 0,
        "reuse_success": 0,
        "ok": True,
        "note": "rrm distill_retrieval_experience — procedural only",
    }


def anomaly_trigger(
    *,
    hit_count: int = 0,
    prior_queries: Sequence[str] | None = None,
    current_query: str = "",
    rounds_used: int = 0,
    max_rounds: int = 5,
) -> dict[str, Any]:
    """Detect retrieval anomalies that should trigger experience reuse."""
    priors = [str(p).strip().lower() for p in (prior_queries or []) if p]
    cur = current_query.strip().lower()
    anomaly = "none"
    if hit_count <= 0:
        anomaly = "empty_hits"
    elif cur and cur in priors:
        anomaly = "duplicate_query"
    elif rounds_used >= max_rounds:
        anomaly = "budget_exhausted"
    elif cur and priors:
        # off_topic if near-zero token overlap with last query
        last = _tokens(priors[-1])
        now = _tokens(cur)
        if last and now and len(last & now) == 0:
            anomaly = "off_topic"
    return {
        "anomaly": anomaly,
        "triggered": anomaly != "none",
        "ok": True,
        "note": "rrm anomaly_trigger",
    }


def query_level_guidance(
    experiences: Sequence[Mapping[str, Any]],
    *,
    query: str,
    anomaly: str = "none",
) -> dict[str, Any]:
    """
    Convert experiences → retrieval focus (query-level only).
    Prefer M+; fall back to M- when anomaly matches.
    Never returns historical answers/facts as answer context.
    """
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query required")
    qtok = _tokens(query)
    succ: list[tuple[int, Mapping[str, Any]]] = []
    fail: list[tuple[int, Mapping[str, Any]]] = []
    for e in experiences:
        if not isinstance(e, Mapping):
            continue
        blob = f"{e.get('applicability') or ''} {e.get('procedure') or ''}"
        score = len(qtok & _tokens(blob))
        if e.get("bank") == "M+" or e.get("outcome") == "success":
            succ.append((score, e))
        else:
            # boost if anomaly matches
            if anomaly != "none" and str(e.get("anomaly") or "") == anomaly:
                score += 3
            fail.append((score, e))
    succ.sort(key=lambda x: (-x[0], str(x[1].get("experience_id") or "")))
    fail.sort(key=lambda x: (-x[0], str(x[1].get("experience_id") or "")))
    chosen: Mapping[str, Any] | None = None
    if succ and succ[0][0] >= 0:
        chosen = succ[0][1]
    elif fail and anomaly != "none":
        chosen = fail[0][1]
    focus = None
    if chosen:
        focus = {
            "search_direction": str(chosen.get("procedure") or "")[:160],
            "evidence_constraints": ["current_store_only", "no_historical_answers"],
            "source_experience_id": chosen.get("experience_id"),
            "bank": chosen.get("bank"),
        }
    return {
        "query": query.strip(),
        "anomaly": anomaly,
        "focus": focus,
        "answer_context_forbidden": True,
        "ok": True,
        "note": "rrm query_level_guidance — experiences never enter answer pack",
    }


def experience_lifecycle_score(
    *,
    usage: int = 0,
    reuse_success: int = 0,
    age_days: float = 0.0,
    half_life_days: float = 30.0,
) -> dict[str, Any]:
    """Utility ≈ reuse feedback × temporal decay."""
    if usage < 0 or reuse_success < 0:
        raise SchemaError("counts must be >= 0")
    if half_life_days <= 0:
        raise SchemaError("half_life_days must be > 0")
    feedback = (reuse_success / usage) if usage else 0.0
    decay = math.exp(-math.log(2) * float(age_days) / float(half_life_days))
    utility = (0.2 + 0.8 * feedback) * decay if usage else 0.15 * decay
    return {
        "utility": round(utility, 4),
        "feedback": round(feedback, 4),
        "decay": round(decay, 4),
        "usage": usage,
        "reuse_success": reuse_success,
        "age_days": age_days,
        "ok": True,
        "note": "rrm experience_lifecycle_score",
    }


def prune_experience_plan(
    experiences: Sequence[Mapping[str, Any]],
    *,
    capacity: int = 10,
    protect_new: int = 2,
) -> dict[str, Any]:
    """Prune lowest-utility experiences under capacity (report-only)."""
    if capacity < 1:
        raise SchemaError("capacity must be >= 1")
    scored: list[dict[str, Any]] = []
    for i, e in enumerate(experiences):
        if not isinstance(e, Mapping):
            continue
        life = experience_lifecycle_score(
            usage=int(e.get("usage") or 0),
            reuse_success=int(e.get("reuse_success") or 0),
            age_days=float(e.get("age_days") or i),
        )
        scored.append(
            {
                "experience_id": e.get("experience_id"),
                "utility": life["utility"],
                "bank": e.get("bank"),
                "is_new": i >= len(list(experiences)) - protect_new,
            }
        )
    # Prefer keeping new + high utility
    keepers = [s for s in scored if s.get("is_new")]
    rest = [s for s in scored if not s.get("is_new")]
    rest.sort(key=lambda x: (-float(x["utility"]), str(x.get("experience_id"))))
    need = max(0, capacity - len(keepers))
    keep = keepers + rest[:need]
    keep_ids = {str(k.get("experience_id")) for k in keep}
    prune = [s for s in scored if str(s.get("experience_id")) not in keep_ids]
    return {
        "capacity": capacity,
        "keep": keep,
        "prune": prune,
        "prune_count": len(prune),
        "apply": False,
        "ok": True,
        "note": "rrm prune_experience_plan",
    }


def isolate_factual_from_procedural(
    *,
    answer_pack_ids: Sequence[str],
    experience_ids: Sequence[str],
) -> dict[str, Any]:
    """Gate: answer pack must not contain reflective experience ids."""
    ans = {str(i) for i in answer_pack_ids if i}
    exp = {str(i) for i in experience_ids if i}
    leak = sorted(ans & exp)
    return {
        "isolated": len(leak) == 0,
        "leaked_ids": leak,
        "ok": True,
        "note": "rrm isolate_factual_from_procedural",
    }
