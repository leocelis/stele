"""Analogical Prompting proxies (stdlib; no LLM).

Shaped by Analogical Prompting (arXiv:2310.01714): self-generate
exemplars/knowledge, then solve. Proxies only — ≠ Auto-CoT / Active-Prompt.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ana_recall(*, problem: str) -> dict[str, Any]:
    """Self-generate a relevant past-experience exemplar."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    rid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "exemplar_id": rid,
        "ok": True,
        "note": "analogical ana_recall",
    }


def ana_knowledge(*, problem: str, facts: int) -> dict[str, Any]:
    """Self-generate relevant knowledge before solving."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    if facts < 0:
        raise SchemaError("facts must be >= 0")
    kid = hashlib.sha256(
        canonical_dumps({"p": p, "f": facts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "knowledge_id": kid,
        "facts": facts,
        "ok": True,
        "note": "analogical ana_knowledge",
    }


def ana_solve(*, exemplar_id: str) -> dict[str, Any]:
    """Solve the target using recalled exemplars (proxy)."""
    eid = exemplar_id.strip()
    if not eid:
        raise SchemaError("exemplar_id required")
    sid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": sid,
        "ok": True,
        "note": "analogical ana_solve",
    }


def ana_adapt(*, tailored: bool) -> dict[str, Any]:
    """Flag that exemplars are tailored per problem."""
    return {
        "tailored": tailored,
        "ok": True,
        "note": "analogical ana_adapt",
    }


def ana_no_label(*, needs_labels: bool) -> dict[str, Any]:
    """Flag that no manual labels/retrieval are required (report-only)."""
    return {
        "needs_labels": needs_labels,
        "apply": False,
        "ok": True,
        "note": "analogical ana_no_label",
    }


def ana_loop_plan(*, phase: str) -> dict[str, Any]:
    """Recall → knowledge → solve → adapt."""
    order = ("recall", "knowledge", "solve", "adapt")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "recall"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "analogical ana_loop_plan",
    }
