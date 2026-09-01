"""BEAM + HaluMem-shaped evaluation proxies (stdlib; no LLM).

Shaped by:
- BEAM benchmark categories (preference, knowledge update, abstention,
  contradiction, temporal, event ordering, multi-session, …)
- HaluMem (arXiv:2511.03506) — operation-level hallucination stages:
  extraction / updating / QA.

Proxies only — not BEAM or HaluMem paper scores.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError

BEAM_CATEGORIES = frozenset(
    {
        "preference_following",
        "instruction_following",
        "information_extraction",
        "knowledge_update",
        "multi_session_reasoning",
        "summarization",
        "temporal_reasoning",
        "event_ordering",
        "abstention",
        "contradiction_resolution",
    }
)

HALU_STAGES = frozenset({"extraction", "updating", "qa"})


def beam_category_inventory() -> dict[str, Any]:
    """BEAM ten-category inventory."""
    return {
        "categories": sorted(BEAM_CATEGORIES),
        "count": len(BEAM_CATEGORIES),
        "ok": True,
        "note": "beam beam_category_inventory",
    }


def classify_beam_query(query: str) -> dict[str, Any]:
    """Map a query to the closest BEAM evaluation category (lexical)."""
    if not isinstance(query, str) or not query.strip():
        raise SchemaError("query string is required")
    q = query.lower()
    rules: list[tuple[str, tuple[str, ...]]] = [
        ("abstention", ("don't know", "unknown", "insufficient", "cannot answer", "abstain")),
        ("contradiction_resolution", ("contradict", "conflict", "which is true", "inconsist")),
        ("knowledge_update", ("now prefers", "changed to", "updated", "no longer", "instead of")),
        ("event_ordering", ("before", "after", "first", "then", "sequence", "order of")),
        ("temporal_reasoning", ("when did", "what date", "how long ago", "timeline")),
        ("multi_session_reasoning", ("last session", "previous chat", "across sessions", "earlier week")),
        ("preference_following", ("prefer", "like me to", "my style", "always respond")),
        ("instruction_following", ("must", "do not", "follow these rules", "instructions:")),
        ("summarization", ("summarize", "summary", "tldr", "overview")),
        ("information_extraction", ("what is", "who is", "extract", "list the")),
    ]
    for cat, phrases in rules:
        if any(p in q for p in phrases):
            return {
                "category": cat,
                "query": query.strip(),
                "ok": True,
                "note": "beam classify_beam_query",
            }
    return {
        "category": "information_extraction",
        "query": query.strip(),
        "ok": True,
        "note": "beam classify_beam_query — default",
    }


def knowledge_update_check(
    *,
    prior: str,
    current: str,
) -> dict[str, Any]:
    """Detect whether current supersedes prior (knowledge-update category)."""
    if not isinstance(prior, str) or not isinstance(current, str):
        raise SchemaError("prior and current strings required")
    p = prior.strip().lower()
    c = current.strip().lower()
    changed = p != c and bool(p) and bool(c)
    supersede_cues = any(
        w in c for w in ("now", "instead", "updated", "no longer", "from now")
    )
    return {
        "changed": changed,
        "supersede_signal": supersede_cues,
        "should_prefer_current": changed,
        "ok": True,
        "note": "beam knowledge_update_check",
    }


def abstention_gate(
    *,
    query: str,
    evidence_count: int,
    min_evidence: int = 1,
) -> dict[str, Any]:
    """Abstain when evidence is insufficient (BEAM abstention)."""
    if not isinstance(query, str):
        raise SchemaError("query string required")
    if evidence_count < 0:
        raise SchemaError("evidence_count must be >= 0")
    abstain = evidence_count < min_evidence
    force = any(
        w in query.lower()
        for w in ("if unknown", "say you don't know", "abstain when unsure")
    )
    return {
        "abstain": abstain or (force and evidence_count == 0),
        "evidence_count": evidence_count,
        "min_evidence": min_evidence,
        "ok": True,
        "note": "beam abstention_gate",
    }


def contradiction_resolve_plan(
    statements: Sequence[Mapping[str, Any] | str],
) -> dict[str, Any]:
    """Plan contradiction resolution without auto-collapse (preserve contested)."""
    if not isinstance(statements, Sequence) or isinstance(statements, (str, bytes)):
        raise SchemaError("statements sequence required")
    norms: list[dict[str, Any]] = []
    for i, s in enumerate(statements):
        if isinstance(s, str):
            norms.append({"id": f"s{i}", "text": s.strip()})
        elif isinstance(s, Mapping):
            norms.append(
                {
                    "id": str(s.get("id") or f"s{i}"),
                    "text": str(s.get("text") or s.get("body") or "").strip(),
                }
            )
    pairs: list[dict[str, Any]] = []
    for i, a in enumerate(norms):
        for b in norms[i + 1 :]:
            ta, tb = a["text"].lower(), b["text"].lower()
            if not ta or not tb or ta == tb:
                continue
            # Negation / opposite cue heuristic
            oppose = (
                ("never" in ta and "always" in tb)
                or ("always" in ta and "never" in tb)
                or ("not " in ta and ta.replace("not ", "") in tb)
                or ("not " in tb and tb.replace("not ", "") in ta)
            )
            # Shared tokens but different polarity words
            shared = set(ta.split()) & set(tb.split())
            if oppose or (len(shared) >= 2 and ta != tb):
                pairs.append(
                    {
                        "a": a["id"],
                        "b": b["id"],
                        "action": "preserve_contested",
                        "collapse": False,
                    }
                )
    return {
        "pair_count": len(pairs),
        "pairs": pairs,
        "apply": False,
        "ok": True,
        "note": "beam contradiction_resolve_plan — never auto-collapse",
    }


def event_order_check(
    events: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Check whether event timestamps are non-decreasing (event ordering)."""
    if not isinstance(events, Sequence) or isinstance(events, (str, bytes)):
        raise SchemaError("events sequence required")
    times: list[tuple[str, str]] = []
    for e in events:
        if not isinstance(e, Mapping):
            continue
        eid = str(e.get("id") or e.get("title") or "")
        t = str(e.get("time") or e.get("valid_from") or e.get("created_at") or "")
        if t:
            times.append((eid, t))
    ordered = all(times[i][1] <= times[i + 1][1] for i in range(len(times) - 1))
    return {
        "event_count": len(times),
        "ordered": ordered,
        "sequence": [{"id": i, "time": t} for i, t in times],
        "ok": True,
        "note": "beam event_order_check",
    }


