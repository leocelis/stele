"""Houlsby adapter proxies (stdlib; no LLM).

Shaped by Houlsby et al. (arXiv:1902.00751): insert bottleneck adapter
modules after attention/FFN (series adapters) while freezing the base —
compact multi-task transfer. Proxies only.

Prefix ``had_*`` — not LoHa Hadamard (``lha_*``) / AdapterDrop (``adp_*``) / ReFT.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def had_insert(*, task: str, bottleneck: int) -> dict[str, Any]:
    """Insert bottleneck adapters (bottleneck >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if bottleneck < 1:
        raise SchemaError("bottleneck must be >= 1")
    iid = hashlib.sha256(
        canonical_dumps({"t": t, "b": bottleneck}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "insert_id": iid,
        "bottleneck": bottleneck,
        "ok": True,
        "note": "had had_insert",
    }


def had_freeze(*, insert_id: str) -> dict[str, Any]:
    """Freeze base weights; train adapters only."""
    iid = insert_id.strip()
    if not iid:
        raise SchemaError("insert_id required")
    fid = hashlib.sha256(
        canonical_dumps({"i": iid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "freeze_id": fid,
        "ok": True,
        "note": "had had_freeze",
    }


def had_train(*, freeze_id: str) -> dict[str, Any]:
    """Train adapter parameters for the task."""
    fid = freeze_id.strip()
    if not fid:
        raise SchemaError("freeze_id required")
    tid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "had had_train",
    }


def had_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score Houlsby adapter adaptation (0–100)."""
    tid = train_id.strip()
    if not tid:
        raise SchemaError("train_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"t": tid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "had had_score",
    }


def had_latency(*, adds_latency: bool) -> dict[str, Any]:
    """Flag that series adapters add inference latency (report-only)."""
    return {
        "adds_latency": adds_latency,
        "apply": False,
        "ok": True,
        "note": "had had_latency",
    }


def had_loop_plan(*, phase: str) -> dict[str, Any]:
    """Insert → freeze → train → score."""
    order = ("insert", "freeze", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "insert"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "had had_loop_plan",
    }
