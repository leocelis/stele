"""Multiagent Debate proxies (stdlib; no LLM).

Shaped by Multiagent Debate (arXiv:2305.14325): propose, debate
rounds, converge on common answer. Proxies only — ≠ Meta-Prompting.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def mad_propose(*, agent: str, answer: str) -> dict[str, Any]:
    """One agent proposes an initial answer."""
    a = agent.strip()
    ans = answer.strip()
    if not a or not ans:
        raise SchemaError("agent and answer required")
    pid = hashlib.sha256(
        canonical_dumps({"a": a, "ans": ans}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "proposal_id": pid,
        "ok": True,
        "note": "mad mad_propose",
    }


def mad_debate(*, round_n: int, agents: int) -> dict[str, Any]:
    """Run one debate round across agents."""
    if round_n < 0:
        raise SchemaError("round_n must be >= 0")
    if agents < 2:
        raise SchemaError("agents must be >= 2")
    did = hashlib.sha256(
        canonical_dumps({"r": round_n, "a": agents}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "debate_id": did,
        "round": round_n,
        "agents": agents,
        "ok": True,
        "note": "mad mad_debate",
    }


def mad_critique(*, proposal_id: str, critique: str) -> dict[str, Any]:
    """Critique another agent's proposal."""
    pid = proposal_id.strip()
    c = critique.strip()
    if not pid or not c:
        raise SchemaError("proposal_id and critique required")
    cid = hashlib.sha256(
        canonical_dumps({"p": pid, "c": c}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "critique_id": cid,
        "ok": True,
        "note": "mad mad_critique",
    }


def mad_converge(*, common: bool) -> dict[str, Any]:
    """Flag convergence on a common final answer (report-only)."""
    return {
        "common": common,
        "apply": False,
        "ok": True,
        "note": "mad mad_converge",
    }


def mad_factuality(*, improved: bool) -> dict[str, Any]:
    """Flag factuality improvement from debate."""
    return {
        "improved": improved,
        "ok": True,
        "note": "mad mad_factuality",
    }


def mad_loop_plan(*, phase: str) -> dict[str, Any]:
    """Propose → debate → critique → converge."""
    order = ("propose", "debate", "critique", "converge")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "mad mad_loop_plan",
    }
