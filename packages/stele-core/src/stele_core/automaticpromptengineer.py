"""Automatic Prompt Engineer proxies (stdlib; no LLM).

Shaped by APE (arXiv:2211.01910): propose instruction candidates,
score/select the best for zero-shot steering. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ape_propose(*, demos: str) -> dict[str, Any]:
    """Propose instruction candidates from demonstrations."""
    d = demos.strip()
    if not d:
        raise SchemaError("demos required")
    pid = hashlib.sha256(
        canonical_dumps({"d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pool_id": pid,
        "ok": True,
        "note": "ape ape_propose",
    }


def ape_score(*, pool_id: str) -> dict[str, Any]:
    """Score instruction candidates via a chosen score function."""
    pid = pool_id.strip()
    if not pid:
        raise SchemaError("pool_id required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "ok": True,
        "note": "ape ape_score",
    }


def ape_select(*, score_id: str) -> dict[str, Any]:
    """Select the best-scoring instruction."""
    sid = score_id.strip()
    if not sid:
        raise SchemaError("score_id required")
    iid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "instr_id": iid,
        "ok": True,
        "note": "ape ape_select",
    }


def ape_steer(*, instr_id: str) -> dict[str, Any]:
    """Steer another model with the selected instruction (proxy)."""
    iid = instr_id.strip()
    if not iid:
        raise SchemaError("instr_id required")
    tid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "steer_id": tid,
        "ok": True,
        "note": "ape ape_steer",
    }


def ape_human(*, match_human: bool) -> dict[str, Any]:
    """Flag parity with human-authored instructions (report-only)."""
    return {
        "match_human": match_human,
        "apply": False,
        "ok": True,
        "note": "ape ape_human",
    }


def ape_loop_plan(*, phase: str) -> dict[str, Any]:
    """Propose → score → select → steer."""
    order = ("propose", "score", "select", "steer")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "propose"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ape ape_loop_plan",
    }
