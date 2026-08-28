"""Faithful CoT-shaped translate+solve (stdlib; no LLM).

Shaped by Faithful Chain-of-Thought (arXiv:2301.13379): translate NL
to symbolic chain, deterministic solve, faithfulness guarantee.
Proxies only — ≠ PAL / PoT.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def fcot_translate(*, query: str, symbolic: str) -> dict[str, Any]:
    """Translate NL query into a symbolic reasoning chain."""
    q = query.strip()
    s = symbolic.strip()
    if not q or not s:
        raise SchemaError("query and symbolic required")
    cid = hashlib.sha256(
        canonical_dumps({"q": q, "s": s}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "chain_id": cid,
        "ok": True,
        "note": "faithfulcot fcot_translate",
    }


def fcot_solve(*, chain_id: str) -> dict[str, Any]:
    """Deterministic solver executes the chain (proxy; report-only)."""
    cid = chain_id.strip()
    if not cid:
        raise SchemaError("chain_id required")
    aid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": aid,
        "apply": False,
        "ok": True,
        "note": "faithfulcot fcot_solve",
    }


def fcot_faithfulness(*, chain_explains: bool) -> dict[str, Any]:
    """Flag that the chain faithfully explains the answer."""
    return {
        "chain_explains": chain_explains,
        "ok": True,
        "note": "faithfulcot fcot_faithfulness",
    }


def fcot_interleave(*, nl_sl: bool) -> dict[str, Any]:
    """Flag NL interleaved with symbolic language in the chain."""
    return {
        "nl_sl": nl_sl,
        "ok": True,
        "note": "faithfulcot fcot_interleave",
    }


def fcot_vs_cot(*, faithful_beats: bool) -> dict[str, Any]:
    """Flag Faithful CoT vs standard CoT."""
    return {
        "faithful_beats": faithful_beats,
        "ok": True,
        "note": "faithfulcot fcot_vs_cot",
    }


def fcot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Translate → solve → faithfulness → flag."""
    order = ("translate", "solve", "faithfulness", "flag")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "translate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "faithfulcot fcot_loop_plan",
    }
