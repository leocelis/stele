"""LISA proxies (stdlib; no LLM).

Shaped by LISA (arXiv:2403.17919): layerwise importance sampling
unfreezes a sampled subset of layers each step so optimizer state
stays small vs full LoRA. Proxies only.

Prefix ``lis_*`` — not LoRA-FA (``lfa_*``) / LoftQ (``lfq_*``) /
LongLoRA (``llr_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lis_layers(*, task: str, n: int) -> dict[str, Any]:
    """Declare n transformer layers (n >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if n < 1:
        raise SchemaError("n must be >= 1")
    lid = hashlib.sha256(
        canonical_dumps({"t": t, "n": n}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "layers_id": lid,
        "n": n,
        "ok": True,
        "note": "lis lis_layers",
    }


def lis_sample(*, layers_id: str) -> dict[str, Any]:
    """Importance-sample which layers to unfreeze this step."""
    lid = layers_id.strip()
    if not lid:
        raise SchemaError("layers_id required")
    sid = hashlib.sha256(
        canonical_dumps({"l": lid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "sample_id": sid,
        "ok": True,
        "note": "lis lis_sample",
    }


def lis_unfreeze(*, sample_id: str) -> dict[str, Any]:
    """Unfreeze the sampled layer subset."""
    sid = sample_id.strip()
    if not sid:
        raise SchemaError("sample_id required")
    uid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "unfreeze_id": uid,
        "ok": True,
        "note": "lis lis_unfreeze",
    }


def lis_score(*, unfreeze_id: str, score: int) -> dict[str, Any]:
    """Score LISA run (0–100)."""
    uid = unfreeze_id.strip()
    if not uid:
        raise SchemaError("unfreeze_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    oid = hashlib.sha256(
        canonical_dumps({"u": uid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": oid,
        "score": score,
        "ok": True,
        "note": "lis lis_score",
    }


def lis_memory(*, less_opt: bool) -> dict[str, Any]:
    """Flag smaller optimizer state vs full LoRA (report-only)."""
    return {
        "less_opt": less_opt,
        "apply": False,
        "ok": True,
        "note": "lis lis_memory",
    }


def lis_loop_plan(*, phase: str) -> dict[str, Any]:
    """Layers → sample → unfreeze → score."""
    order = ("layers", "sample", "unfreeze", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "layers"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lis lis_loop_plan",
    }
