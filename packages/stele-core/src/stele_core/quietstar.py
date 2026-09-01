"""Quiet-STaR-shaped think-before-speak proxies (stdlib; no LLM / no train).

Shaped by Quiet-STaR (arXiv:2403.09629): thought delimiters, parallel
sample, mix head, hard-token aid. Proxies only — not Zelikman training.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def qs_thought_bounds(*, start: str, end: str) -> dict[str, Any]:
    """Record learnable thought start/end delimiters."""
    s = start.strip()
    e = end.strip()
    if not s or not e:
        raise SchemaError("start and end required")
    tid = hashlib.sha256(
        canonical_dumps({"s": s, "e": e}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "bounds_id": tid,
        "ok": True,
        "note": "quietstar qs_thought_bounds",
    }


def qs_parallel_sample(*, positions: int, thoughts: int) -> dict[str, Any]:
    """Tokenwise parallel thought sampling budget."""
    if positions < 1 or thoughts < 1:
        raise SchemaError("positions and thoughts must be >= 1")
    return {
        "positions": positions,
        "thoughts": thoughts,
        "ok": True,
        "note": "quietstar qs_parallel_sample",
    }


def qs_mix_head(*, weight: float) -> dict[str, Any]:
    """Mixing weight between base and thought logits (0..1)."""
    if weight < 0.0 or weight > 1.0:
        raise SchemaError("weight must be in [0, 1]")
    return {
        "weight": weight,
        "ok": True,
        "note": "quietstar qs_mix_head",
    }


def qs_hard_token_aid(*, hard_tokens: int, helped: int) -> dict[str, Any]:
    """Count hard tokens helped by internal thoughts."""
    if hard_tokens < 0 or helped < 0:
        raise SchemaError("hard_tokens and helped must be >= 0")
    if helped > hard_tokens:
        raise SchemaError("helped must be <= hard_tokens")
    return {
        "hard_tokens": hard_tokens,
        "helped": helped,
        "ok": True,
        "note": "quietstar qs_hard_token_aid",
    }


def qs_zero_shot_flag(*, improved: bool) -> dict[str, Any]:
    """Flag zero-shot transfer without task fine-tune (report-only)."""
    return {
        "improved": improved,
        "apply": False,
        "ok": True,
        "note": "quietstar qs_zero_shot_flag",
    }


def qs_loop_plan(*, phase: str) -> dict[str, Any]:
    """Bounds → sample → mix → aid."""
    order = ("bounds", "sample", "mix", "aid")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "bounds"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "quietstar qs_loop_plan",
    }
