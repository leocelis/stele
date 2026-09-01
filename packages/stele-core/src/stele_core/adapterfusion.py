"""AdapterFusion proxies (stdlib; no LLM).

Shaped by AdapterFusion (arXiv:2005.00247): extract task adapters, then
compose via attention without destroying prior adapters. Proxies only.

Prefix ``adf_*`` — not LoRA (``lora_*``) / ATTEMPT (``atm_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def adf_extract(*, task: str) -> dict[str, Any]:
    """Extract / train a task-specific adapter (knowledge extraction stage)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    eid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapter_id": eid,
        "ok": True,
        "note": "adf adf_extract",
    }


def adf_compose(*, adapter_id: str) -> dict[str, Any]:
    """Compose multiple frozen adapters via AdapterFusion attention."""
    aid = adapter_id.strip()
    if not aid:
        raise SchemaError("adapter_id required")
    cid = hashlib.sha256(
        canonical_dumps({"a": aid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "compose_id": cid,
        "ok": True,
        "note": "adf adf_compose",
    }


def adf_attend(*, compose_id: str) -> dict[str, Any]:
    """Learn fusion Ψ attention weights over adapter outputs."""
    cid = compose_id.strip()
    if not cid:
        raise SchemaError("compose_id required")
    fid = hashlib.sha256(
        canonical_dumps({"c": cid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "fusion_id": fid,
        "ok": True,
        "note": "adf adf_attend",
    }


def adf_score(*, fusion_id: str, score: int) -> dict[str, Any]:
    """Score fused composition on the target task (0–100)."""
    fid = fusion_id.strip()
    if not fid:
        raise SchemaError("fusion_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"f": fid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "adf adf_score",
    }


def adf_nondestruct(*, nondestructive: bool) -> dict[str, Any]:
    """Flag non-destructive composition (no catastrophic forgetting)."""
    return {
        "nondestructive": nondestructive,
        "apply": False,
        "ok": True,
        "note": "adf adf_nondestruct",
    }


def adf_loop_plan(*, phase: str) -> dict[str, Any]:
    """Extract → compose → attend → score."""
    order = ("extract", "compose", "attend", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "extract"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "adf adf_loop_plan",
    }
