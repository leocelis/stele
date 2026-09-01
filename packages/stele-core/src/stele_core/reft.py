"""ReFT proxies (stdlib; no LLM).

Shaped by ReFT (arXiv:2404.03592): intervene on hidden representations
rather than weights — LoReFT-style low-rank edits in activation space.
Proxies only.

Prefix ``rft_*`` — not REFLECT contested resolve / Houlsby (``had_*``) / LoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def rft_repr(*, task: str, layers: int) -> dict[str, Any]:
    """Select representation layers to edit (layers >= 1)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if layers < 1:
        raise SchemaError("layers must be >= 1")
    rid = hashlib.sha256(
        canonical_dumps({"t": t, "l": layers}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "repr_id": rid,
        "layers": layers,
        "ok": True,
        "note": "rft rft_repr",
    }


def rft_edit(*, repr_id: str) -> dict[str, Any]:
    """Apply low-rank representation edit (LoReFT-style)."""
    rid = repr_id.strip()
    if not rid:
        raise SchemaError("repr_id required")
    eid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "edit_id": eid,
        "ok": True,
        "note": "rft rft_edit",
    }


def rft_train(*, edit_id: str) -> dict[str, Any]:
    """Train representation interventions."""
    eid = edit_id.strip()
    if not eid:
        raise SchemaError("edit_id required")
    tid = hashlib.sha256(
        canonical_dumps({"e": eid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "rft rft_train",
    }


def rft_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score ReFT adaptation (0–100)."""
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
        "note": "rft rft_score",
    }


def rft_weightless(*, no_weight_update: bool) -> dict[str, Any]:
    """Flag representation-only edits (no weight ΔW) (report-only)."""
    return {
        "no_weight_update": no_weight_update,
        "apply": False,
        "ok": True,
        "note": "rft rft_weightless",
    }


def rft_loop_plan(*, phase: str) -> dict[str, Any]:
    """Repr → edit → train → score."""
    order = ("repr", "edit", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "repr"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "rft rft_loop_plan",
    }
