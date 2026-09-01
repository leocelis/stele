"""AgentCoder-shaped multi-agent code loop (stdlib; no LLM).

Shaped by AgentCoder (arXiv:2312.13010): programmer, test designer,
test executor, refine from feedback. Proxies only — no real exec.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ac_programmer(*, requirement: str) -> dict[str, Any]:
    """Programmer agent emits a code candidate (proxy id)."""
    r = requirement.strip()
    if not r:
        raise SchemaError("requirement required")
    cid = hashlib.sha256(
        canonical_dumps({"r": r}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "code_id": cid,
        "ok": True,
        "note": "agentcoder ac_programmer",
    }


def ac_test_designer(*, requirement: str, cases: int) -> dict[str, Any]:
    """Test designer agent emits test cases from requirements."""
    r = requirement.strip()
    if not r:
        raise SchemaError("requirement required")
    if cases < 1:
        raise SchemaError("cases must be >= 1")
    tid = hashlib.sha256(
        canonical_dumps({"r": r, "c": cases}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "suite_id": tid,
        "cases": cases,
        "ok": True,
        "note": "agentcoder ac_test_designer",
    }


def ac_test_executor(*, code_id: str, suite_id: str) -> dict[str, Any]:
    """Test executor runs suite against code (proxy; report-only)."""
    cid = code_id.strip()
    sid = suite_id.strip()
    if not cid or not sid:
        raise SchemaError("code_id and suite_id required")
    fid = hashlib.sha256(
        canonical_dumps({"c": cid, "s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "feedback_id": fid,
        "apply": False,
        "ok": True,
        "note": "agentcoder ac_test_executor",
    }


def ac_refine(*, code_id: str, feedback_id: str) -> dict[str, Any]:
    """Programmer refines code from executor feedback."""
    cid = code_id.strip()
    fid = feedback_id.strip()
    if not cid or not fid:
        raise SchemaError("code_id and feedback_id required")
    rid = hashlib.sha256(
        canonical_dumps({"c": cid, "f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "refined_id": rid,
        "ok": True,
        "note": "agentcoder ac_refine",
    }


def ac_pass_gate(*, all_pass: bool) -> dict[str, Any]:
    """Stop when all tests pass (report-only)."""
    return {
        "all_pass": all_pass,
        "apply": False,
        "ok": True,
        "note": "agentcoder ac_pass_gate",
    }


def ac_loop_plan(*, phase: str) -> dict[str, Any]:
    """Program → design → execute → refine."""
    order = ("program", "design", "execute", "refine")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "program"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "agentcoder ac_loop_plan",
    }
