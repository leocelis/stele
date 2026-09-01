"""LoRA-SP proxies (stdlib; no LLM).

Shaped by LoRA-SP (arXiv:2403.08822): randomized half-selective freezing
inside A/B — update ~half the adapter params to cut memory. Proxies only.

Prefix ``lsp_*`` — not SPoT (``spot_*``) / OLoRA (``olr_*``) / DropLoRA.
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def lsp_select(*, task: str, fraction: int) -> dict[str, Any]:
    """Declare partial selection mask (fraction 1..99 percent)."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    if fraction < 1 or fraction > 99:
        raise SchemaError("fraction must be 1..99")
    sid = hashlib.sha256(
        canonical_dumps({"t": t, "f": fraction}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "select_id": sid,
        "fraction": fraction,
        "ok": True,
        "note": "lsp lsp_select",
    }


def lsp_freeze(*, select_id: str) -> dict[str, Any]:
    """Freeze non-selected adapter parameters."""
    sid = select_id.strip()
    if not sid:
        raise SchemaError("select_id required")
    fid = hashlib.sha256(
        canonical_dumps({"s": sid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "freeze_id": fid,
        "ok": True,
        "note": "lsp lsp_freeze",
    }


def lsp_train(*, freeze_id: str) -> dict[str, Any]:
    """Train only selected adapter parameters."""
    fid = freeze_id.strip()
    if not fid:
        raise SchemaError("freeze_id required")
    tid = hashlib.sha256(
        canonical_dumps({"f": fid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "train_id": tid,
        "ok": True,
        "note": "lsp lsp_train",
    }


def lsp_score(*, train_id: str, score: int) -> dict[str, Any]:
    """Score LoRA-SP adaptation (0–100)."""
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
        "note": "lsp lsp_score",
    }


def lsp_memory(*, lower_memory: bool) -> dict[str, Any]:
    """Flag lower memory vs full LoRA (report-only)."""
    return {
        "lower_memory": lower_memory,
        "apply": False,
        "ok": True,
        "note": "lsp lsp_memory",
    }


def lsp_loop_plan(*, phase: str) -> dict[str, Any]:
    """Select → freeze → train → score."""
    order = ("select", "freeze", "train", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "select"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "lsp lsp_loop_plan",
    }
