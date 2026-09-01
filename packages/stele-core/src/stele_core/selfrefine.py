"""Self-Refine proxies (stdlib; no LLM).

Shaped by SELF-REFINE (arXiv:2303.17651): generate → feedback → refine
iteratively with the same model. Proxies only.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def sr_generate(*, draft: str) -> dict[str, Any]:
    """Initial output generation."""
    d = draft.strip()
    if not d:
        raise SchemaError("draft required")
    gid = hashlib.sha256(
        canonical_dumps({"d": d}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "gen_id": gid,
        "ok": True,
        "note": "selfrefine sr_generate",
    }


def sr_feedback(*, gen_id: str) -> dict[str, Any]:
    """Same-model self-feedback on the draft."""
    gid = gen_id.strip()
    if not gid:
        raise SchemaError("gen_id required")
    fid = hashlib.sha256(
        canonical_dumps({"g": gid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "feedback_id": fid,
        "ok": True,
        "note": "selfrefine sr_feedback",
    }


def sr_refine(*, gen_id: str, feedback_id: str) -> dict[str, Any]:
    """Refine previous output using self-feedback."""
    gid = gen_id.strip()
    fid = feedback_id.strip()
    if not gid or not fid:
        raise SchemaError("gen_id and feedback_id required")
    rid = hashlib.sha256(
        canonical_dumps({"g": gid, "f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "refine_id": rid,
        "ok": True,
        "note": "selfrefine sr_refine",
    }


def sr_iterate(*, rounds: int) -> dict[str, Any]:
    """Bound iterative feedback/refine rounds."""
    if rounds < 1:
        raise SchemaError("rounds must be >= 1")
    return {
        "rounds": rounds,
        "ok": True,
        "note": "selfrefine sr_iterate",
    }


def sr_no_train(*, no_rl: bool) -> dict[str, Any]:
    """Flag: no supervised training / RL required (report-only)."""
    return {
        "no_rl": no_rl,
        "apply": False,
        "ok": True,
        "note": "selfrefine sr_no_train",
    }


def sr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Generate → feedback → refine → iterate."""
    order = ("generate", "feedback", "refine", "iterate")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "generate"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "selfrefine sr_loop_plan",
    }
