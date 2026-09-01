"""MemR3-shaped reflective retrieval + evidence-gap tracker (stdlib; no LLM).

Closed loop: retrieve → gap report → suggest next probes. Proxies only —
not MemR3 paper scores.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from stele_core.index.lexical import tokenize
from stele_core.schema import SchemaError


def evidence_gap(
    query: str,
    hits: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Compare query tokens/digits to retrieved bodies; list uncovered needs.
    """
    q = str(query or "").strip()
    if not q:
        raise SchemaError("query is required")
    q_tokens = set(tokenize(q))
    q_digits = set(re.findall(r"\d+", q))
    covered_tok: set[str] = set()
    covered_dig: set[str] = set()
    for h in hits:
        blob = f"{h.get('title') or ''}\n{h.get('body') or ''}"
        covered_tok |= set(tokenize(blob))
        covered_dig |= set(re.findall(r"\d+", blob))
    missing_tok = sorted(q_tokens - covered_tok)
    missing_dig = sorted(q_digits - covered_dig)
    gaps: list[dict[str, Any]] = []
    for t in missing_tok:
        gaps.append({"kind": "token", "value": t})
    for d in missing_dig:
        gaps.append({"kind": "digit", "value": d})
    if not hits:
        gaps.append({"kind": "empty_hits", "value": "*"})
    coverage = 1.0
    if q_tokens:
        coverage = len(q_tokens & covered_tok) / len(q_tokens)
    return {
        "query": q,
        "gaps": gaps,
        "gap_count": len(gaps),
        "coverage": round(coverage, 4),
        "hit_ids": [str(h.get("id")) for h in hits],
        "closed": len(gaps) == 0,
        "note": "MemR3 evidence-gap proxy — not reflective LLM reasoning",
    }


def suggest_probes(
    query: str,
    gaps: Sequence[Mapping[str, Any]],
    *,
    max_probes: int = 5,
) -> list[str]:
    """Build follow-up retrieval probes from uncovered tokens/digits."""
    probes: list[str] = []
    base = str(query or "").strip()
    for g in gaps:
        kind = str(g.get("kind") or "")
        val = str(g.get("value") or "").strip()
        if not val or val == "*":
            if base and base not in probes:
                probes.append(base)
            continue
        if kind == "digit":
            probes.append(f"{base} {val}".strip())
        elif kind == "token":
            probes.append(val if not base else f"{val} {base}")
        if len(probes) >= max(1, int(max_probes)):
            break
    # unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for p in probes:
        p = " ".join(p.split())
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def reflective_retrieve_plan(
    query: str,
    hits: Sequence[Mapping[str, Any]],
    *,
    coverage_target: float = 0.85,
    max_rounds: int = 3,
) -> dict[str, Any]:
    """
    One-shot MemR3-shaped plan: gap + next probes + whether another round needed.
    """
    if not (0 < coverage_target <= 1):
        raise SchemaError("coverage_target must be in (0, 1]")
    gap = evidence_gap(query, hits)
    probes = suggest_probes(query, gap.get("gaps") or [])
    need_another = (
        not gap.get("closed")
        and float(gap.get("coverage") or 0) < coverage_target
        and bool(probes)
    )
    return {
        "query": query,
        "round": 1,
        "max_rounds": max_rounds,
        "gap": gap,
        "next_probes": probes,
        "continue": need_another,
        "coverage_target": coverage_target,
        "note": "MemR3 reflective plan — caller runs next Select with probes",
    }


def gap_tracker_update(
    prior_gaps: Sequence[Mapping[str, Any]],
    new_hits: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    """
    Update a global evidence-gap tracker after a follow-up retrieve.
    """
    remaining: list[dict[str, Any]] = []
    blob = "\n".join(
        f"{h.get('title') or ''}\n{h.get('body') or ''}" for h in new_hits
    )
    blob_l = blob.lower()
    digits = set(re.findall(r"\d+", blob))
    toks = set(tokenize(blob))
    resolved: list[dict[str, Any]] = []
    for g in prior_gaps:
        kind = str(g.get("kind") or "")
        val = str(g.get("value") or "")
        done = False
        if kind == "digit" and val in digits:
            done = True
        elif kind == "token" and val.lower() in toks:
            done = True
        elif kind == "empty_hits" and new_hits:
            done = True
        elif val and val.lower() in blob_l:
            done = True
        if done:
            resolved.append(dict(g))
        else:
            remaining.append(dict(g))
    return {
        "resolved": resolved,
        "remaining": remaining,
        "resolved_count": len(resolved),
        "remaining_count": len(remaining),
        "closed": len(remaining) == 0,
        "note": "MemR3 gap tracker update after follow-up retrieve",
    }
