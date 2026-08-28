"""AdapterDrop proxies (stdlib; no LLM).

Shaped by AdapterDrop (arXiv:2010.11918): drop adapters from lower
transformer layers for training/inference efficiency; prune AdapterFusion
lower adapters. Proxies only.

Prefix ``adp_*`` — not VeRA (``vra_*``) / AdapterFusion (``adf_*``) / AdaLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def adp_insert(*, task: str) -> dict[str, Any]:
    """Insert full-depth task adapters (pre-drop baseline)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    iid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "adapter_id": iid,
        "ok": True,
        "note": "adp adp_insert",
    }


def adp_drop(*, adapter_id: str, lower_layers: int) -> dict[str, Any]:
    """Drop adapters from the lowest N layers (lower_layers >= 0)."""
    aid = adapter_id.strip()
    if not aid:
        raise SchemaError("adapter_id required")
    if lower_layers < 0:
        raise SchemaError("lower_layers must be >= 0")
    did = hashlib.sha256(
        canonical_dumps({"a": aid, "n": lower_layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "drop_id": did,
        "lower_layers": lower_layers,
        "ok": True,
        "note": "adp adp_drop",
    }


def adp_infer(*, drop_id: str) -> dict[str, Any]:
    """Run multi-task inference with dropped lower adapters."""
    did = drop_id.strip()
    if not did:
        raise SchemaError("drop_id required")
    iid = hashlib.sha256(
        canonical_dumps({"d": did}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "infer_id": iid,
        "ok": True,
        "note": "adp adp_infer",
    }


def adp_score(*, infer_id: str, score: int) -> dict[str, Any]:
    """Score AdapterDrop efficiency/quality trade-off (0–100)."""
    iid = infer_id.strip()
    if not iid:
        raise SchemaError("infer_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"i": iid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "adp adp_score",
    }


def adp_efficient(*, multi_task: bool) -> dict[str, Any]:
    """Flag multi-task inference overhead reduction (report-only)."""
    return {
        "multi_task": multi_task,
        "apply": False,
        "ok": True,
        "note": "adp adp_efficient",
    }


def adp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Insert → drop → infer → score."""
    order = ("insert", "drop", "infer", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "insert"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "adp adp_loop_plan",
    }
