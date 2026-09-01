"""Recursion of Thought proxies (stdlib; no LLM).

Shaped by Recursion of Thought (arXiv:2306.06891): emit trigger tokens,
divide into sub-contexts, conquer, merge. Proxies only — ≠ Least-to-Most.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rot_trigger(*, token: str) -> dict[str, Any]:
    """Emit a special RoT context-operation trigger token."""
    t = token.strip()
    if not t:
        raise SchemaError("token required")
    tid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "trigger_id": tid,
        "ok": True,
        "note": "rot rot_trigger",
    }


def rot_divide(*, problem: str, parts: int) -> dict[str, Any]:
    """Divide a problem into multiple shorter contexts."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    if parts < 2:
        raise SchemaError("parts must be >= 2")
    did = hashlib.sha256(
        canonical_dumps({"p": p, "n": parts}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "divide_id": did,
        "parts": parts,
        "ok": True,
        "note": "rot rot_divide",
    }


def rot_conquer(*, divide_id: str, part: int) -> dict[str, Any]:
    """Solve one sub-context (proxy)."""
    did = divide_id.strip()
    if not did:
        raise SchemaError("divide_id required")
    if part < 0:
        raise SchemaError("part must be >= 0")
    cid = hashlib.sha256(
        canonical_dumps({"d": did, "p": part}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sub_id": cid,
        "part": part,
        "ok": True,
        "note": "rot rot_conquer",
    }


def rot_merge(*, parts: int) -> dict[str, Any]:
    """Merge sub-context results into a final answer."""
    if parts < 1:
        raise SchemaError("parts must be >= 1")
    return {
        "parts": parts,
        "ok": True,
        "note": "rot rot_merge",
    }


def rot_context_limit(*, within_limit: bool) -> dict[str, Any]:
    """Flag that each sub-context stays within the model limit (report-only)."""
    return {
        "within_limit": within_limit,
        "apply": False,
        "ok": True,
        "note": "rot rot_context_limit",
    }


def rot_loop_plan(*, phase: str) -> dict[str, Any]:
    """Trigger → divide → conquer → merge."""
    order = ("trigger", "divide", "conquer", "merge")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "trigger"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rot rot_loop_plan",
    }
