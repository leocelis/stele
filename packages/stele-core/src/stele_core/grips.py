"""GrIPS proxies (stdlib; no LLM).

Shaped by GrIPS (arXiv:2203.07281): gradient-free, edit-based local
search over instructional prompts (add/paraphrase/swap/delete phrases).
Proxies only.

Prefix ``grips_*`` — not MAPO (``mapo_*``) / ProTeGi (``ptg_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def grips_seed(*, instruction: str) -> dict[str, Any]:
    """Seed search from a human-readable instructional prompt."""
    i = instruction.strip()
    if not i:
        raise SchemaError("instruction required")
    sid = hashlib.sha256(
        canonical_dumps({"i": i}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "seed_id": sid,
        "ok": True,
        "note": "grips grips_seed",
    }


def grips_edit(*, seed_id: str, op: str) -> dict[str, Any]:
    """Apply a phrase-level edit op (add|paraphrase|swap|delete)."""
    sid = seed_id.strip()
    if not sid:
        raise SchemaError("seed_id required")
    allowed = ("add", "paraphrase", "swap", "delete")
    if op not in allowed:
        raise SchemaError(f"op must be one of {list(allowed)}")
    eid = hashlib.sha256(
        canonical_dumps({"s": sid, "o": op}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edit_id": eid,
        "op": op,
        "ok": True,
        "note": "grips grips_edit",
    }


def grips_score(*, edit_id: str, score: int) -> dict[str, Any]:
    """Score an edited instruction on the task set (0–100)."""
    eid = edit_id.strip()
    if not eid:
        raise SchemaError("edit_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    tid = hashlib.sha256(
        canonical_dumps({"e": eid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": tid,
        "score": score,
        "ok": True,
        "note": "grips grips_score",
    }


def grips_accept(*, score_id: str) -> dict[str, Any]:
    """Accept an improved edit into the current prompt."""
    sid = score_id.strip()
    if not sid:
        raise SchemaError("score_id required")
    aid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "accept_id": aid,
        "ok": True,
        "note": "grips grips_accept",
    }


def grips_api(*, api_tunable: bool) -> dict[str, Any]:
    """Flag API-based (gradient-free) tuning suitability (report-only)."""
    return {
        "api_tunable": api_tunable,
        "apply": False,
        "ok": True,
        "note": "grips grips_api",
    }


def grips_loop_plan(*, phase: str) -> dict[str, Any]:
    """Seed → edit → score → accept."""
    order = ("seed", "edit", "score", "accept")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "seed"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "grips grips_loop_plan",
    }
