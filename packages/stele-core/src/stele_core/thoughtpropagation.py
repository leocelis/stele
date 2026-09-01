"""Thought Propagation proxies (stdlib; no LLM).

Shaped by Thought Propagation (arXiv:2310.03965): propose analogous
problems → solve → reuse insights → amend scratch solution. Proxies only.

Prefix ``tprop_*`` — not Program-of-Thoughts / Progressive-Hint.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def tprop_propose(*, problem: str) -> dict[str, Any]:
    """Propose analogous problems related to the input."""
    p = problem.strip()
    if not p:
        raise SchemaError("problem required")
    pid = hashlib.sha256(
        canonical_dumps({"p": p}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "propose_id": pid,
        "ok": True,
        "note": "tprop tprop_propose",
    }


def tprop_solve(*, propose_id: str) -> dict[str, Any]:
    """Solve the analogous problem set."""
    pid = propose_id.strip()
    if not pid:
        raise SchemaError("propose_id required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "analog_id": sid,
        "ok": True,
        "note": "tprop tprop_solve",
    }


def tprop_reuse(*, analog_id: str) -> dict[str, Any]:
    """Reuse analogous solutions / strategies."""
    aid = analog_id.strip()
    if not aid:
        raise SchemaError("analog_id required")
    rid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "reuse_id": rid,
        "ok": True,
        "note": "tprop tprop_reuse",
    }


def tprop_amend(*, reuse_id: str) -> dict[str, Any]:
    """Amend scratch solution with propagated insights."""
    rid = reuse_id.strip()
    if not rid:
        raise SchemaError("reuse_id required")
    mid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "amend_id": mid,
        "ok": True,
        "note": "tprop tprop_amend",
    }


def tprop_compat(*, plug_and_play: bool) -> dict[str, Any]:
    """Flag compatibility with other prompting methods (report-only)."""
    return {
        "plug_and_play": plug_and_play,
        "apply": False,
        "ok": True,
        "note": "tprop tprop_compat",
    }


def tprop_loop_plan(*, phase: str) -> dict[str, Any]:
    """Propose → solve → reuse → amend."""
    order = ("propose", "solve", "reuse", "amend")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "tprop tprop_loop_plan",
    }
