"""Least-to-Most-shaped decompose-then-solve (stdlib; no LLM).

Shaped by Least-to-Most Prompting (arXiv:2205.10625): decompose into
subproblems, solve in order, carry forward answers. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ltm_decompose(*, problem: str, n_subs: int) -> dict[str, Any]:
    """Decompose a hard problem into simpler subproblems."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    if n_subs < 1:
        raise SchemaError("n_subs must be >= 1")
    did = hashlib.sha256(
        canonical_dumps({"p": p, "n": n_subs}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "decomp_id": did,
        "n_subs": n_subs,
        "ok": True,
        "note": "ltm ltm_decompose",
    }


def ltm_solve_sub(*, decomp_id: str, sub_idx: int) -> dict[str, Any]:
    """Solve one subproblem by index."""
    did = decomp_id.strip()
    if not did:
        raise SchemaError("decomp_id required")
    if sub_idx < 0:
        raise SchemaError("sub_idx must be >= 0")
    sid = hashlib.sha256(
        canonical_dumps({"d": did, "i": sub_idx}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sub_id": sid,
        "sub_idx": sub_idx,
        "ok": True,
        "note": "ltm ltm_solve_sub",
    }


def ltm_carry_forward(*, answered: int) -> dict[str, Any]:
    """Carry prior sub-answers into the next prompt context."""
    if answered < 0:
        raise SchemaError("answered must be >= 0")
    return {
        "answered": answered,
        "ok": True,
        "note": "ltm ltm_carry_forward",
    }


def ltm_compose_final(*, subs_done: int) -> dict[str, Any]:
    """Compose final answer after all subproblems."""
    if subs_done < 0:
        raise SchemaError("subs_done must be >= 0")
    return {
        "subs_done": subs_done,
        "composed": True,
        "ok": True,
        "note": "ltm ltm_compose_final",
    }


def ltm_easy_to_hard(*, exemplars: int) -> dict[str, Any]:
    """Count easy exemplars used for hard generalization."""
    if exemplars < 0:
        raise SchemaError("exemplars must be >= 0")
    return {
        "exemplars": exemplars,
        "ok": True,
        "note": "ltm ltm_easy_to_hard",
    }


def ltm_loop_plan(*, phase: str) -> dict[str, Any]:
    """Decompose → solve → carry → compose."""
    order = ("decompose", "solve", "carry", "compose")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "decompose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ltm ltm_loop_plan",
    }
