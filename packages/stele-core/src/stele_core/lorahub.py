"""LoraHub proxies (stdlib; no LLM).

Shaped by LoraHub (arXiv:2307.13269 · COLM 2024): gradient-free
compose + adapt of multiple task LoRAs for few-shot cross-task
generalization without extra params. Proxies only.

Prefix ``lhb_*`` — not LoRA-LEGO (``llg_*``) / HydraLoRA (``hyd_*``) /
MultiLoRA (``mlr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lhb_pool(*, task: str, modules: int) -> dict[str, Any]:
    """Collect candidate LoRA modules (modules >= 2)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if modules < 2:
        raise SchemaError("modules must be >= 2")
    pid = hashlib.sha256(
        canonical_dumps({"t": t, "m": modules}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "pool_id": pid,
        "modules": modules,
        "ok": True,
        "note": "lhb lhb_pool",
    }


def lhb_compose(*, pool_id: str) -> dict[str, Any]:
    """Linearly compose LoRAs with coefficient vector w."""
    pid = pool_id.strip()
    if not pid:
        raise SchemaError("pool_id required")
    cid = hashlib.sha256(
        canonical_dumps({"p": pid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compose_id": cid,
        "ok": True,
        "note": "lhb lhb_compose",
    }


def lhb_adapt(*, compose_id: str, shots: int) -> dict[str, Any]:
    """Gradient-free adapt of w on few-shot examples (shots >= 1)."""
    cid = compose_id.strip()
    if not cid:
        raise SchemaError("compose_id required")
    if shots < 1:
        raise SchemaError("shots must be >= 1")
    aid = hashlib.sha256(
        canonical_dumps({"c": cid, "s": shots}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapt_id": aid,
        "shots": shots,
        "ok": True,
        "note": "lhb lhb_adapt",
    }


def lhb_score(*, adapt_id: str, score: int) -> dict[str, Any]:
    """Score LoraHub composition (0–100)."""
    aid = adapt_id.strip()
    if not aid:
        raise SchemaError("adapt_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"a": aid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "lhb lhb_score",
    }


def lhb_nograd(*, gradient_free: bool) -> dict[str, Any]:
    """Flag gradient-free composition (report-only)."""
    return {
        "gradient_free": gradient_free,
        "apply": False,
        "ok": True,
        "note": "lhb lhb_nograd",
    }


def lhb_loop_plan(*, phase: str) -> dict[str, Any]:
    """Pool → compose → adapt → score."""
    order = ("pool", "compose", "adapt", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "pool"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lhb lhb_loop_plan",
    }
