"""GLoRA proxies (stdlib; no LLM).

Shaped by GLoRA (arXiv:2306.07967): generalized LoRA prompt that
rescales weights and activations, plus layer-wise adapter search.
Zero extra infer cost via reparam. Proxies only.

Prefix ``glo_*`` — not GaLore (``gal_*``) / FLoRA (``flo_*``) /
PeriodicLoRA (``plr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def glo_prompt(*, task: str) -> dict[str, Any]:
    """Allocate the generalized prompt module."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    pid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "prompt_id": pid,
        "ok": True,
        "note": "glo glo_prompt",
    }


def glo_scale(*, prompt_id: str) -> dict[str, Any]:
    """Scale weights and activations."""
    pid = prompt_id.strip()
    if not pid:
        raise SchemaError("prompt_id required")
    sid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "scale_id": sid,
        "ok": True,
        "note": "glo glo_scale",
    }


def glo_search(*, scale_id: str) -> dict[str, Any]:
    """Layer-wise adapter search."""
    sid = scale_id.strip()
    if not sid:
        raise SchemaError("scale_id required")
    xid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "search_id": xid,
        "ok": True,
        "note": "glo glo_search",
    }


def glo_score(*, search_id: str, score: int) -> dict[str, Any]:
    """Score GLoRA run (0–100)."""
    xid = search_id.strip()
    if not xid:
        raise SchemaError("search_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"x": xid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "glo glo_score",
    }


def glo_zero(*, zero_infer: bool) -> dict[str, Any]:
    """Flag zero extra inference cost (report-only)."""
    return {
        "zero_infer": zero_infer,
        "apply": False,
        "ok": True,
        "note": "glo glo_zero",
    }


def glo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Prompt → scale → search → score."""
    order = ("prompt", "scale", "search", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "prompt"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "glo glo_loop_plan",
    }
