"""ReMe-shaped dynamic procedural memory (stdlib; no LLM).

Shaped by ReMe (arXiv:2512.10696 / ACL 2026 Findings): multi-faceted
distillation (success / failure / comparative), scenario-aware reuse,
utility-based refine (selective add + prune). Proxies only — not ReMe scores.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps

_TOKEN = re.compile(r"[a-z0-9_]{2,}", re.I)


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in _TOKEN.findall(text or "")}


def multi_faceted_distill(
    *,
    scenario: str,
    outcome: str,
    steps: Sequence[str] | None = None,
    failure_reason: str = "",
    peer_success: str = "",
) -> dict[str, Any]:
    """
    Distill structured experience from a trajectory.
    outcome: success | failure
    Returns success_pattern and/or failure_trigger plus optional comparative.
    """
    if outcome not in {"success", "failure"}:
        raise SchemaError("outcome must be success|failure")
    if not isinstance(scenario, str) or not scenario.strip():
        raise SchemaError("scenario required")
    step_list = [str(s).strip() for s in (steps or []) if str(s).strip()]
    facets: dict[str, Any] = {"scenario": scenario.strip()[:120]}
    if outcome == "success":
        pattern = (
            " → ".join(step_list[:6])
            if step_list
            else "repeat validated success path under matching scenario"
        )
        facets["success_pattern"] = pattern[:240]
        facets["kind"] = "success"
    else:
        trigger = failure_reason.strip() or "unspecified failure trigger"
        facets["failure_trigger"] = trigger[:240]
        facets["kind"] = "failure"
        if step_list:
            facets["failed_steps"] = step_list[:6]
    comparative = None
    if peer_success.strip() and outcome == "failure":
        comparative = (
            f"avoid: {facets.get('failure_trigger')}; prefer: {peer_success.strip()[:120]}"
        )
        facets["comparative_insight"] = comparative[:240]
    eid = hashlib.sha256(
        canonical_dumps(facets).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "experience_id": eid,
        "facets": facets,
        "usage_scenario": scenario.strip()[:80],
        "freq": 0,
        "utility": 0,
        "ok": True,
        "note": "reme multi_faceted_distill",
    }


def scenario_retrieve(
    pool: Sequence[Mapping[str, Any]],
    *,
    scenario: str,
    top_k: int = 3,
) -> dict[str, Any]:
    """Scenario-aware lexical retrieve from experience pool."""
    if not isinstance(scenario, str) or not scenario.strip():
        raise SchemaError("scenario required")
    qtok = _tokens(scenario)
    scored: list[tuple[int, dict[str, Any]]] = []
    for e in pool:
        if not isinstance(e, Mapping):
            continue
        blob = (
            f"{e.get('usage_scenario') or ''} "
            f"{(e.get('facets') or {}).get('success_pattern') or ''} "
            f"{(e.get('facets') or {}).get('failure_trigger') or ''} "
            f"{(e.get('facets') or {}).get('comparative_insight') or ''}"
        )
        score = len(qtok & _tokens(blob))
        scored.append((score, dict(e)))
    scored.sort(key=lambda x: (-x[0], str(x[1].get("experience_id") or "")))
    hits = [e for sc, e in scored[:top_k] if sc >= 0]
    return {
        "scenario": scenario.strip(),
        "hits": hits,
        "hit_count": len(hits),
        "ok": True,
        "note": "reme scenario_retrieve",
    }


def adaptive_rewrite_plan(
    experiences: Sequence[Mapping[str, Any]],
    *,
    new_scenario: str,
) -> dict[str, Any]:
    """Rewrite retrieved experiences into task-specific guidance (report-only)."""
    if not isinstance(new_scenario, str) or not new_scenario.strip():
        raise SchemaError("new_scenario required")
    lines: list[str] = []
    for e in experiences[:5]:
        if not isinstance(e, Mapping):
            continue
        facets = e.get("facets") if isinstance(e.get("facets"), Mapping) else {}
        if facets.get("success_pattern"):
            lines.append(f"APPLY: {facets['success_pattern']}")
        if facets.get("failure_trigger"):
            lines.append(f"AVOID: {facets['failure_trigger']}")
        if facets.get("comparative_insight"):
            lines.append(f"COMPARE: {facets['comparative_insight']}")
    guidance = (
        f"For scenario [{new_scenario.strip()[:80]}]: " + "; ".join(lines)
        if lines
        else f"No reusable guidance for [{new_scenario.strip()[:80]}]"
    )
    return {
        "new_scenario": new_scenario.strip(),
        "guidance": guidance[:500],
        "source_count": len(lines),
        "apply": False,
        "ok": True,
        "note": "reme adaptive_rewrite_plan",
    }


def utility_after_reuse(
    *,
    freq: int,
    utility: int,
    reuse_helped: bool,
) -> dict[str, Any]:
    """Update freq/utility counters after a reuse attempt."""
    if freq < 0 or utility < 0:
        raise SchemaError("freq/utility must be >= 0")
    new_freq = freq + 1
    new_util = utility + (1 if reuse_helped else 0)
    ratio = (new_util / new_freq) if new_freq else 0.0
    return {
        "freq": new_freq,
        "utility": new_util,
        "ratio": round(ratio, 4),
        "ok": True,
        "note": "reme utility_after_reuse",
    }


def selective_add_plan(
    pool: Sequence[Mapping[str, Any]],
    candidate: Mapping[str, Any],
    *,
    require_validated: bool = True,
    validated: bool = True,
) -> dict[str, Any]:
    """Selective addition — skip unvalidated or duplicate scenarios."""
    if not isinstance(candidate, Mapping):
        raise SchemaError("candidate mapping required")
    if require_validated and not validated:
        return {
            "action": "SKIP",
            "reason": "not_validated",
            "apply": False,
            "ok": True,
            "note": "reme selective_add_plan",
        }
    scen = str(candidate.get("usage_scenario") or "").strip().lower()
    for e in pool:
        if not isinstance(e, Mapping):
            continue
        if str(e.get("usage_scenario") or "").strip().lower() == scen and scen:
            return {
                "action": "SKIP",
                "reason": "duplicate_scenario",
                "existing_id": e.get("experience_id"),
                "apply": False,
                "ok": True,
                "note": "reme selective_add_plan",
            }
    return {
        "action": "ADD",
        "experience": dict(candidate),
        "apply": False,
        "ok": True,
        "note": "reme selective_add_plan",
    }


def utility_prune_plan(
    pool: Sequence[Mapping[str, Any]],
    *,
    alpha: int = 3,
    beta: float = 0.3,
) -> dict[str, Any]:
    """
    Prune when freq >= alpha and utility/freq < beta (ReMe Eq. 1 shaped).
    Report-only.
    """
    if alpha < 1:
        raise SchemaError("alpha must be >= 1")
    if not (0.0 <= beta <= 1.0):
        raise SchemaError("beta must be in [0,1]")
    keep: list[dict[str, Any]] = []
    prune: list[dict[str, Any]] = []
    for e in pool:
        if not isinstance(e, Mapping):
            continue
        freq = int(e.get("freq") or 0)
        util = int(e.get("utility") or 0)
        ratio = (util / freq) if freq else 1.0
        item = {
            "experience_id": e.get("experience_id"),
            "freq": freq,
            "utility": util,
            "ratio": round(ratio, 4),
        }
        if freq >= alpha and ratio < beta:
            prune.append(item)
        else:
            keep.append(item)
    return {
        "alpha": alpha,
        "beta": beta,
        "keep": keep,
        "prune": prune,
        "prune_count": len(prune),
        "apply": False,
        "ok": True,
        "note": "reme utility_prune_plan",
    }
