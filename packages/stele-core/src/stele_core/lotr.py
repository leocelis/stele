"""LoTR proxies (stdlib; no LLM).

Shaped by LoTR (arXiv:2402.01376): share left/right LoRA factors
across layers; only a small core tensor is per-block. Proxies only.

Prefix ``ltr_*`` — not LoRTA (``lrt_*``) / FacT (``fct_*``) /
TensLoRA (``tnl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def ltr_stack(*, task: str, layers: int) -> dict[str, Any]:
    """Stack Q/V updates across layers (layers >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if layers < 1:
        raise SchemaError("layers must be >= 1")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "l": layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "stack_id": sid,
        "layers": layers,
        "ok": True,
        "note": "ltr ltr_stack",
    }


def ltr_core(*, stack_id: str) -> dict[str, Any]:
    """Allocate the shared core tensor."""
    sid = stack_id.strip()
    if not sid:
        raise SchemaError("stack_id required")
    cid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "core_id": cid,
        "ok": True,
        "note": "ltr ltr_core",
    }


def ltr_share(*, core_id: str) -> dict[str, Any]:
    """Share left/right factors across depth."""
    cid = core_id.strip()
    if not cid:
        raise SchemaError("core_id required")
    hid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "share_id": hid,
        "ok": True,
        "note": "ltr ltr_share",
    }


def ltr_score(*, share_id: str, score: int) -> dict[str, Any]:
    """Score LoTR run (0–100)."""
    hid = share_id.strip()
    if not hid:
        raise SchemaError("share_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"h": hid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "ltr ltr_score",
    }


def ltr_deep(*, better_for_deep: bool) -> dict[str, Any]:
    """Flag better param scaling on deep stacks (report-only)."""
    return {
        "better_for_deep": better_for_deep,
        "apply": False,
        "ok": True,
        "note": "ltr ltr_deep",
    }


def ltr_loop_plan(*, phase: str) -> dict[str, Any]:
    """Stack → core → share → score."""
    order = ("stack", "core", "share", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "stack"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "ltr ltr_loop_plan",
    }
