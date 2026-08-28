"""ECHO-shaped selective turn memory (stdlib; no LLM / no RL).

Shaped by ECHO (arXiv:2606.31650): prune-to-act, trace-to-learn,
source-indexed reconstruction, provenance-guided credit.
Proxies only — not ECHO paper scores.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def write_turn_memory(
    *,
    source_turn_id: str,
    finding: str,
) -> dict[str, Any]:
    """Compress a completed turn into a source-indexed memory record."""
    sid = source_turn_id.strip()
    find = finding.strip()
    if not sid or not find:
        raise SchemaError("source_turn_id and finding required")
    mid = hashlib.sha256(
        canonical_dumps({"s": sid, "f": find}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "memory_id": mid,
        "source_turn_id": sid[:64],
        "finding": find[:160],
        "ok": True,
        "note": "echomem write_turn_memory",
    }


def select_turn_memories(
    *,
    memory_ids: Sequence[str],
    budget: int,
) -> dict[str, Any]:
    """Select up to budget memories (policy selects under binding budget)."""
    if budget < 0:
        raise SchemaError("budget must be >= 0")
    if not isinstance(memory_ids, Sequence) or isinstance(memory_ids, (str, bytes)):
        raise SchemaError("memory_ids sequence required")
    cleaned = [str(m).strip() for m in memory_ids if str(m).strip()]
    selected = cleaned[:budget]
    return {
        "selected": selected,
        "dropped": cleaned[budget:],
        "budget": budget,
        "ok": True,
        "note": "echomem select_turn_memories",
    }


def reconstruct_policy_context(
    *,
    selected_findings: Sequence[str],
    recent_turns: Sequence[str],
    max_chars: int = 400,
) -> dict[str, Any]:
    """Reconstruct bounded context from selected memories + recent turns."""
    if max_chars < 1:
        raise SchemaError("max_chars must be >= 1")
    if not isinstance(selected_findings, Sequence) or isinstance(
        selected_findings, (str, bytes)
    ):
        raise SchemaError("selected_findings sequence required")
    if not isinstance(recent_turns, Sequence) or isinstance(recent_turns, (str, bytes)):
        raise SchemaError("recent_turns sequence required")
    parts = [str(f).strip() for f in selected_findings if str(f).strip()]
    parts += [str(t).strip() for t in recent_turns if str(t).strip()]
    text = " | ".join(parts)[:max_chars]
    return {
        "context": text,
        "char_len": len(text),
        "within_budget": len(text) <= max_chars,
        "ok": True,
        "note": "echomem reconstruct_policy_context",
    }


def provenance_credit_mask(
    *,
    source_turn_ids: Sequence[str],
    selected_source_ids: Sequence[str],
    outcome_positive: bool,
) -> dict[str, Any]:
    """Route positive outcome credit only through selected source turns."""
    if not isinstance(source_turn_ids, Sequence) or isinstance(
        source_turn_ids, (str, bytes)
    ):
        raise SchemaError("source_turn_ids sequence required")
    if not isinstance(selected_source_ids, Sequence) or isinstance(
        selected_source_ids, (str, bytes)
    ):
        raise SchemaError("selected_source_ids sequence required")
    selected = {str(s).strip() for s in selected_source_ids if str(s).strip()}
    mask: dict[str, bool] = {}
    for tid in source_turn_ids:
        t = str(tid).strip()
        if not t:
            continue
        mask[t] = bool(outcome_positive and t in selected)
    return {
        "credit_mask": mask,
        "credited_count": sum(1 for v in mask.values() if v),
        "ok": True,
        "note": "echomem provenance_credit_mask",
    }


def history_collapse_gate(
    *,
    collapsed_summary_only: bool,
) -> dict[str, Any]:
    """Reject global history collapse (ECHO keeps source-addressable set)."""
    return {
        "allow_collapse": False if collapsed_summary_only else True,
        "reject_collapse": collapsed_summary_only,
        "apply": False,
        "ok": True,
        "note": "echomem history_collapse_gate",
    }


def budget_binding_check(
    *,
    history_chars: int,
    budget_chars: int,
) -> dict[str, Any]:
    """Whether context budget is binding (triggers selective reconstruction)."""
    if history_chars < 0 or budget_chars < 1:
        raise SchemaError("history_chars >= 0 and budget_chars >= 1")
    binding = history_chars > budget_chars
    return {
        "binding": binding,
        "overflow": max(0, history_chars - budget_chars),
        "ok": True,
        "note": "echomem budget_binding_check",
    }
