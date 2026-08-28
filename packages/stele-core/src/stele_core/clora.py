"""C-LoRA proxies (stdlib; no LLM).

Shaped by C-LoRA (arXiv:2502.17920): one shared adapter plus a
learnable route, with orthogonality to cut forgetting. Proxies only.

Prefix ``clo_*`` — not LoRA (``lra_*``) / LoRTA (``lrt_*``) /
ConcurrentLoRA (``cnl_*``).
"""

from __future__ import annotations

import hashlib
from typing import Any

from stele_core.schema import SchemaError, canonical_dumps


def clo_route(*, task: str) -> dict[str, Any]:
    """Open the shared continual route."""
    t = task.strip()
    if not t:
        raise SchemaError("task required")
    rid = hashlib.sha256(
        canonical_dumps({"t": t}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "route_id": rid,
        "ok": True,
        "note": "clo clo_route",
    }


def clo_task(*, route_id: str) -> dict[str, Any]:
    """Bind a sequential task onto the route."""
    rid = route_id.strip()
    if not rid:
        raise SchemaError("route_id required")
    tid = hashlib.sha256(
        canonical_dumps({"r": rid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "task_id": tid,
        "ok": True,
        "note": "clo clo_task",
    }


def clo_ortho(*, task_id: str) -> dict[str, Any]:
    """Apply orthogonality vs prior tasks."""
    tid = task_id.strip()
    if not tid:
        raise SchemaError("task_id required")
    oid = hashlib.sha256(
        canonical_dumps({"t": tid}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "ortho_id": oid,
        "ok": True,
        "note": "clo clo_ortho",
    }


def clo_score(*, ortho_id: str, score: int) -> dict[str, Any]:
    """Score C-LoRA run (0–100)."""
    oid = ortho_id.strip()
    if not oid:
        raise SchemaError("ortho_id required")
    if score < 0 or score > 100:
        raise SchemaError("score must be 0..100")
    sid = hashlib.sha256(
        canonical_dumps({"o": oid, "s": score}).encode("utf-8")
    ).hexdigest()[:12]
    return {
        "score_id": sid,
        "score": score,
        "ok": True,
        "note": "clo clo_score",
    }


def clo_forget(*, less_forget: bool) -> dict[str, Any]:
    """Flag less forgetting vs per-task LoRA (report-only)."""
    return {
        "less_forget": less_forget,
        "apply": False,
        "ok": True,
        "note": "clo clo_forget",
    }


def clo_loop_plan(*, phase: str) -> dict[str, Any]:
    """Route → task → ortho → score."""
    order = ("route", "task", "ortho", "score")
    if phase not in order:
        raise SchemaError(f"phase must be one of {list(order)}")
    idx = order.index(phase)
    nxt = order[idx + 1] if idx + 1 < len(order) else "route"
    return {
        "phase": phase,
        "next": nxt,
        "apply": False,
        "ok": True,
        "note": "clo clo_loop_plan",
    }