def localize_hallucination_stage(
    *,
    symptom: str,
    context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """HaluMem-shaped stage localization: extraction | updating | qa."""
    if not isinstance(symptom, str) or not symptom.strip():
        raise SchemaError("symptom string required")
    s = symptom.lower()
    ctx = context or {}
    stage = "qa"
    if any(w in s for w in ("extracted", "wrote wrong", "fabricated memory", "invented fact")):
        stage = "extraction"
    if any(w in s for w in ("update overwrote", "stale replace", "merge error", "failed update")):
        stage = "updating"
    if any(w in s for w in ("answered without", "retrieval miss", "wrong recall", "hallucinated answer")):
        stage = "qa"
    # Context overrides
    if ctx.get("write_time_error"):
        stage = "extraction"
    if ctx.get("update_time_error"):
        stage = "updating"
    return {
        "stage": stage,
        "symptom": symptom.strip(),
        "ok": stage in HALU_STAGES,
        "note": "halumem localize_hallucination_stage — operation-level proxy",
    }


def beam_eval_pack(
    cases: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """Score a small pack of shaped BEAM-like cases (local CI oracle)."""
    if not isinstance(cases, Sequence) or isinstance(cases, (str, bytes)):
        raise SchemaError("cases sequence required")
    results: list[dict[str, Any]] = []
    for c in cases:
        if not isinstance(c, Mapping):
            continue
        cat = str(c.get("category") or classify_beam_query(str(c.get("query") or ""))["category"])
        expected = c.get("expected")
        observed = c.get("observed")
        passed = expected == observed if expected is not None else bool(c.get("pass"))
        results.append(
            {
                "id": c.get("id"),
                "category": cat,
                "pass": bool(passed),
            }
        )
    total = len(results)
    wins = sum(1 for r in results if r["pass"])
    return {
        "case_count": total,
        "pass_count": wins,
        "pass_rate": round(wins / total, 4) if total else 0.0,
        "results": results,
        "ok": True,
        "note": "beam beam_eval_pack — local proxy, not BEAM scores",
    }
