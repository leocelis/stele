"""Hint-before-Solving Prompting proxies (stdlib; no LLM).

Shaped by HSP (arXiv:2402.14310): emit hints (knowledge/key ideas)
before intermediate reasoning and the final answer. Proxies only.

Prefix ``hsp_*`` — orthogonal to CoT / Least-to-Most / Plan-and-Solve.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def hsp_hint(*, problem: str) -> dict[str, Any]:
    """Generate hints (knowledge or key ideas) before solving."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    hid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "hint_id": hid,
        "ok": True,
        "note": "hsp hsp_hint",
    }


def hsp_solve(*, hint_id: str) -> dict[str, Any]:
    """Generate intermediate reasoning guided by hints."""
    hid = hint_id.strip()
    if not hid:
        raise SchemaError("hint_id required")
    sid = hashlib.sha256(
        canonical_dumps({"h": hid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "solve_id": sid,
        "ok": True,
        "note": "hsp hsp_solve",
    }


def hsp_answer(*, solve_id: str) -> dict[str, Any]:
    """Emit the final answer after hint-guided solving."""
    sid = solve_id.strip()
    if not sid:
        raise SchemaError("solve_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "answer_id": aid,
        "ok": True,
        "note": "hsp hsp_answer",
    }


def hsp_compose(*, base: str) -> dict[str, Any]:
    """Compose HSP with a base prompting method (cot/ltm/ps/standard)."""
    b = base.strip().lower()
    allowed = ("cot", "ltm", "ps", "standard")
    if b not in allowed:
        raise SchemaError(f"base must be one of {list(allowed)}")
    return {
        "base": b,
        "ok": True,
        "note": "hsp hsp_compose",
    }


def hsp_quality(*, high_quality: bool) -> dict[str, Any]:
    """Flag high-quality hint enhancement (report-only)."""
    return {
        "high_quality": high_quality,
        "apply": False,
        "ok": True,
        "note": "hsp hsp_quality",
    }


def hsp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Hint → solve → answer → compose."""
    order = ("hint", "solve", "answer", "compose")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "hint"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "hsp hsp_loop_plan",
    }
