"""Complexity-Based Prompting proxies (stdlib; no LLM).

Shaped by Complexity-Based Prompting (arXiv:2210.00720): select
high-complexity CoT exemplars, sample chains, vote on complex ones.
Proxies only — ≠ Auto-CoT / Active-Prompt.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def cbp_score(*, steps: int) -> dict[str, Any]:
    """Score reasoning complexity by intermediate step count."""
    if steps < 0:
        raise SchemaError("steps must be >= 0")
    return {
        "steps": steps,
        "ok": True,
        "note": "complexity cbp_score",
    }


def cbp_select(*, min_steps: int, exemplars: int) -> dict[str, Any]:
    """Select complex exemplars for the prompt."""
    if min_steps < 1:
        raise SchemaError("min_steps must be >= 1")
    if exemplars < 1:
        raise SchemaError("exemplars must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"m": min_steps, "e": exemplars}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "selection_id": sid,
        "min_steps": min_steps,
        "exemplars": exemplars,
        "ok": True,
        "note": "complexity cbp_select",
    }


def cbp_sample_chains(*, n: int) -> dict[str, Any]:
    """Sample multiple reasoning chains at decode time."""
    if n < 1:
        raise SchemaError("n must be >= 1")
    return {
        "n": n,
        "ok": True,
        "note": "complexity cbp_sample_chains",
    }


def cbp_vote_complex(*, prefer_complex: bool) -> dict[str, Any]:
    """Majority vote preferring complex chains (report-only)."""
    return {
        "prefer_complex": prefer_complex,
        "apply": False,
        "ok": True,
        "note": "complexity cbp_vote_complex",
    }


def cbp_robust(*, under_shift: bool) -> dict[str, Any]:
    """Flag robustness under format/distribution shift."""
    return {
        "under_shift": under_shift,
        "ok": True,
        "note": "complexity cbp_robust",
    }


def cbp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Score → select → sample → vote."""
    order = ("score", "select", "sample", "vote")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "score"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "complexity cbp_loop_plan",
    }
